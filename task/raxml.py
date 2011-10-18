import os
import sys
import logging
log = logging.getLogger("main")

from .master_task import Task
from .master_job import Job

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
        self.alg_file = alg_file
        self.model = model
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

    def load_jobs(self):
        tree_job = Job(self.bin, self.args)
        self.jobs.append(tree_job)

    def finish(self):
        # first job is the raxml tree
        tree_job = self.jobs[0]
        self.tree_file = os.path.join(tree_job.jobdir,
                                      "RAxML_bestTree."+self.cladeid)
    def check(self):
        if os.path.exists(self.tree_file) and PhyloTree(self.tree_file):
            return True
        return False
