import os
import re
apps = {
    'muscle'         : "%BIN%/muscle",
    'mafft'          : "MAFFT_BINARIES=%BIN%/mafft-6.861-without-extensions/binaries/  %BIN%/mafft",
    'clustalo'       : "%BIN%/clustalo",
    'trimal'         : "%BIN%/trimal",
    'readal'         : "%BIN%/readal",
    'tcoffee'        : "export DIR_4_TCOFFEE=%BIN%/t_coffee_9_01 MAFFT_BINARIES=$DIR_4_TCOFFEE/plugins/linux/ TMP_4_TCOFFEE=/tmp/ LOCKDIR_4_TCOFFEE=/tmp/  PERL5LIB=$PERL5LIB:$DIR_4_TCOFFEE/perl  && $DIR_4_TCOFFEE/bin/t_coffee",
    'phyml'          : "%BIN%/phyml",
    'raxml-pthreads' : "%BIN%/raxmlHPC-PTHREADS-SSE3",
    'raxml'          : "%BIN%/raxmlHPC-SSE3",
    'jmodeltest'     : "JMODELTEST_HOME=%BIN%/jmodeltest2; cd $JMODELTEST_HOME; java -jar $JMODELTEST_HOME/jModelTest.jar",
    'dialigntx'      : "%BIN%/dialign-tx %BIN%/DIALIGN-TX_1.0.2/conf/",
    'usearch'        : "%BIN%/usearch",
    'fasttree'       : "%BIN%/FastTree",
    }

def get_call(appname, apps_path):
    try:
        cmd = apps[appname]
    except KeyError:
        return None
    libpath = os.path.join(apps_path, "local_libs")
    cmd = re.sub("%BIN%", apps_path, cmd)
    #cmd = "export LD_LIBRARY_PATH=%s:$LD_LIBRARY_PATH; " %(libpath) +cmd
    return cmd
  
    