import os 
import numpy 

from .utils import del_gaps
from .task import *

import sys
sys.path.insert(0, "/home/jhuerta/_Devel/ete/2.2/")
from ete_dev import PhyloTree, SeqGroup

MAX_SEQS_FOR_MUSCLE = 200
MAX_AA_COLUMN_CONSERVATION = 0.9
MAX_SEQS_TO_USE_NT = 20
SEQS_lIMIT = 4
CLEAN_ALG = True

def pipeline(task, main_tree, aa_seed_file, nt_seed_file):
    # new tasks is a list of Task instances that are returned to the
    # scheduler.

    new_tasks = []
    if not task:
        if aa_seed_file:
            new_tasks.append(MsfTask(None, aa_seed_file, "aa"))
        elif nt_seed_file:
            new_tasks.append(MsfTask(None, nt_seed_file, "nt"))
        else:
            raise Exception("I need at least one seed file")

    elif task.ttype == "msf":
        if task.nseqs <= MAX_SEQS_FOR_MUSCLE:
            new_tasks.append(MuscleAlgTask(task.cladeid, task.multiseq_file, 
                                           task.seqtype))
        else:
            new_tasks.append(ClustalOmegaAlgTask(task.cladeid, 
                                                 task.multiseq_file))

    elif task.ttype == "alg":
        if CLEAN_ALG:
            new_tasks.append(\
                TrimalTask(task.cladeid, task.alg_fasta_file, task.seqtype))
        else:
            if task.seqtype == "aa":
                new_tasks.append(BionjModelChooserTask(task.cladeid, 
                                                       task.alg_phylip_file))
            elif task.seqtype == "nt":
                new_tasks.append(JModeltestTask(task.cladeid, 
                                                task.alg_fasta_file))
                               
    elif task.ttype == "acleaner":
        if task.seqtype == "aa":
            new_tasks.append(BionjModelChooserTask(task.cladeid,
                                                   task.clean_alg_phylip_file))
        elif task.seqtype == "nt":
            new_tasks.append(JModeltestTask(task.cladeid, 
                                            task.alg_file))
            
    elif task.ttype == "mchooser":
        if task.seqtype == "aa":
            new_tasks.append(RaxmlTreeTask(task.cladeid, task.alg_file, 
                                           task.best_model, "aa"))
        else:
            raise Exception("Not implemented yet!!")

    elif task.ttype == "tree":
        t = PhyloTree(task.tree_file)
        merge = MergeTreeTask(task.cladeid, t, main_tree)
        main_tree = merge.main_tree
                       
        for part in [merge.set_a, merge.set_b]:
            part_cladeid, seqs, outgroups = part

            # Partition size limit
            if len(seqs) < SEQS_lIMIT:
                continue
            
            # Shall I switch to DNA?
            if nt_seed_file and len(seqs) <= MAX_SEQS_TO_USE_NT: 
                alg = SeqGroup(nt_seed_file)
                seqtype = "nt"
            else:
                alg = SeqGroup(aa_seed_file)
                seqtype = "aa"

            msf_seqs = seqs + outgroups[:3]
            new_msf_file = os.path.join(task.taskdir, 
                                        "children_%s.msf" %part_cladeid)
            fasta = '\n'.join([">%s\n%s" %
                               (n,del_gaps(alg.get_seq(n)))
                               for n in msf_seqs])
            open(new_msf_file, "w").write(fasta)
            new_tasks.append(\
                MsfTask(part_cladeid, new_msf_file, seqtype))
            
    return new_tasks, main_tree

import commands
def get_conservation(alg_file):
    output = commands.getoutput("trimal -ssc -in %s" %alg_file)
    conservation = []
    for line in output.split("\n")[3:]:
        a, b = map(float, line.split())
        conservation.append(b)
    mean = numpy.mean(conservation)
    std =  numpy.std(conservation)
    print mean, "+-", std 
    return mean, std
         
