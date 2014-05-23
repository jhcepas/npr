from string import strip
from collections import defaultdict
import argparse
parser = argparse.ArgumentParser()
from pprint import pprint

tpl = parser.add_argument_group('TEMPLATE')
tpl.add_argument('-npr', dest='npr', default='noNPR')
tpl.add_argument('-appset', dest='appset', default='builtin_apps')
tpl.add_argument('-c', dest='config')
tpl.add_argument('-meta', dest='meta', nargs='+')


args = parser.parse_args()


TEMPLATE = """
[{name}]
_app = main
_max_seqs = 9999999999,
_npr = {npr_config},
_workflow = {workflow},
_appset = {appset}

[w.{name}]
_app = genetree
_aa_aligner           =   {aa_aligner}
_aa_alg_cleaner       =   {aa_trimmer}
_aa_model_tester      =   {aa_tester}
_aa_tree_builder      =   {aa_treebuilder}
 
_nt_aligner           =   {nt_aligner}
_nt_alg_cleaner       =   {nt_trimmer}
_nt_model_tester      =   none
_nt_tree_builder      =   {nt_treebuilder}
"""

workflows = dict()
names = defaultdict(list)

for metaline in args.meta:
    for subline in metaline.split(';'):
        subline = subline.strip()
        if subline.startswith('name:'):
            tagname = subline[5:].strip()
        elif subline.startswith('a:'):
            aligners = map(strip, subline[2:].split(','))
        elif subline.startswith('a:'):
            aligners = map(strip, subline[2:].split(','))
        elif subline.startswith('r:'):
            trimmers = map(strip, subline[2:].split(','))
        elif subline.startswith('m:'):
            modelers = map(strip, subline[2:].split(','))
        elif subline.startswith('t:'):
            treebuilders = map(strip, subline[2:].split(','))
    for al in aligners:
        if al != "none": al = "@%s" %al
        for tr in trimmers:
            if tr != "none": tr = "@%s" %tr
            for pt in modelers:
                if pt != "none": pt = "@%s" %pt
                for tb in treebuilders:
                    if tb != "none": tb = "@%s" %tb
                    name = '-'.join(map(lambda x: x.lstrip('@'),[al, tr, pt, tb]))
                    CFG = TEMPLATE.replace('{name}', name)
                    CFG = CFG.replace('{appset}', "@"+args.appset)
                    CFG = CFG.replace('{npr_config}', "@"+args.npr)
                    CFG = CFG.replace('{workflow}', "@w."+name)
                    
                    CFG = CFG.replace('{aa_aligner}', al)
                    CFG = CFG.replace('{aa_aligner}', al)
                    CFG = CFG.replace('{nt_aligner}', al)
                    CFG = CFG.replace('{aa_trimmer}', tr)
                    CFG = CFG.replace('{nt_trimmer}', tr)
                    CFG = CFG.replace('{aa_tester}', pt)
                    CFG = CFG.replace('{aa_treebuilder}', tb)
                    CFG = CFG.replace('{nt_treebuilder}', tb)
                    names[tagname].append(name)
                    workflows[name] = CFG

OUT = open('auto_config.cfg', 'w')
print >>OUT, '[meta_workflow]\n%s' %('\n'.join(
        ["%s=%s," %(k, ','.join(map(lambda x: "@"+x, v))) for k,v in names.iteritems()]))
   
print >>OUT, '\n'.join(workflows.values())
print >>OUT, open(args.config).read()                
OUT.close()

                
                
                
