from os import path
import numpy 
import re
import commands
import logging
log = logging.getLogger("main")
from .utils import del_gaps, GENCODE, PhyloTree, SeqGroup, TreeStyle
from .task import *
from .errors import DataError

n2class = {
    "none": None, 
    "meta_aligner":MetaAligner, 
    "mafft":Mafft, 
    "muscle":Muscle, 
    "uhire":Uhire, 
    "dialigntx":Dialigntx, 
    "fasttree":FastTree, 
    "clustalo": Clustalo, 
    "raxml": Raxml,
    "phyml": Phyml,
    "jmodeltest": JModeltest,
    "prottest": BionjModelChooser,
    "trimal": Trimal
    }


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
    #print "%s -sident -in %s" %\
    #    (trimal_bin, alg_file)
    output = commands.getoutput("%s -sident -in %s" %\
                                    (trimal_bin, alg_file))
    #print output
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


def process_task(task, main_tree, conf):
    aa_seed_file = conf["main"]["aa_seed"]
    nt_seed_file = conf["main"]["nt_seed"]
    seqtype = task.seqtype
    cladeid = task.cladeid
    nseqs = task.nseqs
    sst = conf["main"]["DNA_sst"]
    sit = conf["main"]["DNA_sit"]
    sct = conf["main"]["DNA_sct"]
    ttype = task.ttype

    # Loads application handlers according to current task size
    index = None
    index_slide = 0
    while index is None: 
        try: 
            max_seqs = conf["main"]["npr_max_seqs"][index_slide]
        except IndexError:
            raise DataError("Number of seqs [%d] not considered"
                             " in current config" %nseqs)
        else:
            if nseqs <= max_seqs:
                index = index_slide
            else:
                index_slide += 1

    if seqtype == "nt": 
        _aligner = n2class[conf["main"]["npr_nt_aligner"][index]]
        _alg_cleaner = n2class[conf["main"]["npr_nt_alg_cleaner"][index]]
        _model_tester = n2class[conf["main"]["npr_nt_model_tester"][index]]
        _tree_builder = n2class[conf["main"]["npr_nt_tree_builder"][index]]
    elif seqtype == "aa": 
        _aligner = n2class[conf["main"]["npr_aa_aligner"][index]]
        _alg_cleaner = n2class[conf["main"]["npr_aa_alg_cleaner"][index]]
        _model_tester = n2class[conf["main"]["npr_aa_model_tester"][index]]
        _tree_builder = n2class[conf["main"]["npr_aa_tree_builder"][index]]

    print (nseqs, index, _alg_cleaner, _model_tester,
           _aligner, _tree_builder)

    
    new_tasks = []
    if ttype == "msf":
        alg_task = _aligner(cladeid, task.multiseq_file,
                           seqtype, conf)
        alg_task.nseqs = nseqs
        new_tasks.append(alg_task)

    elif ttype == "alg" or ttype == "acleaner":
        alg_fasta_file = getattr(task, "clean_alg_fasta_file", 
                                 task.alg_fasta_file)
        alg_phylip_file = getattr(task, "clean_alg_phylip_file", 
                                  task.alg_phylip_file)

        # Calculate alignment stats           
        cons_mean, cons_std = get_conservation(task.alg_fasta_file, 
                                               conf["app"]["trimal"])

        max_identity = get_max_identity(task.alg_fasta_file, 
                                        conf["app"]["trimal"])

        log.info("Conservation: %0.2f +-%0.2f", cons_mean, cons_std)
        log.info("Max. Identity: %0.2f", max_identity)
        task.max_identity = max_identity
        task.mean_conservation = cons_mean
        task.std_conservation = cons_std

        if ttype == "alg" and _alg_cleaner:
            next_task = _alg_cleaner(cladeid, seqtype, alg_fasta_file, 
                                     alg_phylip_file, conf)
        else:
            # Converts aa alignment into nt if necessary
            if seqtype == "aa" and nt_seed_file and \
                    task.nseqs <= sst and max_identity > sit and \
                    cons_mean >= sct:
                    log.info("switching to codon alignment")
                    # Change seqtype config 
                    seqtype = "nt"
                    _model_tester = n2class[conf["main"]["npr_nt_model_tester"][index]]
                    _aligner = n2class[conf["main"]["npr_nt_aligner"][index]]
                    _tree_builder = n2class[conf["main"]["npr_nt_tree_builder"][index]]
                    alg_fasta_file, alg_phylip_file = switch_to_codon(
                        task.alg_fasta_file, task.alg_phylip_file, 
                        nt_seed_file)

            if _model_tester:
                next_task = _model_tester(cladeid,
                                         alg_fasta_file, 
                                         alg_phylip_file, 
                                         conf)
            else:
                next_task = _tree_builder(cladeid, alg_phylip_file, None, 
                                          seqtype, conf)

        next_task.nseqs = nseqs
        new_tasks.append(next_task)

    elif ttype == "mchooser":
        alg_fasta_file = task.alg_fasta_file
        alg_phylip_file = task.alg_phylip_file
        model = task.best_model

        tree_task = _tree_builder(task.cladeid, alg_phylip_file, model, 
                                  seqtype, conf)
        tree_task.nseqs = nseqs
        new_tasks.append(tree_task)

    elif ttype == "tree":
        t = PhyloTree(task.tree_file)
        treemerge_task = TreeMerger(cladeid, seqtype, t, main_tree, conf)
        treemerge_task.nseqs = nseqs
        new_tasks.append(treemerge_task)

    elif ttype == "treemerger":
        main_tree = task.main_tree
                      
        for part in [task.set_a, task.set_b]:
            part_cladeid, seqs, outgroups = part
            # Partition size limit
            if len(seqs) >= int(conf["tree_merger"]["_min_size"]) and \
                    len(outgroups) >= int(conf["tree_merger"]["_min_outgroups"]):

                # Creates msf file for the new partitions. If
                # possible, it always uses aa, even when previous tree
                # was done with a codon alignment.
                if conf["main"]["aa_seed"]:
                    alg = SeqGroup(conf["main"]["aa_seed"])
                    seqtype = "aa"
                else:
                    alg = SeqGroup(conf["main"]["nt_seed"])
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

def pipeline(task, main_tree, conf):
    if not task:
        if conf["main"]["aa_seed"]:
            new_tasks = [Msf(None, conf["main"]["aa_seed"], "aa")]
        else:
            new_tasks = [Msf(None, conf["main"]["nt_seed"], "nt")]
    else:
        new_tasks, main_tree = process_task(task, main_tree, conf)

    return new_tasks, main_tree
