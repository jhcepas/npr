import os
import sys
import re

import logging
log = logging.getLogger("main")

from .master_task import Task
from .master_job import Job
from .utils import basename, PhyloTree

__all__ = ["Phyml"]

class Phyml(Task):
    def __init__(self, cladeid, alg_file, model, seqtype, conf):
        self.conf = conf
        self.alg_phylip_file = alg_file
        self.alg_basename = basename(self.alg_phylip_file)
        self.seqtype = seqtype
        self.model = model 
        self.lk = None

        base_args = {
            "--model": model, 
            "--datatype": seqtype,
            "--input": self.alg_basename,
            "--no_memory_check": "", 
            "--quiet": "" }

        Task.__init__(self, cladeid, "tree", "phyml", 
                      base_args, conf["phyml"])

        # Prepare jobs and task
        self.init()
        
        # Phyml cannot write the output in a different directory that
        # the original alg file. So I use relative path to alg file
        # for processes and I create a symlink for each of the
        # instances.
        j = self.jobs[0]
        fake_alg_file = os.path.join(j.jobdir, self.alg_basename)
        if os.path.exists(fake_alg_file):
            os.remove(fake_alg_file)
        os.symlink(self.alg_phylip_file, fake_alg_file)

    def load_jobs(self):
        args = self.args.copy()
        job = Job(self.conf["app"]["phyml"], args)
        self.jobs.append(job)

    def finish(self):
        lks = []
        j = self.jobs[0]
        tree_file = os.path.join(j.jobdir,
                                 self.alg_basename+"_phyml_tree.txt")
        stats_file = os.path.join(j.jobdir,
                                  self.alg_basename+"_phyml_stats.txt")

        m = re.search('Log-likelihood:\s+(-?\d+\.\d+)',
                      open(stats_file).read())
        lk = float(m.groups()[0])
        self.lk =  lk
        self.tree_file = os.path.join(j.jobdir,
                                      "phyml_tree."+self.cladeid)
        tree = PhyloTree(tree_file)        
        tree.write(outfile=self.tree_file)

    def check(self):
        try: 
            t = PhyloTree(self.tree_file)
        except Exception, e: 
            log.error(e)
            return False
        else:
            return True
        
