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

__all__ = ["BionjModelChooser"]

class BionjModelChooser(Task):
    def __init__(self, cladeid, alg_file, args):
        self.alg_phylip_file = alg_file
        self.alg_basename = basename(self.alg_phylip_file)
        self.bin = args["_path"]
        base_args = {
            "--datatype": "aa",
            "--input": self.alg_basename,
            "--bootstrap": "0",
            "-o": "lr",
            "--model": None, # I will iterate over this value when
                             # creating jobs
            "--quiet": ""
            }

        Task.__init__(self, cladeid, "mchooser", "bionj_model_chooser", base_args, args)
        self.best_model = None

        self.seqtype = "aa"
        self.models = args["_models"]
        # Prepare jobs and task
        self.load_jobs()
        self.load_task_info()
        self.set_jobs_wd(self.taskdir)

        # Phyml cannot write the output in a different directory that
        # the original alg file. So I use relative path to alg file
        # for processes and I create a symlink for each of the
        # instances.
        for j in self.jobs:
            fake_alg_file = os.path.join(j.jobdir, self.alg_basename)
            if os.path.exists(fake_alg_file):
                os.remove(fake_alg_file)
            os.symlink(self.alg_phylip_file, fake_alg_file)

    def load_jobs(self):
        for m in self.models:
            args = self.args.copy()
            args["--model"] = m
            job = Job(self.bin, args)
            self.jobs.append(job)
        log.info(self.models)
    def finish(self):
        lks = []
        for j in self.jobs:
            tree_file = os.path.join(j.jobdir,
                                     self.alg_basename+"_phyml_tree.txt")
            stats_file = os.path.join(j.jobdir,
                                      self.alg_basename+"_phyml_stats.txt")
            tree = PhyloTree(tree_file)
            m = re.search('Log-likelihood:\s+(-?\d+\.\d+)',
                          open(stats_file).read())
            lk = float(m.groups()[0])
            tree.add_feature("lk", lk)
            tree.add_feature("model", j.args["--model"])
            lks.append([float(tree.lk), tree.model])
        lks.sort()
        lks.reverse()
        # choose the model with higher likelihood
        self.best_model = lks[-1][1]

    def check(self):
        if self.best_model != None:
            return True
        return False