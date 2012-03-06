import os
import numpy 
import re
import commands
import logging
import numpy
from collections import defaultdict

from nprlib.utils import (del_gaps, GENCODE, PhyloTree, SeqGroup,
                          TreeStyle, generate_node_ids, DEBUG, NPR_TREE_STYLE, faces)
from nprlib.task import (MetaAligner, Mafft, Muscle, Uhire, Dialigntx,
                         FastTree, Clustalo, Raxml, Phyml, JModeltest,
                         Prottest, Trimal, TreeMerger, select_outgroups,
                         Msf)
from nprlib.errors import DataError

log = logging.getLogger("main")

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
    "prottest": Prottest,
    "trimal": Trimal
    }

def get_trimal_conservation(alg_file, trimal_bin):
    output = commands.getoutput("%s -ssc -in %s" % (trimal_bin,
                                                    alg_file))
    conservation = []
    for line in output.split("\n")[3:]:
        a, b = map(float, line.split())
        conservation.append(b)
    mean = numpy.mean(conservation)
    std =  numpy.std(conservation)
    return mean, std

def get_statal_identity(alg_file, statal_bin):
    output = commands.getoutput("%s -scolidentt -in %s" % (statal_bin,
                                                           alg_file))
    ## Columns Identity Descriptive Statistics
    #maxColIdentity	1
    #minColIdentity	0.428571
    #avgColIdentity	0.781853
    #stdColIdentity	0.2229
    #print output
    maxi, mini, avgi, stdi = [None]*4
    for line in output.split("\n"):
        if line.startswith("#maxColIdentity"):
            maxi = float(line.split()[1])
        elif line.startswith("#minColIdentity"):
            mini = float(line.split()[1])
        elif line.startswith("#avgColIdentity"):
            avgi = float(line.split()[1])
        elif line.startswith("#stdColIdentity"):
            stdi = float(line.split()[1])
            break
    return maxi, mini, avgi, stdi
    
def get_trimal_identity(alg_file, trimal_bin):
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

def get_identity(fname): 
    s = SeqGroup(fname)
    seqlen = len(s.id2seq.itervalues().next())
    ident = list()
    for i in xrange(seqlen):
        states = defaultdict(int)
        for seq in s.id2seq.itervalues():
            if seq[i] != "-":
                states[seq[i]] += 1
        values = states.values()
        if values:
            ident.append(float(max(values))/sum(values))
    return (numpy.max(ident), numpy.min(ident), 
            numpy.mean(ident), numpy.std(ident))

         
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

def process_task(task, main_tree, conf, nodeid2info):
    aa_seed_file = conf["main"]["aa_seed"]
    nt_seed_file = conf["main"]["nt_seed"]
    seqtype = task.seqtype
    nodeid = task.nodeid
    ttype = task.ttype
    node_info = nodeid2info[nodeid]
    nseqs = task.nseqs#node_info.get("nseqs", 0)
    target_seqs = node_info.get("target_seqs", [])
    out_seqs = node_info.get("out_seqs", [])
    constrain_tree = None
    constrain_tree_path = None
    if out_seqs and len(out_seqs) > 1:
        constrain_tree = "((%s), (%s));" %(','.join(out_seqs), 
                                           ','.join(target_seqs))
        constrain_tree_path = os.path.join(task.taskdir, "constrain.nw")
                                           
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
        #log.debug("INDEX %s %s %s", index, nseqs, max_seqs)
                
    _min_branch_support = conf["main"]["npr_min_branch_support"][index_slide]
    skip_outgroups = _min_branch_support < 1.0 and conf["tree_splitter"]["_outgroup_size"] == 0
    
    if seqtype == "nt": 
        _aligner = n2class[conf["main"]["npr_nt_aligner"][index]]
        _alg_cleaner = n2class[conf["main"]["npr_nt_alg_cleaner"][index]]
        _model_tester = n2class[conf["main"]["npr_nt_model_tester"][index]]
        _tree_builder = n2class[conf["main"]["npr_nt_tree_builder"][index]]
        _aa_identity_thr = 1.0
    elif seqtype == "aa": 
        _aligner = n2class[conf["main"]["npr_aa_aligner"][index]]
        _alg_cleaner = n2class[conf["main"]["npr_aa_alg_cleaner"][index]]
        _model_tester = n2class[conf["main"]["npr_aa_model_tester"][index]]
        _tree_builder = n2class[conf["main"]["npr_aa_tree_builder"][index]]
        _aa_identity_thr = conf["main"]["npr_max_aa_identity"][index]

    #print node_info, (nseqs, index, _alg_cleaner, _model_tester, _aligner, _tree_builder)
    
    new_tasks = []
    if ttype == "msf":
        alg_task = _aligner(nodeid, task.multiseq_file,
                           seqtype, conf)
        nodeid2info[nodeid]["nseqs"] = task.nseqs
        nodeid2info[nodeid]["target_seqs"] = task.target_seqs
        nodeid2info[nodeid]["out_seqs"] = task.out_seqs
        alg_task.nseqs = task.nseqs
        new_tasks.append(alg_task)

    elif ttype == "alg" or ttype == "acleaner":
        alg_fasta_file = getattr(task, "clean_alg_fasta_file",
                                 task.alg_fasta_file)
        alg_phylip_file = getattr(task, "clean_alg_phylip_file",
                                  task.alg_phylip_file)

        # Calculate alignment stats           
        # cons_mean, cons_std = get_trimal_conservation(task.alg_fasta_file, 
        #                                        conf["app"]["trimal"])
        #  
        # max_identity = get_trimal_identity(task.alg_fasta_file, 
        #                                 conf["app"]["trimal"])
        # log.info("Conservation: %0.2f +-%0.2f", cons_mean, cons_std)
        # log.info("Max. Identity: %0.2f", max_identity)
        #import time
        #t1 = time.time()
        #mx, mn, mean, std = get_identity(task.alg_fasta_file)
        #print time.time()-t1
        #log.log(26, "Identity: max=%0.2f min=%0.2f mean=%0.2f +- %0.2f",
        #        mx, mn, mean, std)
        #t1 = time.time()
        mx, mn, mean, std = get_statal_identity(task.alg_phylip_file,
                                                conf["app"]["statal"])
        #print time.time()-t1
        log.log(26, "Identity: max=%0.2f min=%0.2f mean=%0.2f +- %0.2f",
                mx, mn, mean, std)
        task.max_ident = mx
        task.min_ident = mn
        task.mean_ident = mean
        task.std_ident = std
        
        if ttype == "alg" and _alg_cleaner:
            next_task = _alg_cleaner(nodeid, seqtype, alg_fasta_file, 
                                     alg_phylip_file, conf)
        else:
            # Converts aa alignment into nt if necessary
            if seqtype == "aa" and nt_seed_file and \
               task.mean_ident > _aa_identity_thr:
                log.log(26, "switching to codon alignment")
                # Change seqtype config 
                seqtype = "nt"
                _model_tester = n2class[conf["main"]["npr_nt_model_tester"][index]]
                _aligner = n2class[conf["main"]["npr_nt_aligner"][index]]
                _tree_builder = n2class[conf["main"]["npr_nt_tree_builder"][index]]
                alg_fasta_file, alg_phylip_file = switch_to_codon(
                    task.alg_fasta_file, task.alg_phylip_file,
                    nt_seed_file)
            if constrain_tree:
                open(constrain_tree_path, "w").write(constrain_tree)
                                           
            if _model_tester:
                next_task = _model_tester(nodeid,
                                          alg_fasta_file, 
                                          alg_phylip_file,
                                          constrain_tree_path,
                                          conf)
            else:
                next_task = _tree_builder(nodeid, alg_phylip_file, constrain_tree_path,
                                          None,
                                          seqtype, conf)
        next_task.nseqs = task.nseqs
        new_tasks.append(next_task)

    elif ttype == "mchooser":
        alg_fasta_file = task.alg_fasta_file
        alg_phylip_file = task.alg_phylip_file
        model = task.get_best_model()
        if constrain_tree:
            open(constrain_tree_path, "w").write(constrain_tree)
                                          
        tree_task = _tree_builder(nodeid, alg_phylip_file, constrain_tree_path,
                                  model,
                                  seqtype, conf)
        tree_task.nseqs = task.nseqs
        new_tasks.append(tree_task)

    elif ttype == "tree":
        treemerge_task = TreeMerger(nodeid, seqtype, task.tree_file, main_tree, conf)
        #if conf["tree_splitter"]["_outgroup_size"]:
        #    treemerge_task = TreeSplitterWithOutgroups(nodeid, seqtype, task.tree_file, main_tree, conf)
        #else:
        #    treemerge_task = TreeSplitter(nodeid, seqtype, task.tree_file, main_tree, conf)

        treemerge_task.nseqs = task.nseqs
        new_tasks.append(treemerge_task)

    elif ttype == "treemerger":
        if conf["main"]["aa_seed"]:
            source = SeqGroup(conf["main"]["aa_seed"])
            source_seqtype = "aa"
        else:
            source = SeqGroup(conf["main"]["nt_seed"])
            source_seqtype = "nt"

        if not task.task_tree:
            task.finish()
        main_tree = task.main_tree
        #print task.task_tree.get_ascii(attributes=["name", "support"])
        #print task.task_tree
        # processable_node = lambda _n: (_n is not task.task_tree and
        #                                _n.children and
        #                                _n.support <= _min_branch_support)

        def processable_node(_n):
            _isleaf = False
            if _n is not task.task_tree:
                if skip_outgroups:
                    # If we are optimizing only lowly supported nodes, and
                    # nodes are optimized without outgroup, our target node is
                    # actually the parent of the real target. Otherwise,
                    # select outgroups from sister partition.
                    for _ch in _n.children:
                        if _ch.support <= _min_branch_support:
                            _isleaf = True
                            break
                elif _n.support <= _min_branch_support:
                    _isleaf = True
            return _isleaf
        
        n2content = main_tree.get_node2content()
        for node in task.task_tree.iter_leaves(is_leaf_fn=processable_node):
            if skip_outgroups:
                seqs = set([_i.name for _i in n2content[node]])
                outs = set()
            else:
                seqs, outs = select_outgroups(node, n2content, conf["tree_splitter"])

            if (conf["_iters"] < int(conf["main"].get("max_iters", conf["_iters"]+1)) and 
                len(seqs) >= int(conf["tree_splitter"]["_min_size"])):
                    msf_task = Msf(seqs, outs, seqtype=source_seqtype, source=source)
                    if msf_task.nodeid not in nodeid2info:
                        nodeid2info[msf_task.nodeid] = {}
                        new_tasks.append(msf_task)
                        conf["_iters"] += 1
                    if DEBUG():
                        node.img_style["fgcolor"] = "Green"
                        node.img_style["size"] = 60
                        node.add_face(faces.TextFace("%s" %conf["_iters"], fsize=24), 0, "branch-top")
        if DEBUG():
            task.task_tree.show(tree_style=NPR_TREE_STYLE)
            for _n in task.main_tree.traverse():
                _n.img_style = None
           

    return new_tasks, main_tree

def pipeline(task, main_tree, conf, nodeid2info):
    if not task:
        if conf["main"]["aa_seed"]:
            source = SeqGroup(conf["main"]["aa_seed"])
            source_seqtype = "aa"
        else:
            source = SeqGroup(conf["main"]["nt_seed"])
            source_seqtype = "nt"

        new_tasks = [Msf(set(source.id2name.values()), set(),
                         seqtype=source_seqtype,
                         source = source)]
        conf["_iters"] = 1
    else:
        new_tasks, main_tree = process_task(task, main_tree, conf, nodeid2info)

    return new_tasks, main_tree

config_specs = """

[main]
max_iters = integer(minv=1)
render_tree_images = boolean()

npr_max_seqs = integer_list(minv=0)
npr_min_branch_support = float_list(minv=0, maxv=1)

npr_max_aa_identity = float_list(minv=0.0)

npr_nt_alg_cleaner = list()
npr_aa_alg_cleaner = list()

npr_aa_aligner = list()
npr_nt_aligner = list()

npr_aa_tree_builder = list()
npr_nt_tree_builder = list()

npr_aa_model_tester = list()
npr_nt_model_tester = list()

[tree_splitter]
_min_size = integer()
_outgroup_size = integer()


"""