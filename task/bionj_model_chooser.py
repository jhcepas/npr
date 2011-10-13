import os
import sys
import re

import logging
log = logging.getLogger("main")

from .config import *
from .master_task import Task
from .master_job import Job
from .utils import basename 

sys.path.insert(0, "/home/jhuerta/_Devel/ete/2.2/")
from ete_dev import PhyloTree

__all__ = ["BionjModelChooserTask"]

class BionjModelChooserTask(Task):
    def __init__(self, cladeid, alg_file):
        Task.__init__(self, cladeid, "mchooser", "model_chooser")
        self.best_model = None
        self.alg_file = alg_file
        self.seqtype = "aa"
        self.alg_basename = basename(self.alg_file)
        self.models = ["JTT", "DcMut"]#, "Blosum62", "MtRev"]
        # Arguments used to start phyml jobs. Note that models is a
        # list, so the dictionary will be used to submit several
        # phyml_jobs
        self.args = {
            "--datatype": "aa",
            "--input": self.alg_basename,
            "--bootstrap": "0",
            "-f": "m", # char freq (m)odel or (e)stimated
            "--pinv": "e",
            "--alpha": "e",
            "-o": "lr",
            "--nclasses": "4",
            "--model": None, # I will iterate over this value when
                            # creating jobs
            "--quiet": "" }

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

            os.symlink(self.alg_file, fake_alg_file)

    def load_jobs(self):
        for m in self.models:
            args = self.args.copy()
            args["--model"] = m
            job = Job(PHYML_BIN, args)
            self.jobs.append(job)

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
