import os 

from .utils import del_gaps
from .task import *

import sys
sys.path.insert(0, "/home/jhuerta/_Devel/ete/2.2/")
from ete_dev import PhyloTree, SeqGroup

MAX_SEQS_FOR_MUSCLE = 200
CLEAN_ALG = True

def pipeline(task, main_tree):
    new_tasks = []
    if task.ttype == "msf":
        if task.nseqs <= MAX_SEQS_FOR_MUSCLE:
            new_tasks.append(MuscleAlgTask(task.cladeid,
                                           task.multiseq_file))
        else:
            new_tasks.append(ClustalOmegaAlgTask(task.cladeid,
                                                 task.multiseq_file))

    elif task.ttype == "alg":
        if CLEAN_ALG:
            new_tasks.append(\
                TrimalTask(task.cladeid, task.alg_fasta_file))
        else:
            new_tasks.append(BionjModelChooserTask(task.cladeid, 
                                                   task.alg_phylip_file))
    elif task.ttype == "acleaner":
        new_tasks.append(BionjModelChooserTask(task.cladeid,
                                               task.clean_alg_phylip_file))

    elif task.ttype == "mchooser":
        new_tasks.append(RaxmlTreeTask(task.cladeid, 
                                       task.alg_file, task.best_model))

    elif task.ttype == "tree":
        t = PhyloTree(task.tree_file)
        merge = MergeTreeTask(task.cladeid, t, main_tree)
        main_tree = merge.main_tree
        alg = SeqGroup(task.alg_file, "iphylip_relaxed")
        for part in [merge.set_a, merge.set_b]:
            set_cladeid, seqs, outgroups = part
            if len(seqs)>4 and len(outgroups)>2:
                msf_seqs = seqs + outgroups[:3]
                new_msf_file = os.path.join(task.taskdir, "children_%s.msf" %set_cladeid)
                fasta = '\n'.join([">%s\n%s" %
                                   (n,del_gaps(alg.get_seq(n)))
                                   for n in msf_seqs])
                open(new_msf_file, "w").write(fasta)
                new_tasks.append(\
                    MsfTask(set_cladeid, new_msf_file))
    return new_tasks, main_tree
