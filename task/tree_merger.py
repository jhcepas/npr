import os
import numpy
import logging
log = logging.getLogger("main")

from .master_task import Task
from .master_job import Job
from .utils import get_cladeid, load_node_size

import sys
sys.path.insert(0, "/home/jhuerta/_Devel/ete/2.2/")
from ete_dev import PhyloTree

__all__ = ["TreeMerger"]

class TreeMerger(Task):
    def __init__(self, cladeid, task_tree, main_tree, args):
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
                # Root to a non-outgroup leave to leave all outgroups
                # in one side.
                t.set_outgroup(list(core_seqs)[0])
                outgroup = t.get_common_ancestor(outgroup_seqs)
            else:
                outgroup = t & list(outgroup_seqs)[0]

            t.set_outgroup(outgroup)
            t = t.get_common_ancestor(core_seqs)
            # Let's forget about outgroups, we want only the
            # informative topology
            t.detach()

        else:
            log.info("Rooting new tree using midpoint outgroup")
            t.set_outgroup(t.get_midpoint_outgroup())
            load_node_size(t)
            supports = []
            for n in t.get_descendants("levelorder"):
                if n.is_leaf():
                    continue
                st = n.get_sisters()
                if len(st) == 1:
                    min_size = min([st[0].size, n.size])
                    min_support = min([st[0].support, n.support])
                    supports.append([min_support, min_size, n])
                else:
                    log.warning("skipping multifurcation in basal tree")

            # Roots to the best supported and larger partitions
            supports.sort()
            supports.reverse()
            t.set_outgroup(supports[0][2])
            print supports

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
        if args["_outgroup_selection_policy"] == "mean_dist":
            dist_fn = numpy.mean
        elif args["_outgroup_selection_policy"] == "median_dist":
            dist_fn = numpy.median
        elif args["_outgroup_selection_policy"] == "max_dist":
            dist_fn = numpy.max
        elif args["_outgroup_selection_policy"] == "min_dist":
            dist_fn = numpy.min


        best_dist_to_b = dist_fn([d[0] for d in  to_b_dists])
        best_dist_to_a = dist_fn([d[0] for d in  to_a_dists])

        rank_outs_a = sorted(to_a_dists, lambda x,y: cmp(abs(x[0] - best_dist_to_a),
                                                        abs(y[0] - best_dist_to_a),
                                                        ))

        rank_outs_b = sorted(to_b_dists, lambda x,y: cmp(abs(x[0] - best_dist_to_b),
                                                        abs(y[0] - best_dist_to_b),
                                                        ))
        outs_a = [e[1] for e in rank_outs_a]
        outs_b = [e[1] for e in rank_outs_b]

        log.debug("Best distance to node A: %s" %best_dist_to_a)
        log.debug("Best outgroup for A: %s" %rank_outs_a[:5])
        log.debug("Best distance to node B: %s" %best_dist_to_b)
        log.debug("Best outgroup for B: %s" %rank_outs_b[:5])

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

