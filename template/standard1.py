import os 
import numpy 

from .utils import del_gaps
from .task import *

import sys
sys.path.insert(0, "/home/jhuerta/_Devel/ete/2.2/")
from ete_dev import PhyloTree, SeqGroup

LARGE_ALG_LENGTH = 200
MAX_AA_COLUMN_CONSERVATION = 0.9
MAX_SEQS_TO_USE_NT = 20
CLEAN_ALG = True

def pipeline(task, main_tree, config):
    # new tasks is a list of Task instances that are returned to the
    # scheduler.

    aa_seed_file = config["general"]["aa_seed"]
    nt_seed_file = config["general"]["nt_seed"]

    new_tasks = []
    if not task:
        if aa_seed_file:
            new_tasks.append(Msf(None, aa_seed_file, "aa"))
        elif nt_seed_file:
            new_tasks.append(Msf(None, nt_seed_file, "nt"))
        else:
            raise Exception("I need at least one seed file")

    elif task.ttype == "msf":
        if task.nseqs < LARGE_ALG_LENGTH:
            #new_tasks.append(Muscle(task.cladeid, task.multiseq_file, 
            #                        task.seqtype, config["muscle"]))
            new_tasks.append(Mafft(task.cladeid, task.multiseq_file, 
                                   task.seqtype, config["mafft"]))


        else:
            new_tasks.append(Clustalo(task.cladeid, 
                                                 task.multiseq_file, 
                                                 config["clustalo"]))

    elif task.ttype == "alg":
        if CLEAN_ALG:
            new_tasks.append(\
                Trimal(task.cladeid, task.alg_fasta_file, task.seqtype, 
                       config["trimal"]))
        else:
            if task.seqtype == "aa":
                new_tasks.append(BionjModelChooser(task.cladeid, 
                                                   task.alg_phylip_file, 
                                                   config["bionj_modelchooser"]))
            elif task.seqtype == "nt":
                new_tasks.append(JModeltest(task.cladeid, 
                                            task.alg_fasta_file, 
                                            config["jmodeltest"]))
                               
    elif task.ttype == "acleaner":
        if task.seqtype == "aa":
            new_tasks.append(BionjModelChooser(task.cladeid,
                                               task.clean_alg_phylip_file, 

                                               config["bionj_modelchooser"]))
        elif task.seqtype == "nt":
            new_tasks.append(JModeltest(task.cladeid, 
                                        task.alg_file, 
                                        config["jmodeltest"]))
            
    elif task.ttype == "mchooser":
        if task.seqtype == "aa":
            #new_tasks.append(Raxml(task.cladeid, task.alg_phylip_file, 
            #                       task.best_model, "aa", 
            #                       config["raxml"]))
            new_tasks.append(Phyml(task.cladeid, task.alg_phylip_file, 
                                       task.best_model, "aa", 
                                       config["phyml"]))

        else:
            raise Exception("Not implemented yet!!")

    elif task.ttype == "tree":
        t = PhyloTree(task.tree_file)
        merge = TreeMerger(task.cladeid, t, main_tree, config["treemerger"])
        main_tree = merge.main_tree
                       
        for part in [merge.set_a, merge.set_b]:
            part_cladeid, seqs, outgroups = part

            # Partition size limit
            if len(seqs) < int(config["treemerger"]["_min_seqs_for_optimization"]) or \
                    len(outgroups) < int(config["treemerger"]["_min_outgroups_for_optimization"]):
                print len(seqs)
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
                Msf(part_cladeid, new_msf_file, seqtype))
            
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
         
