import numpy
import logging
import os
log = logging.getLogger("main")

from .master_task import Task
from .master_job import Job
from .utils import get_cladeid, load_node_size, PhyloTree, SeqGroup

__all__ = ["TreeMerger"]

class TreeMerger(Task):
    def __init__(self, cladeid, seqtype, task_tree, main_tree, conf):
        # Initialize task
        Task.__init__(self, cladeid, "treemerger", "Standard-TreeMerger")
        self.conf = conf
        self.args = conf["tree_merger"]
        self.task_tree_file = task_tree
        self.main_tree = main_tree
        self.seqtype = seqtype
        self.set_a = None
        self.set_b = None
        self.init()
        self.left_part_file = os.path.join(self.taskdir, "left.msf")
        self.right_part_file = os.path.join(self.taskdir, "right.msf")

    def finish(self):
        ttree = PhyloTree(self.task_tree_file)
        mtree = self.main_tree

        #log.debug("Task Tree: %s", ttree)
        #log.debug("Main Tree: %s", mtree)

        # Process current main tree and the new generated tree
        # (task_tree) to find out the outgroups used in task_tree. The
        # trick lies on the fact that cladeid is always calculated
        # ignoring the IDs of outgroups seqs.
        if mtree:
            target_node = fast_search_node(self.cladeid, mtree)
            core_seqs = set(target_node.get_leaf_names())
            outgroup_seqs = set(ttree.get_leaf_names()) - core_seqs
        else:
            outgroup_seqs = None

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
                ttree.set_outgroup(list(core_seqs)[0])
                outgroup = ttree.get_common_ancestor(outgroup_seqs)
            else:
                outgroup = ttree & list(outgroup_seqs)[0]

            ttree.set_outgroup(outgroup)
            ttree = ttree.get_common_ancestor(core_seqs)
            # Let's forget about outgroups, we want only the
            # informative topology
            ttree.detach()

        else:
            log.info("Rooting new tree using midpoint outgroup")
            ttree.set_outgroup(ttree.get_midpoint_outgroup())
            # Pre load node size for better performance
            load_node_size(ttree)
            supports = []
            for n in ttree.get_descendants("levelorder"):
                if n.is_leaf():
                    continue
                st = n.get_sisters()
                if len(st) == 1:
                    min_size = min([st[0]._size, n._size])
                    min_support = min([st[0].support, n.support])
                    supports.append([min_support, min_size, n])
                else:
                    log.warning("skipping multifurcation in basal tree")

            # Roots to the best supported and larger partitions
            supports.sort()
            supports.reverse()
            ttree.set_outgroup(supports[0][2])
            log.info("Done")

        self.outgroup_topology = ttree.children[0].__str__()

        #log.debug("Pruned Task_Tree: %s", ttree)

        # Extract the two new partitions (potentially representing two
        # new iterations in the pipeline). Note that outgroup node was
        # detached previously.
        a = ttree.children[0]
        b = ttree.children[1]

        # Sequences grouped by each of the new partitions
        seqs_a = a.get_leaf_names()
        seqs_b = b.get_leaf_names()

        # To detect the best outgroups of each of the new partitions
        # (a and b), I calculate the branch length distances from them
        # (a and b) to all leaf nodes in its corresponding sister
        # node.
        log.info("Calculating node distance")
        to_b_dists = []
        to_a_dists = []
        n2rootdist = root_distance_matrix(ttree)
        for b_leaf in b.iter_leaves():
            dist = n2rootdist[b_leaf] + a.dist
            #dist1 = b_leaf.get_distance(a)
            #print dist, dist1
            to_a_dists.append([dist, b_leaf.name])
            
        for a_leaf in a.iter_leaves():
            dist = n2rootdist[a_leaf] + b.dist
            #dist1 = a_leaf.get_distance(b)
            #print dist, dist1
            to_b_dists.append([dist, a_leaf.name])

        # Then we can sort outgroups prioritizing sequences whose
        # distances are close to the mean (avoiding the closest and
        # farthest sequences).
        if self.args["_outgroup_policy"] == "mean_dist":
            dist_fn = numpy.mean
        elif self.args["_outgroup_policy"] == "median_dist":
            dist_fn = numpy.median
        elif self.args["_outgroup_policy"] == "max_dist":
            dist_fn = numpy.max
        elif self.args["_outgroup_policy"] == "min_dist":
            dist_fn = numpy.min

        best_dist_to_b = dist_fn([d[0] for d in  to_b_dists])
        best_dist_to_a = dist_fn([d[0] for d in  to_a_dists])

        rank_outs_a = sorted(to_a_dists, 
                             lambda x,y: cmp(abs(x[0] - best_dist_to_a),
                                             abs(y[0] - best_dist_to_a),
                                             ))

        rank_outs_b = sorted(to_b_dists, 
                             lambda x,y: cmp(abs(x[0] - best_dist_to_b),
                                             abs(y[0] - best_dist_to_b),
                                             ))
        outs_a = [e[1] for e in rank_outs_a]
        outs_b = [e[1] for e in rank_outs_b]

        log.debug("Best distance to node A: %s" %best_dist_to_a)
        log.debug("Best outgroup for A: %s" %rank_outs_a[:5])
        log.debug("Best distance to node B: %s" %best_dist_to_b)
        log.debug("Best outgroup for B: %s" %rank_outs_b[:5])

        # Annotate current tree
        log.info("Annotating new tree")
        for n in ttree.traverse():
            n.add_features(cladeid=get_cladeid(n.get_leaf_names()))

        # Updates main tree with the results extracted from task_tree
        if mtree is None:
            mtree = ttree
        else:
            log.info("Merging trees")
            target = fast_search_node(self.cladeid, mtree)
            # Switch nodes in the main_tree so current tree topology
            # is incorporated.
            up = target.up
            target.detach()
            up.add_child(ttree)

        self.set_a = [a.cladeid, seqs_a, outs_a, self.left_part_file]
        self.set_b = [b.cladeid, seqs_b, outs_b, self.right_part_file]
        self.main_tree = mtree
        #log.debug("Final Merged Main_Tree: %s", self.main_tree)

        # Dump partitions into disk
        log.info("Dumping new partitions")
        for part in [self.set_a, self.set_b]:
            part_cladeid, seqs, outgroups, fname = part

            # Creates msf file for the new partitions. If
            # possible, it always uses aa, even when previous tree
            # was done with a codon alignment.
            if self.conf["main"]["aa_seed"]:
                alg = SeqGroup(self.conf["main"]["aa_seed"])
                seqtype = "aa"
            else:
                alg = SeqGroup(self.conf["main"]["nt_seed"])
                seqtype = "nt"

            msf_seqs = seqs + outgroups[:3]
            fasta = '\n'.join([">%s\n%s" %
                               (n, alg.get_seq(n))
                               for n in msf_seqs])
            open(fname, "w").write(fasta)

        self.dump_inkey_file(self.task_tree_file)
        log.info("Done.")
        
    def check(self):
        if os.path.exists(self.left_part_file) and \
                os.path.exists(self.right_part_file) and \
                os.path.getsize(self.left_part_file) and \
                os.path.getsize(self.right_part_file):
            return True
        return False
            
def fast_search_node(cladeid, tree):
    for n in tree.traverse():
        if n.cladeid == cladeid:
            return n

def root_distance_matrix(root):
    root.dist = 0.0
    n2rdist = {root:0.0}
    for n in root.iter_descendants("preorder"):
        n2rdist[n] = n2rdist[n.up] + n.dist
    return n2rdist




