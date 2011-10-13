import os
import sys
import logging
log = logging.getLogger("main")

from .config import *
from .master_task import Task
from .master_job import Job

sys.path.insert(0, "/home/jhuerta/_Devel/ete/2.2/")
from ete_dev import SeqGroup

__all__ = ["TrimalTask"]

class TrimalTask(Task):
    def __init__(self, cladeid, alg_file, seqtype):
        # Initialize task
        Task.__init__(self, cladeid, "acleaner", "trimal_cleaner")

        # Arguments and options used to executed the associated muscle
        # jobs. This will identify different Tasks of the same type
        self.seqtype = seqtype
        self.alg_file = alg_file
        self.args = {
            '-in': None,
            '-out': None,
            '-fasta': "", 
            '-gt': "0.1",
            }

        # Prepare required jobs
        self.load_jobs()

        # Set task information, such as task working dir and taskid
        self.load_task_info()

        # Set the working dir for all jobs
        self.set_jobs_wd(self.taskdir)

        # Set Task specific attributes
        main_job = self.jobs[0]
        self.clean_alg_fasta_file = os.path.join(main_job.jobdir, "clean.alg.fasta")
        self.clean_alg_phylip_file = os.path.join(main_job.jobdir, "clean.alg.iphylip")

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format. Both files, fasta and phylip,
        # remain accessible.
        alg = SeqGroup(self.clean_alg_fasta_file)
        alg.write(outfile=self.clean_alg_phylip_file, format="iphylip_relaxed")

    def load_jobs(self):
        args = self.args.copy()
        args["-in"] = self.alg_file
        args["-out"] = "clean.alg.fasta"
        job = Job(TRIMAL_BIN, args)
        self.jobs.append(job)

    def check(self):
        if os.path.exists(self.clean_alg_fasta_file) and \
                os.path.exists(self.clean_alg_phylip_file):
            return True
        return False
