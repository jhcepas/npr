from os import path
import numpy 
import re
import commands
import logging
log = logging.getLogger("main")
from .utils import del_gaps, GENCODE, PhyloTree, SeqGroup, TreeStyle
from .task import *

def create_alg_task(cladeid, msf, seqtype, app_conf):
    pass

def create_msf_task(seed_file, seqtype):
    return Msf(None, seed_file, seqtype)

def create_tree_task(cladeid, msf, seqtype, app_conf):
    pass

def pipeline(task, main_tree, conf):
    # new tasks is a list of Task instances that are returned to the
    # scheduler.
    aa_seed_file = conf["main"]["aa_seed"]
    nt_seed_file = conf["main"]["nt_seed"]

    new_tasks = []
    if not task:
        if aa_seed_file:
            new_tasks.append(Msf(None, aa_seed_file, "aa"))
        elif nt_seed_file:
            new_tasks.append(Msf(None, nt_seed_file, "nt"))
        else:
            raise Exception("I need at least one seed file")

    elif task.ttype == "msf":
        if task.nseqs < conf["main"]["aligner_max_seqs"]:
            # new_tasks.append(Muscle(task.cladeid, task.multiseq_file, 
            #                        task.seqtype, conf["muscle"]))
            # new_tasks.append(Mafft(task.cladeid, task.multiseq_file, 
            #                        task.seqtype, conf))
            new_tasks.append(MetaAligner(task.cladeid, task.multiseq_file, 
                                         task.seqtype, conf))

        else:
            new_tasks.append(Clustalo(task.cladeid, task.multiseq_file, 
                                      "aa", conf))

    elif conf["main"]["clean_alg"] and task.ttype == "alg":
        new_tasks.append(\
            Trimal(task.cladeid, task.alg_fasta_file, task.alg_phylip_file,
                   task.seqtype, 
                   conf))
                               
    elif (task.ttype == "alg" or task.ttype == "acleaner"):
        seqtype = task.seqtype
        cladeid = task.cladeid
        kept_columns = getattr(task, "kept_columns", None)
           
        cons_mean, cons_std = get_conservation(task.alg_fasta_file, 
                                               conf["app"]["trimal"])
        max_identity = get_max_identity(task.alg_fasta_file, 
                                        conf["app"]["trimal"])

        log.info("Conservation: %0.2f +-%0.2f", cons_mean, cons_std)
        log.info("Max. Identity: %0.2f", max_identity)
        log.info("Seqs: %d", task.nseqs)

        sst = conf["main"]["DNA_sst"]
        sit = conf["main"]["DNA_sit"]
        sct = conf["main"]["DNA_sct"]

        # Converts aa alignment into nt if necessary
        if seqtype == "aa" and nt_seed_file and \
                task.nseqs <= sst and max_identity > sit and \
                cons_mean >= sct:

                log.info("switching to codon alignment")
                alg_fasta_file, alg_phylip_file = switch_to_codon(\
                    task.alg_fasta_file, task.alg_phylip_file, 
                    nt_seed_file, kept_columns)
                seqtype = "nt"
        # Should I use clean or raw alignment 
        else:
            alg_fasta_file = getattr(task, "clean_alg_fasta_file", 
                                     task.alg_fasta_file)
            alg_phylip_file = getattr(task, "clean_alg_phylip_file", 
                                      task.alg_phylip_file)

        # Register model testing task
        if seqtype == "aa":
            new_tasks.append(BionjModelChooser(cladeid,
                                               alg_fasta_file, 
                                               alg_phylip_file, 
                                               conf))
        elif seqtype == "nt":
            new_tasks.append(JModeltest(cladeid, 
                                        alg_fasta_file, 
                                        alg_phylip_file,
                                        conf))
            
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
                                   conf))
            
            #new_tasks.append(Phyml(cladeid, alg_phylip_file, 
            #                           model, "aa", 
            #                           conf))

        else:
            if model:
                new_tasks.append(Phyml(cladeid, alg_phylip_file, 
                                       model, "nt", 
                                       conf))
            else:
                new_tasks.append(Raxml(cladeid,
                                   alg_phylip_file,
                                   "GTR", "nt",
                                   conf))

    elif task.ttype == "tree":
        t = PhyloTree(task.tree_file)
        treemerge_task = TreeMerger(task.cladeid, t, main_tree, conf)
        new_tasks.append(treemerge_task)

    elif task.ttype == "treemerger":
        main_tree = task.main_tree
                      
        for part in [task.set_a, task.set_b]:
            part_cladeid, seqs, outgroups = part
            # Partition size limit
            if len(seqs) >= int(conf["tree_merger"]["_min_size"]) and \
                    len(outgroups) >= int(conf["tree_merger"]["_min_outgroups"]):

                # Creates msf file for the new partitions. If
                # possible, it always uses aa, even when previous tree
                # was done with a codon alignment.
                if aa_seed_file: 
                    alg = SeqGroup(aa_seed_file)
                    seqtype = "aa"
                else:
                    alg = SeqGroup(nt_seed_file)
                    seqtype = "nt"

                msf_seqs = seqs + outgroups[:3]
                new_msf_file = path.join(task.taskdir, 
                                            "children_%s.msf" %part_cladeid)
                fasta = '\n'.join([">%s\n%s" %
                                   (n,del_gaps(alg.get_seq(n)))
                                   for n in msf_seqs])
                open(new_msf_file, "w").write(fasta)
                new_tasks.append(\
                    Msf(part_cladeid, new_msf_file, seqtype))
           
    return new_tasks, main_tree


def get_conservation(alg_file, trimal_bin):
    output = commands.getoutput("%s -ssc -in %s" %\
                                    (trimal_bin, alg_file))
    conservation = []
    for line in output.split("\n")[3:]:
        a, b = map(float, line.split())
        conservation.append(b)
    mean = numpy.mean(conservation)
    std =  numpy.std(conservation)
    return mean, std

def get_max_identity(alg_file, trimal_bin):
    output = commands.getoutput("%s -sident -in %s" %\
                                    (trimal_bin, alg_file))
    conservation = []
    for line in output.split("\n"):
        m = re.search("#MaxIdentity\s+(\d+\.\d+)", line)
        if m: 
            max_identity = float(m.groups()[0])
    return max_identity

         
def switch_to_codon(alg_fasta_file, alg_phylip_file, nt_seed_file, 
                    kept_columns=[]):
    GAP_CHARS = set(".-")
    NUCLEOTIDES = set("ATCG") 
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
                # If codon does not contain unknown symbols, check
                # that translation is correct
                if not (set(codon) - NUCLEOTIDES) and GENCODE[codon] != ch:
                    log.error("[%s] CDS does not match protein sequence:"
                              " %s = %s not %s at pos %d" %\
                                  (seqname, codon, GENCODE[codon], ch, nt_pos))
                    raise ValueError()

        ntalgseq = "".join(ntalgseq)
        nt_alg.set_seq(seqname, ntalgseq)

    alg_fasta_filename = alg_fasta_file + ".nt"
    alg_phylip_filename = alg_phylip_file + ".nt"
    nt_alg.write(outfile=alg_fasta_filename, format="fasta")
    nt_alg.write(outfile=alg_phylip_filename, format="iphylip_relaxed")
        
    return alg_fasta_filename, alg_phylip_filename
