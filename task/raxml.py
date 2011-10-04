import os
import sys
import logging
log = logging.getLogger("main")

from .config import *
from .master_task import Task
from .master_job import Job

sys.path.insert(0, "/home/jhuerta/_Devel/ete/2.2/")
from ete_dev import PhyloTree

__all__ = ["RaxmlTreeTask"]

class RaxmlTreeTask(Task):
    def __init__(self, cladeid, alg_file, model):
        Task.__init__(self, cladeid, "tree", "raxml_tree")
        # set app arguments and options
        self.alg_file = alg_file
        seqtype = "PROT"
        cpus = 2
        partitions_file = None
        self.args = {
            '-f': "d", # Normal ML algorithm
            '-T': '%d' %cpus,
            '-m': '%sGAMMA%s' %(seqtype, model.upper()),
            '-s': self.alg_file,
            '-n': self.cladeid,
            '-q': partitions_file,
            }

        self.load_jobs()
        self.load_task_info()
        self.set_jobs_wd(self.taskdir)

    def load_jobs(self):
        tree_job = Job(RAXML_BIN, self.args)
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
