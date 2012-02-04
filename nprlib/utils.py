import sys
import os
import socket
from subprocess import Popen
from string import strip
import string 
import random
import hashlib
import logging
log = logging.getLogger("main")

try: 
    from collections import OrderedDict
except ImportError: 
    from ordereddict import OrderedDict

sys.path.insert(0, "/home/jhuerta/_Devel/ete/gui/")
try:
    from ete_dev import PhyloTree, SeqGroup, TreeStyle, NodeStyle, faces
    from ete_dev.parser.fasta import read_fasta
except ImportError:
    from ete2 import PhyloTree, SeqGroup, TreeStyle, NodeStyle, faces
    from ete2.parser.fasta import read_fasta
    

AA = set("ABCDEFGHIJKLMNPOQRSUTVWXYZ") | set("abcdefghijklmnpoqrsutvwxyz") 
NT = set("ACGTURYKMSWBDHVN") | set("acgturykmswbdhvn")

GENCODE = {
    'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M',
    'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T',
    'AAC':'N', 'AAT':'N', 'AAA':'K', 'AAG':'K',
    'AGC':'S', 'AGT':'S', 'AGA':'R', 'AGG':'R',
    'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L',
    'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P',
    'CAC':'H', 'CAT':'H', 'CAA':'Q', 'CAG':'Q',
    'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R',
    'GTA':'V', 'GTC':'V', 'GTG':'V', 'GTT':'V',
    'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A',
    'GAC':'D', 'GAT':'D', 'GAA':'E', 'GAG':'E',
    'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G',
    'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S',
    'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L',
    'TAC':'Y', 'TAT':'Y', 'TAA':'*', 'TAG':'*',
    'TGC':'C', 'TGT':'C', 'TGA':'*', 'TGG':'W', 
    '---': '-',
    }

# Aux functions (general)
md5 = lambda x: hashlib.md5(x).hexdigest()
basename = lambda path: os.path.split(path)[-1]
# Aux functions (task specific)
get_raxml_mem = lambda taxa,sites: (taxa-2) * sites * (80 * 8) * 9.3132e-10
del_gaps = lambda seq: seq.replace("-","").replace(".", "")
random_string = lambda N: ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(N))
generate_id = lambda items: md5(','.join(sorted(items)))

def generate_node_ids(target_seqs, out_seqs):
    cladeid = generate_id(target_seqs)
    nodeid = md5(','.join([cladeid, generate_id(out_seqs)]))
    return nodeid, cladeid

HOSTNAME = socket.gethostname()

def merge_arg_dicts(source, target, parent=""):
    for k,v in source.iteritems(): 
        if not k.startswith("_"): 
            if k not in target:
                target[k] = v
            else:
                log.warning("%s: [%s] argument cannot be manually set" %(parent,k))
    return target

def load_node_size(n):
    if n.is_leaf():
        size = 1
    else:
        size = 0
        for ch in n.children: 
            size += load_node_size(ch)
    n.add_feature("_size", size)
    return size

def render_tree(tree, fname):
    # Generates tree snapshot 
    npr_nodestyle = NodeStyle()
    npr_nodestyle["fgcolor"] = "red"
    for n in tree.traverse():
        if hasattr(n, "nodeid"):
            n.set_style(npr_nodestyle)
    ts = TreeStyle()
    ts.show_leaf_name = True
    ts.show_branch_length = True
    ts.show_branch_support = True
    ts.mode = "r"
    iterface = faces.TextFace("iter")
    ts.legend.add_face(iterface, 0)

    tree.dist = 0
    tree.sort_descendants()
    tree.render(fname, tree_style = ts, w = 700)

def checksum(*fnames):
    block_size=2**20
    hash = hashlib.md5()
    for fname in fnames:
        f = open(fname, "rb")
        while True:
            data = f.read(block_size)
            if not data:
                break
            hash.update(data)
        f.close()
    return hash.hexdigest()

def pid_up(pid):        
    """ Check For the existence of a unix pid. """
    try:
        os.kill(int(pid), 0)
    except OSError:
        return False
    else:
        return True

def print_as_table(rows, header=[], print_header=True, stdout=sys.stdout):
    """ Print >>Stdout, a list matrix as a formated table. row must be a list of
    dicts or lists."""

    def _str(i):
        if isinstance(i, float):
            return "%0.2f" %i
        else:
            return str(i)

    vtype = None
    for v in rows:
        if vtype != None and type(v)!=vtype:
            raise "ValueError", "Mixed row types in input"
        else:
            vtype = type(v)
	    
    lengths  = {}
    if vtype == list or vtype == tuple:
        v_len = len(rows[0])
        if header and len(header)!=v_len:
            raise Exception("Bad header length")

        # Get max size of each field
        for i in xrange(v_len):
            header_length = 0
            if header != []:
                header_length = len(_str(header[i]))
            max_field_length = max( [ len(_str(r[i])) for r in rows] )
            lengths[i] = max( [ header_length, max_field_length ] )

        if header and print_header:
            # Print >>Stdout, header names
            for i in xrange(v_len):
                print >>stdout, _str(header[i]).rjust(lengths[i])+" | ",
            print >>stdout, ""
            # Print >>Stdout, underlines
            for i in xrange(v_len):
                print >>stdout, "".rjust(lengths[i],"-")+" | ",
            print >>stdout, ""
        # Print >>Stdout, table lines
        for r in rows:
            for i in xrange(v_len):
                print >>stdout, _str(r[i]).rjust(lengths[i])+" | ",
            print >>stdout, ""

    elif vtype == dict:
        if header == []:
            header = rows[0].keys()
        for ppt in header:
            lengths[ppt] = max( [len(_str(ppt))]+[ len(_str(p.get(ppt,""))) for p in rows])
        if header:
            for ppt in header:
                    print >>stdout, _str(ppt).rjust(lengths[ppt])+" | ",
            print >>stdout, ""
            for ppt in header:
                    print >>stdout, "".rjust(lengths[ppt],"-")+" | ",
            print >>stdout, ""
        page_counter = 0
        for p in rows:
            for ppt in header:
                print >>stdout, _str(p.get(ppt,"")).rjust(lengths[ppt])+" | ",
            print >>stdout, ""
            page_counter +=1

    