#!/usr/bin/env python
import sys
import os
import cPickle
from string import strip
import commands

# This avoids installing nprlib module. npr script will find it in the
# same directory in which it is
NPRPATH = os.path.split(os.path.realpath(__file__))[0]
sys.path.insert(0, NPRPATH)

from nprlib.argparse import ArgumentParser, RawDescriptionHelpFormatter
from nprlib.logger import get_main_log
   
__DESCRIPTION__ = "Benchmark iter snapshots"
       
if __name__ == "__main__":
    log = get_main_log(sys.stderr)
    
    parser = ArgumentParser(description=__DESCRIPTION__, 
                            formatter_class=RawDescriptionHelpFormatter)
 
    parser.add_argument('nprdir', metavar='npr_base_dir', type=str, nargs=1,
                   help='path to an NPR execution directory')

    parser.add_argument("-g",  dest="generate_cmds", 
                        action="store_true",
                        help="""Prints benchmark commands """)
    
    parser.add_argument("--tag",  dest="report_tag", 
                        type=str, default=".report",
                        help="""Tag used for report files""")

    parser.add_argument("--reportfile",  dest="reportfile", 
                        type=str, 
                        help="""Use this reportfile""")

    parser.add_argument("-b",  dest="branch_assembly", 
                        action="store_true", 
                        help=""" branch assembly""")

    
    args = parser.parse_args()

    iterfiles = commands.getoutput("find %s -type f -name '*.nhx'|sort" %args.nprdir[0])

    if args.generate_cmds: 
        for fname in iterfiles.split("\n"):
            fname = os.path.abspath(fname)
            infofile = fname.replace(".nhx", ".info")
            reportfile = fname.replace(".nhx", args.report_tag)
            info = dict(line.split("\t") for line in open(infofile))

            try:
                prev_data = open(reportfile).read()
            except Exception:
                pass
            else:
                if os.path.basename(fname) in prev_data:
                    continue

            #ABC = "--tax /users/tg/jhuerta/ABC/seqname2tax.txt --rf-only --ref /users/tg/jhuerta/ABC/ref_tree_fungi_jaime_taxIDs.nw  --tax2name /users/tg/jhuerta/ABC/tax2name.pkl --tax2track /users/tg/jhuerta/ABC/tax2track.pkl"
            ABC = "--tax name2tax --ref /users/tg/jhuerta/cytb_ncbi/ref_NCBI_for_2520cb.nw"
                    
            cmd = "python /users/tg/jhuerta/ncbi_taxa/ncbi_consensus.py -t %s -o %s %s" %(fname, reportfile, ABC)
            print cmd
            
    else:
        plotvalues = ["iternumber", "itername", "nseqs", "tree_seqtype",
                      "clean_alg_mean_ident", "alg_mean_ident", "subtrees", "ndups",
                      "broken_clades", "treemerger_out_match_dist",
                      "rf", "max_rf"]

        iter2info = {}
        iterations = []
        for fname in iterfiles.split("\n"):
            infofile = fname.replace(".nhx", ".info")
            if args.reportfile:
                reportfile = args.reportfile
            else:
                reportfile = fname.replace(".nhx", args.report_tag)
            itername = os.path.basename(fname)

            if os.path.exists(reportfile) and os.path.getsize(reportfile)>0:
                info = dict( map(strip, line.split("\t")) for line in open(infofile))
                #print '\n'.join(info.keys())
                for line in open(reportfile):
                    line = line.strip()

                    #print "[%s]" %line, len(line), reportfile
                    #if line == "":
                    #    print "NOP"
                    if not line or line.startswith("#"):
                        continue

                    #name, refname, subtrees, ndups, broken, broken_clades, rf, rf_med, rf_std, rf_max = map(strip, line.split("\t"))
                    name, refname, subtrees, ndups, broken, broken_clades, rf, rf_med, rf_std, rf_max = [0] * 10
                    name, kk1, kk2, kk3, rf, rf_max, size_avg, size_min = map(strip, line.split("\t"))
                    
                    if name.strip() == itername:
                        info["itername"] = name
                        info["rf"] = rf
                        info["subtrees"] = subtrees
                        info["ndups"] = ndups
                        info["broken_clades"] = broken_clades
                        info["rf_max"] = rf_max
                        info["rf_med"] = rf_med
                        info["rf_std"] = rf_std
                        
                        iter2info[itername] = info
                        iterations.append(itername)
                        #print '\t'.join(map(str, [info[key] for key in plotvalues]))
                       

        if args.branch_assembly:
            threads_file = os.path.join(args.nprdir[0], "threads")
            key = "rf"
            for line in open(threads_file):
                print '\t'.join([iter2info.get(i, {key: "NA"})[key] for i in line.strip().split(",")])

            clade2improve = {}

            for line in open(threads_file):
                prev = None
                for it in line.strip().split(","):
                    if prev: 
                        improve = float(iter2info[prev]["rf"]) - float(iter2info[it]["rf"])
                    else:
                        improve = 0
                    if it not in clade2improve:
                        clade2improve[iter2info[it]["cladeid"]] = improve
                    prev = it

            print '\n'.join(["%s\t%s" %(k,v)    for k,v in clade2improve.iteritems()])
        else:
            print '\t'.join(plotvalues)
            for i in iterations:
                print '\t'.join(map(str, [iter2info[i].get(key, "NA") for key in plotvalues]))




