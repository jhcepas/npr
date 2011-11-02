import os
import sys
import logging
import re

log = logging.getLogger("main")

from .master_task import Task
from .master_job import Job
from .utils import basename

sys.path.insert(0, "/home/jhuerta/_Devel/ete/2.2/")
from ete_dev import PhyloTree

__all__ = ["Raxml"]

class Raxml(Task):
    def __init__(self, cladeid, alg_file, model, seqtype, args):
        method = args.get("method", "GAMMA").upper()
        inv = args.get("pinv", "").upper()
        freq = args.get("ebf", "").upper()
        # set app arguments and options
        self.bin = args["_path"]
        self.phyml_bin = args["_phyml_bin"]
        self.alg_file = alg_file
        self.model = model
        self.compute_alrt = True
        self.seqtype = seqtype
        if self.seqtype.lower() == "aa":
            model_string =  'PROT%s%s' %(method, self.model.upper())
        elif self.seqtype.lower() == "nt":
            model_string =  'GTR%s' %method
        else:
            raise ValueError("Unknown seqtype %s", seqtype)
        base_args = {
            '-m': model_string,
            '-s': alg_file,
            '-n': cladeid,
            }
        Task.__init__(self, cladeid, "tree", "raxml", base_args, args)

        # Load task info
        self.init()

        self.ml_tree_file = os.path.join(self.jobs[0].jobdir,
                                      "RAxML_bestTree." + self.cladeid)
        if self.compute_alrt:
            self.jobs[1].args["-t"] = self.ml_tree_file
            self.alrt_tree_file = os.path.join(self.jobs[1].jobdir,
                                               "RAxML_fastTreeSH_Support." +\
                                                   self.cladeid)


            fake_alg_file = os.path.join(self.jobs[2].jobdir, basename(self.alg_file))
            if os.path.exists(fake_alg_file):
                os.remove(fake_alg_file)
            os.symlink(self.alg_file, fake_alg_file)
            
            self.jobs[2].args["-u"] = self.ml_tree_file
            self.alrt_tree_file = os.path.join(self.jobs[2].jobdir,
                                               basename(self.alg_file) +"_phyml_tree.txt")

    def load_jobs(self):
        tree_job = Job(self.bin, self.args)
        self.jobs.append(tree_job)
        if self.compute_alrt:
            alrt_args = {
                "-f": "J",
                "-t": None,
                "-T": self.args.get("-T", "1"),
                "-m": self.args["-m"],
                "-n": self.cladeid,
                "-s": self.args["-s"],
                }
            alrt_job = Job(self.bin, alrt_args)       
            self.jobs.append(alrt_job)


            alrt_args = {
                "-o": "n",
                "--bootstrap": "-2",
                "-d": self.seqtype,
                "-u": None,
                "--model": self.model,
                "--input": basename(self.alg_file), 
                "--quiet": "",
                "--no_memory_check": "",
                }

            alrt_job = Job(self.phyml_bin, alrt_args)       
            self.jobs.append(alrt_job)

    def finish(self):
        #first job is the raxml tree
        def parse_alrt(match):
            dist = match.groups()[0]
            support = float(match.groups()[1])/100.0
            return "%g:%s" %(support, dist)
         
        if self.compute_alrt:
            tree = open(self.alrt_tree_file).read().replace("\n", "")
            nw = re.subn(":(\d+\.\d+)\[(\d+)\]", parse_alrt, tree, re.MULTILINE)
            
            open(self.alrt_tree_file+".parsed", "w").write(nw[0])

        if self.compute_alrt:
            self.tree_file = self.alrt_tree_file
        else:
            self.tree_file = self.ml_tree_file

    def check(self):
        if os.path.exists(self.tree_file) and PhyloTree(self.tree_file):
            return True
        return False
