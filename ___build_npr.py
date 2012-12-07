#!/usr/bin/env python

# requires: 
#  pdflatex tools
# python twitter module 
# sphinx

import os
import sys
import commands
import readline
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-e", "--examples", dest="test_examples", \
                      action="store_true", \
                      help="Test tutorial examples before building package")

parser.add_option("-d", "--doc", dest="doc", \
                      action="store_true", \
                      help="Process documentation files")

parser.add_option("--a32", dest="a32", \
                      action="store_true", \
                      help="compile for 32 bits")

parser.add_option("-D", "--doc-only", dest="doc_only", \
                      action="store_true", \
                      help="Process last modifications of the documentation files. No git commit necessary. Package is not uploaded to PyPI")

parser.add_option("-v", "--verbose", dest="verbose", \
                      action="store_true", \
                      help="It shows the commands that are executed at every step.")

parser.add_option("-s", "--simulate", dest="simulate", \
                      action="store_true", \
                      help="Do not actually do anything. ")

(options, args) = parser.parse_args()

print options

def _ex(cmd, interrupt=True):
    if options.verbose or options.simulate:
        print "***", cmd
    if not options.simulate:
        s = os.system(cmd)
        if s != 0 and interrupt:
            sys.exit(s)
        else:
            return s
    else:
        return 0

def ask(string, valid_values, default=-1, case_sensitive=False):
    """ Asks for a keyborad answer """

    v = None
    if not case_sensitive:
        valid_values = [value.lower() for value in valid_values]
    while v not in valid_values:
        readline.set_startup_hook(lambda: readline.insert_text(default))
        try:
            v = raw_input("%s [%s] " % (string, ', '.join(valid_values))).strip()
            if v == '' and default>=0:
                v = valid_values[default]
            if not case_sensitive:
                v = v.lower()
        finally:
            readline.set_startup_hook()
    return v

def ask_path(string, default_path):
    v = None
    while v is None:
        v = raw_input("%s [%s] " % (string, default_path)).strip()
        if v == '':
            v = default_path
        if not os.path.exists(v):
            print >>sys.stderr, v, "does not exist."
            v = None
    return v

#Check repo is commited

#Creates a release clone
#SERVER="jhuerta@cgenomics"
#SERVER_RELEASES_PATH = "/home/services/web/ete.cgenomics.org/releases/ete2"
#SERVER_DOC_PATH = "/home/services/web/ete.cgenomics.org/releases/ete2/doc"
#SERVER_METAPKG_PATH = "/home/services/web/ete.cgenomics.org/releases/ete2/metapkg"
#METAPKG_JAIL_PATH = "/home/jhuerta/_Devel/ete_metapackage/etepkg_CheckBeforeRm"
#METAPKG_PATH = "/home/jhuerta/_Devel/ete_metapackage"

CHROOT_32_PATH = "../npr_pkg/debian32"
CHROOT_64_PATH = "../npr_pkg/debian64"

RELEASES_BASE_PATH = "../npr_pkg"
MODULE_NAME = "npr"
MODULE_RELEASE = "1.0"
REVISION = commands.getoutput("git log --pretty=format:'' | wc -l").strip()
VERSION = MODULE_RELEASE+ "rev" + REVISION
VERSION_LOG = commands.getoutput("git log --pretty=format:'%s' | head -n1").strip()
RELEASE_NAME = MODULE_NAME+"-"+VERSION
RELEASE_PATH = os.path.join(RELEASES_BASE_PATH, RELEASE_NAME)
RELEASE_MODULE_PATH = os.path.join(RELEASE_PATH, MODULE_NAME)
DOC_PATH = os.path.join(RELEASE_PATH, "doc")

print "================================="
print
print "VERSION", VERSION
print "RELEASE:", RELEASE_NAME
print "RELEASE_PATH:", RELEASE_PATH
print
print "================================="

if os.path.exists(RELEASE_PATH):
    print RELEASE_PATH, "exists"
    overwrite = ask("Overwrite current release path?",["y","n"])
    if overwrite=="y":
        _ex("rm %s -rf" %RELEASE_PATH)
    else:
        print "Aborted."
        sys.exit(-1)

if options.doc_only:
    print "Creating a repository copy in ", RELEASE_PATH
    options.doc = True
    process_package = False
    _ex("mkdir %s; cp -a ./ %s" %(RELEASE_PATH, RELEASE_PATH))
else:
    process_package = True
    print "Creating a repository clone in ", RELEASE_PATH
    _ex("git clone . %s" %RELEASE_PATH)

# Set VERSION in all modules
print "*** Setting VERSION in all python files..."
_ex('find %s/ete_dev/ -name \'*.py\' |xargs sed \'1 i __VERSION__=\"%s\" \' -i' %\
              (RELEASE_PATH, RELEASE_NAME))

# Generating VERSION file
print "*** Generating VERSION file..."
_ex('echo %s > %s/VERSION' %\
              (VERSION, RELEASE_PATH))

print "Cleaning doc dir..."
_ex("mv %s/doc %s/sdoc" %(RELEASE_PATH, RELEASE_PATH))
_ex("mkdir %s/doc" %(RELEASE_PATH))

if options.doc:
    print "*** Creating reference guide"
    #_ex('export PYTHONPATH="%s/build/lib/"; epydoc %s -n %s --exclude PyQt4  --inheritance grouped --name ete2 -o %s/doc/ete_guide_html' %\
    #              (RELEASE_PATH, RELEASE_MODULE_PATH, RELEASE_NAME, RELEASE_PATH))
    #_ex('export PYTHONPATH="%s/build/lib/"; epydoc %s -n %s  --exclude PyQt4 --pdf --inheritance grouped --name ete2 -o %s/doc/latex_guide' %\
    #_ex('export PYTHONPATH="%s/build/lib/"; epydoc %s -n %s  --exclude PyQt4  --inheritance grouped --name ete2 -o %s/doc/latex_guide' %\
    #              (RELEASE_PATH, RELEASE_MODULE_PATH, RELEASE_NAME, RELEASE_PATH))
    # _ex("cp %s/doc/latex_guide/api.pdf %s/doc/%s.pdf " %\
    #              (RELEASE_PATH, RELEASE_PATH, RELEASE_NAME))

    # Generates PDF doc
    _ex("cd %s/sdoc; make latex" % RELEASE_PATH)
    _ex("cd %s/sdoc/_build/latex/; make all-pdf" % RELEASE_PATH)
    _ex("cp -a %s/sdoc/_build/latex/*.pdf %s/doc/" %(RELEASE_PATH, RELEASE_PATH))

    # Generates HTML doc (it includes a link to the PDF doc, so it
    # must be executed after PDF commands)
    _ex("cd %s/sdoc; make html" % RELEASE_PATH)
    _ex("cp -a %s/sdoc/_build/html/ %s/doc/" %(RELEASE_PATH, RELEASE_PATH))

    # Set the correct ete module name in all doc files
    #_ex('find %s/doc | xargs perl -e "s/ete_dev/%s/g" -p -i' %\
    #        (RELEASE_PATH, MODULE_NAME) )

    copydoc= ask("Update ONLINE documentation?", ["y","n"])
    if copydoc=="y":
        # INSTALL THIS http://pypi.python.org/pypi/Sphinx-PyPI-upload/0.2.1
        print "Uploading"
        
        # Always upload DOC to the main page
        _ex(' cd %s; cp VERSION _VERSION;  perl -e "s/%s/npr/g" -p -i VERSION;' %\
                (RELEASE_PATH, MODULE_NAME))
        
        _ex("cd %s; python setup.py upload_sphinx --upload-dir %s/doc/html/ --show-response" %\
                (RELEASE_PATH, RELEASE_PATH))

        # Restore real VERSION 
        _ex(' cd %s; mv _VERSION VERSION;' % (RELEASE_PATH) )

        #_ex("cd %s; rsync -arv doc/html/ jhuerta@cgenomics:/data/services/web/ete.cgenomics.org/doc/2.1/" %\
        #        (RELEASE_PATH))

        #_ex("rsync -r %s/doc/ete_guide_html/ %s/html/" %\
        #        (RELEASE_PATH, SERVER+":"+SERVER_DOC_PATH))

if process_package:
    # Clean from internal files
    _ex("rm %s/.git -rf" %\
            (RELEASE_PATH))
    #_ex('rm %s/build/ -r' %(RELEASE_PATH))
    _ex('rm %s/sdoc/ -rf' %(RELEASE_PATH))
    _ex('rm %s/___* -rf' %(RELEASE_PATH))


    if ask("Cross compile within CHROOT?",["y","n"]) ==  "y":
        if options.a32: 
            CHROOT_PATH = CHROOT_32_PATH
            ARCH = "32bits"
        else: 
            CHROOT_PATH = CHROOT_64_PATH
            ARCH = "64bits"
            
        PORTABLE_PATH =  "%s_portable_%s" %(RELEASE_PATH, ARCH)
        RELEASE_CHROOT_PATH = '%s/opt/%s' %(CHROOT_PATH, RELEASE_NAME)
        _ex('cp %s/cde* %s' %(RELEASES_BASE_PATH, RELEASE_PATH))
        open("%s/cde.options" %RELEASE_PATH, "a").write("\nredirect_prefix=/opt/%s\n\n" %RELEASE_NAME)

        print "Now copying to chroot environment (need root permission):"
        if os.path.exists(RELEASE_CHROOT_PATH):
            _ex('sudo rm -r %s' %RELEASE_CHROOT_PATH)

        _ex('sudo cp -r %s %s/opt/' %(RELEASE_PATH, CHROOT_PATH))
        _ex('sudo cp -r %s/opt/ext_apps/ %s' %(CHROOT_PATH, RELEASE_CHROOT_PATH))
        os.system('sudo chroot %s env -i HOME=/root TERM="$TERM" /opt/%s/cde_make_portable.sh' %(CHROOT_PATH, RELEASE_NAME))
    
    if ask("Build portable package (will extract portable dir from chroot)?",["y","n"]) ==  "y":
        if os.path.exists(PORTABLE_PATH):
            print PORTABLE_PATH, "exists"
            overwrite = ask("Overwrite?",["y","n"])
            if overwrite=="y":
                _ex("rm %s -rf" %PORTABLE_PATH)

        _ex('mkdir %s' %PORTABLE_PATH)
        
        _ex('cp -r %s/tmp/portable_npr/ %s_portable_%s' %(CHROOT_PATH, RELEASE_PATH, ARCH))
        for cmd in ["npr", "nprtop", "nprdump", "nprete"]:
            script = open("%s/%s" %(PORTABLE_PATH, cmd), "w")
            print >>script, "#!/bin/sh"
            print >>script, 'DIR="$(dirname "$(readlink -f "${0}")")"'
            print >>script, '$DIR/portable_npr/cde-exec /opt/%s/%s $@ \n' %(RELEASE_NAME, cmd)
            script.close()
            _ex("chmod +x %s/%s" %(PORTABLE_PATH, cmd))        
    
