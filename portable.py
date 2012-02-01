import sys
import re
import os
import shutil
import commands

def get_libs(fname):
    raw = commands.getoutput("ldd %s" %fname)
    libs = set()
    skipped = set()
    for line in raw.split("\n"):
        if line == "not a dynamic executable":
            continue
        else:
            m = re.search("(/.+?\.so(\.\d+)?)", line)
            if m:
                path = m.groups()[0]
                if os.path.exists(path):
                    libs.add(path)
                    _libs, _skipped = get_libs(path)
                    libs.update(_libs)
                    skipped.update(_skipped)
            else:
                skipped.add(line)

    return libs, skipped

inpath = os.path.realpath(sys.argv[1])
libpath = os.path.join("./portable_lib")

os.mkdir(libpath)

if os.path.isfile(inpath):
    libfiles, skipped = get_libs(inpath)
else:
    print >>sys.stderr, "Creating list of ELF 64bits files"
    filelist = commands.getoutput('find %s -type f -exec file {} \;|grep ELF|grep executable|grep dynamically|cut -f1 -d":"' %inpath)
    
    libfiles = set()
    skipped = set()
    for fname in filelist.split("\n"):
        print >>sys.stderr, "procesing", fname
        _libs, _skipped = get_libs(fname)
        libfiles.update(_libs)
        skipped.update(_skipped)

       
print >>sys.stderr,'\n'.join(libfiles)
print >>sys.stderr, "****** SKIPPED LINES:"
print >>sys.stderr,'\n'.join(libfiles)

for x in libfiles:
    shutil.copy(x, libpath)
   
print "LD_LIBRARY_PATH=%s:$LD_LIBRARY_PATH} %s/BINARY" %(libpath, inpath)

    