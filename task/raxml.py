import os
import sys
import logging
import re

log = logging.getLogger("main")

from .master_task import TreeTask
from .master_job import Job
from .utils import basename, PhyloTree, OrderedDict

__all__ = ["Raxml"]

class Raxml(TreeTask):
    def __init__(self, cladeid, alg_file, model, seqtype, conf):

        TreeTask.__init__(self, cladeid, "tree", "RaxML", 
                      OrderedDict(), conf["raxml"])

        self.conf = conf
        self.seqtype = seqtype
        self.alg_phylip_file = alg_file
        self.compute_alrt = conf["raxml"].get("_alrt_calculation", None)
        # Process raxml options
        model = model or conf["raxml"]["_aa_model"]
        method = conf["raxml"].get("method", "GAMMA").upper()
        if seqtype.lower() == "aa":
            self.model_string =  'PROT%s%s' %(method, model.upper())
            self.model = model 
        elif seqtype.lower() == "nt":
            self.model_string =  'GTR%s' %method
            self.model = "GTR"
        else:
            raise ValueError("Unknown seqtype %s", seqtype)
        #inv = conf["raxml"].get("pinv", "").upper()
        #freq = conf["raxml"].get("ebf", "").upper()

        self.init()

        self.ml_tree_file = os.path.join(self.jobs[0].jobdir,
                                      "RAxML_bestTree." + self.cladeid)
        if self.compute_alrt == "raxml":
            self.jobs[1].args["-t"] = self.ml_tree_file
            self.alrt_tree_file = os.path.join(self.jobs[1].jobdir,
                                               "RAxML_fastTreeSH_Support." +\
                                                   self.cladeid)

        elif self.compute_alrt == "phyml":
            fake_alg_file = os.path.join(self.jobs[1].jobdir, basename(self.alg_phylip_file))
            if os.path.exists(fake_alg_file):
                os.remove(fake_alg_file)
            os.symlink(self.alg_phylip_file, fake_alg_file)
            self.jobs[1].args["-u"] = self.ml_tree_file
            self.alrt_tree_file = os.path.join(self.jobs[1].jobdir,
                                               basename(self.alg_phylip_file) +"_phyml_tree.txt")

    def load_jobs(self):
        args = self.args.copy()
        args["-s"] = self.alg_phylip_file
        args["-m"] = self.model_string
        args["-n"] = self.cladeid
        tree_job = Job(self.conf["app"]["raxml"], args)
        self.jobs.append(tree_job)

        if self.compute_alrt == "raxml":
            alrt_args = {
                "-f": "J",
                "-t": None,
                "-T": args.get("-T", "1"),
                "-m": args["-m"],
                "-n": args["-n"],
                "-s": args["-s"],
                }
            alrt_job = Job(self.conf["app"]["raxml"], alrt_args)       
            alrt_job.dependencies.add(tree_job)
            self.jobs.append(alrt_job)

        elif self.compute_alrt == "phyml":
            alrt_args = {
                "-o": "n",
                "--bootstrap": "-2",
                "-d": self.seqtype,
                "-u": None,
                "--model": self.model,
                "--input": basename(self.alg_phylip_file), 
                "--quiet": "",
                "--no_memory_check": "",
                }

            alrt_job = Job(self.conf["app"]["phyml"], alrt_args)       
            alrt_job.dependencies.add(tree_job)
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
