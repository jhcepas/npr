import os
import sys
import re

import logging
log = logging.getLogger("main")

from .master_task import Task
from .master_job import Job
from .utils import basename 

sys.path.insert(0, "/home/jhuerta/_Devel/ete/2.2/")
from ete_dev import PhyloTree

__all__ = ["JModeltest"]

class JModeltest(Task):
    def __init__(self, cladeid, alg_fasta_file, alg_phylip_file, args):
        base_args = {
            '-d': alg_fasta_file, 
            }
        Task.__init__(self, cladeid, "tree", "jmodeltest", base_args, args)
        # set app arguments and options
        self.bin = args["_path"]
        self.alg_fasta_file = alg_fasta_file
        self.alg_phylip_file = alg_phylip_file
        self.seqtype = "nt"
        self.best_model = None

        # Load task data
        self.init()

    def load_jobs(self):
        tree_job = Job(self.bin, self.args)
        self.jobs.append(tree_job)

    def finish(self):
        # first job is the raxml tree
        for line in open(self.jobs[-1].stdout_file, "rU"):
            t = None
            best_model = None
            best_model_in_next_line = False
            if best_model_in_next_line:
                best_model = line.split("=")[1].strip()
                best_model_in_next_line = False
            elif line.strip() == "Model selected:":
                best_model_in_next_line = True
            elif line.startswith("ML tree (NNI) for the best AIC model ="): 
                nw = line.replace("ML tree (NNI) for the best AIC model =", "")
                t = PhyloTree(nw)
                break
        if t: 
            tree_job = self.jobs[-1]
            self.tree_file = os.path.join(tree_job.jobdir,
            "jModelTest_tree."+self.cladeid)
            t.write(outfile=self.tree_file)
            self.model = best_model
        else: 
            raise Exception("jModeltest failed!")

    def check(self):
        if os.path.exists(self.tree_file) and PhyloTree(self.tree_file):
            return True
        return False
