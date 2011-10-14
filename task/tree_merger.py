import os
import numpy
import logging
log = logging.getLogger("main")

from .master_task import Task
from .master_job import Job
from .utils import get_cladeid

import sys
sys.path.insert(0, "/home/jhuerta/_Devel/ete/2.2/")
from ete_dev import PhyloTree

__all__ = ["TreeMerger"]

class TreeMerger(Task):
    def __init__(self, cladeid, task_tree, main_tree,
                 rooting_dict=None):
        # Initialize task
        Task.__init__(self, cladeid, "mergetree", "tree_merger")
        log.debug("Task Tree: %s", task_tree)
        log.debug("Main Tree: %s", main_tree)
        # Process current main tree and the new generated tree
        # (task_tree) to find out the outgroups used in task_tree. The
        # trick lies on the fact that cladeid is always calculated
        # ignoring the IDs of outgroups seqs.
        if main_tree:
            target_node = main_tree.search_nodes(cladeid=cladeid)[0]
            core_seqs = set(target_node.get_leaf_names())
            outgroup_seqs = set(task_tree.get_leaf_names()) - core_seqs
        else:
            outgroup_seqs = None

        t = task_tree
        # Root task_tree. If outgroup_seqs are available, uses manual
        # rooting. Otherwise, it means that task_tree is the result of
        # the first iteration, so it will try automatic rooting based
        # on dictionary or midpoint.
        if outgroup_seqs:
            log.info("Rooting new tree using %d custom seqs" %
                     len(outgroup_seqs))
            if len(outgroup_seqs) > 1:
                outgroup = t.get_common_ancestor(outgroup_seqs)
            else:
                outgroup = t & list(outgroup_seqs)[0]

            # If outcrop_seqs are split by current root node, outgroup
            # cannot be found. Let's find it from a different
            # perspective using non-outgroup seqs.
            if outgroup is t:
                outgroup = t.get_common_ancestor(core_seqs)

            t.set_outgroup(outgroup)
            t = t.get_common_ancestor(core_seqs)
            # Let's forget about outgroups, we want only the
            # informative topology
            t.detach()

        elif rooting_dict:
            log.info("Rooting new tree using a rooting dictionary")
            t.set_outgroup(t.get_farthest_oldest_node(rooting_dict))
        else:
            log.info("Rooting new tree using midpoint outgroup")
            t.set_outgroup(t.get_midpoint_outgroup())

        log.debug("Pruned Task_Tree: %s", t)

        # Extract the two new partitions (potentially representing two
        # new iterations in the pipeline). Note that outgroup node was
        # detached previously.
        a = t.children[0]
        b = t.children[1]

        # Sequences grouped by each of the new partitions
        seqs_a = a.get_leaf_names()
        seqs_b = b.get_leaf_names()

        # To detect the best outgroups of each of the new partitions
        # (a and b), I calculate the branch length distances from them
        # (a and b) to all leaf nodes in its corresponding sister
        # node.
        to_b_dists = []
        to_a_dists = []
        for b_leaf in b.iter_leaves():
            dist = b_leaf.get_distance(a)
            to_a_dists.append([dist, b_leaf.name])
        for a_leaf in a.iter_leaves():
            dist = a_leaf.get_distance(b)
            to_b_dists.append([dist, a_leaf.name])

        # Then we can sort outgroups prioritizing sequences whose
        # distances are close to the mean (avoiding the closest and
        # farthest sequences).
        mean_to_b_dist = numpy.mean([d[0] for d in  to_b_dists])
        mean_to_a_dist = numpy.mean([d[0] for d in  to_a_dists])
        rank_outs_a = sorted(to_a_dists, lambda x,y: cmp(abs(x[0] - mean_to_a_dist),
                                                        abs(y[0] - mean_to_a_dist),
                                                        ))

        rank_outs_b = sorted(to_b_dists, lambda x,y: cmp(abs(x[0] - mean_to_b_dist),
                                                        abs(y[0] - mean_to_b_dist),
                                                        ))
        outs_a = [e[1] for e in rank_outs_a]
        outs_b = [e[1] for e in rank_outs_b]
        log.debug("Mean distance to node A: %s" %mean_to_a_dist)
        log.debug("Best outgroup for A: %s" %rank_outs_a[:2])
        log.debug("Mean distance to node B: %s" %mean_to_b_dist)
        log.debug("Best outgroup for B: %s" %rank_outs_b[:2])

        # Annotate current tree
        for n in t.traverse():
            n.add_features(cladeid=get_cladeid(n.get_leaf_names()))

        # Updates main tree with the results extracted from task_tree
        if main_tree is None:
            main_tree = t
        else:
            log.info("Merging trees")
            target = main_tree.search_nodes(cladeid=cladeid)[0]
            # Switch nodes in the main_tree so current tree topology
            # is incorporated.
            up = target.up
            target.detach()
            up.add_child(t)

        self.set_a = [a.cladeid, seqs_a, outs_a]
        self.set_b = [b.cladeid, seqs_b, outs_b]
        self.main_tree = main_tree
        log.debug("Final Merged Main_Tree: %s", main_tree)

