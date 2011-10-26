import os 
import numpy 
import logging
log = logging.getLogger("main")
from .utils import del_gaps, GENCODE
from .task import *

import sys
sys.path.insert(0, "/home/jhuerta/_Devel/ete/2.2/")
from ete_dev import PhyloTree, SeqGroup

CLEAN_ALG = True
MODEL_TEST = True
GAP_CHARS = set(".-")
NUCLETIDES = set("ATCG") 

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
        if task.nseqs < config["general"]["large_alg_length"]:
            #new_tasks.append(Muscle(task.cladeid, task.multiseq_file, 
            #                        task.seqtype, config["muscle"]))
            new_tasks.append(Mafft(task.cladeid, task.multiseq_file, 
                                   task.seqtype, config["mafft"]))


        else:
            new_tasks.append(Clustalo(task.cladeid, 
                                                 task.multiseq_file, 
                                                 config["clustalo"]))

    elif CLEAN_ALG and task.ttype == "alg":
        new_tasks.append(\
            Trimal(task.cladeid, task.alg_fasta_file, task.alg_phylip_file, task.seqtype, 
                   config["trimal"]))
                               
    elif MODEL_TEST and (task.ttype == "alg" or task.ttype == "acleaner"):
        seqtype = task.seqtype
        cladeid = task.cladeid
        kept_columns = getattr(task, "kept_columns", None)
            
        cons_mean, cons_std = get_conservation(task.alg_fasta_file)
        log.info("Conservation%0.2f +-%0.2f", cons_mean, cons_std)
        # Converts aa alignment into nt if necessary
        if seqtype == "aa" and nt_seed_file and \
                cons_mean > config["general"]["DNA_sct"]:
            log.info("switching to codon alignment")
            alg_fasta_file, alg_phylip_file = switch_to_codon(\
                task.alg_fasta_file, task.alg_phylip_file, 
                nt_seed_file, kept_columns)
            seqtype = "nt"
        # Should I use clean or raw alignment 
        else:
            alg_fasta_file = getattr(task, "clean_alg_fasta_file", task.alg_fasta_file)
            alg_phylip_file = getattr(task, "clean_alg_phylip_file", task.alg_phylip_file)

        # Register model testing task
        if seqtype == "aa":
            new_tasks.append(BionjModelChooser(cladeid,
                                               alg_fasta_file, 
                                               alg_phylip_file, 
                                               config["bionj_modelchooser"]))
        elif seqtype == "nt":
            new_tasks.append(JModeltest(cladeid, 
                                        alg_fasta_file, 
                                        alg_phylip_file,
                                        config["jmodeltest"]))
            
    elif task.ttype in set(["mchooser", "alg", "acleaner"]):
        seqtype = task.seqtype
        alg_fasta_file = task.alg_fasta_file
        alg_phylip_file = task.alg_phylip_file
        cladeid = task.cladeid
        if task.ttype == "mchooser": 
            model = task.best_model
        else:
            model = None

        if task.seqtype == "aa":
            new_tasks.append(Raxml(cladeid,
                                   alg_phylip_file,
                                   model, "aa",
                                   config["raxml"]))

            #new_tasks.append(Phyml(cladeid, alg_phylip_file, 
            #                           model, "aa", 
            #                           config["phyml"]))

        else:
            new_tasks.append(Raxml(cladeid,
                                   alg_phylip_file,
                                   moel, "nt",
                                   config["raxml"]))

    elif task.ttype == "tree":
        t = PhyloTree(task.tree_file)
        merge = TreeMerger(task.cladeid, t, main_tree, config["treemerger"])
        main_tree = merge.main_tree
                       
        for part in [merge.set_a, merge.set_b]:
            part_cladeid, seqs, outgroups = part

            # Partition size limit
            if len(seqs) >= int(config["treemerger"]["_min_seqs_for_optimization"]) and \
                    len(outgroups) >= int(config["treemerger"]["_min_outgroups_for_optimization"]):

                # Creates msf file for the new partitions. IF
                # possible, it always uses aa, even when previous tree
                # was done with a codon alignment.
                if aa_seed_file: 
                    alg = SeqGroup(aa_seed_file)
                    seqtype = "aa"
                else:
                    alg = SeqGroup(nt_seed_file)
                    seqtype = "nt"

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
    return mean, std
         
def switch_to_codon(alg_fasta_file, alg_phylip_file, nt_seed_file, kept_columns=[]):
    # Check conservation of columns. If too many identities,
    # switch to codon alignment and make the tree with DNA. 
    # Mixed models is another possibility.
    kept_columns = set(map(int, kept_columns))
    all_nt_alg = SeqGroup(nt_seed_file)
    aa_alg = SeqGroup(alg_fasta_file)
    nt_alg = SeqGroup()

    for seqname, aaseq, comments in aa_alg.iter_entries():
        ntseq = all_nt_alg.get_seq(seqname).upper()
        ntalgseq = []
        nt_pos = 0
        for pos, ch in enumerate(aaseq):
            if ch in GAP_CHARS:
                codon = "---"
            else:
                codon = ntseq[nt_pos:nt_pos+3]
                nt_pos += 3

            if not kept_columns or pos in kept_columns: 
                ntalgseq.append(codon)
                # If codon does not contain wildcard, check that
                # translation is correct
                if not (set(codon) - NUCLETIDES) and GENCODE[codon] != ch:
                    log.error("[%s] CDS does not match protein sequence: %s = %s not %s at pos %d" \
                                         %(seqname, codon, GENCODE[codon], ch, nt_pos))
                    raise ValueError()

        ntalgseq = "".join(ntalgseq)
        nt_alg.set_seq(seqname, ntalgseq)

    alg_fasta_filename = alg_fasta_file + ".nt"
    alg_phylip_filename = alg_phylip_file + ".nt"
    nt_alg.write(outfile=alg_fasta_filename, format="fasta")
    nt_alg.write(outfile=alg_phylip_filename, format="iphylip_relaxed")
        
    return alg_fasta_filename, alg_phylip_filename
