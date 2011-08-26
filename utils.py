import os
from string import strip
import hashlib

# Aux functions (general)
get_md5 = lambda x: hashlib.md5(x).hexdigest()
basename = lambda path: os.path.split(path)[-1]
# Aux functions (task specific)
get_raxml_mem = lambda taxa,sites: (taxa-2) * sites * (80 * 8) * 9.3132e-10
get_cladeid = lambda seqids: get_md5(','.join(sorted(map(strip, seqids))))
del_gaps = lambda seq: seq.replace("-","").replace(".", "")
