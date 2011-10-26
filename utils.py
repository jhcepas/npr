import os
from string import strip
import hashlib
import logging
log = logging.getLogger("main")

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
get_md5 = lambda x: hashlib.md5(x).hexdigest()
basename = lambda path: os.path.split(path)[-1]
# Aux functions (task specific)
get_raxml_mem = lambda taxa,sites: (taxa-2) * sites * (80 * 8) * 9.3132e-10
get_cladeid = lambda seqids: get_md5(','.join(sorted(map(strip, seqids))))
del_gaps = lambda seq: seq.replace("-","").replace(".", "")

def merge_dicts(source, target, parent=""):
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
    n.add_feature("size", size)
    return size


