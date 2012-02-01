import os
import re
apps = {
    'muscle'         : "%BIN%/muscle",
    'mafft'          : "MAFFT_BINARIES=~/_Projects/npr/external_apps/mafft-6.861-without-extensions/binaries/  %BIN%/mafft",
    'clustalo'       : "%BIN%/clustalo",
    'trimal'         : "%BIN%/trimal",
    'readal'         : "%BIN%/readal",
    'tcoffee'        : "export DIR_4_TCOFFEE=%BIN%/t_coffee_9_01 MAFFT_BINARIES=$DIR_4_TCOFFEE/plugins/linux/ TMP_4_TCOFFEE=/tmp/ LOCKDIR_4_TCOFFEE=/tmp/  PERL5LIB=$PERL5LIB:$DIR_4_TCOFFEE/perl  && $DIR_4_TCOFFEE/bin/t_coffee",
    'phyml'          : "%BIN%/phyml",
    'raxml-pthreads' : "%BIN%/raxmlHPC-PTHREADS-SSE3",
    'raxml'          : "%BIN%/raxmlHPC-SSE3",
    'jmodeltest'     : "JMODELTEST_HOME=~/_Projects/npr/external_apps/jmodeltest2; cd $JMODELTEST_HOME; java -jar $JMODELTEST_HOME/jModelTest.jar",
    'dialigntx'      : "%BIN%/dialign-tx %BIN%/DIALIGN-TX_1.0.2/conf/",
    'usearch'        : "%BIN%/usearch",
    'fasttree'       : "%BIN%/FastTree",
    }

def get_call(appname, nprpath):
    try:
        cmd = apps[appname]
    except KeyError:
        return None
    binpath = os.path.join(nprpath, "apps")
    libpath = os.path.join(binpath, "local_libs")
    cmd = re.sub("%BIN%", binpath, cmd)
    cmd = "export LD_LIBRARY_PRELOAD=%s:$LD_LIBRARY_PRELOAD; " %(libpath) +cmd
    return cmd

    
    