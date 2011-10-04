import os
import sys
import logging
log = logging.getLogger("main")

from .config import *
from .master_task import Task
from .master_job import Job

__all__ = ["ClustalOmegaAlgTask"]

class ClustalOmegaAlgTask(Task):
    def __init__(self, cladeid, multiseq_file):
        # Initialize task
        Task.__init__(self, cladeid, "alg", "clustal_omega_alg")

        # Arguments and options used to executed the associated muscle
        # jobs. This will identify different Tasks of the same type
        self.multiseq_file = multiseq_file
        self.args = {
            '-i': None,
            '-o': None,
            '-v': "",
            '--threads': "1", 
            '--outfmt': "fa",
            }

        # Prepare required jobs
        self.load_jobs()

        # Set task information, such as task working dir and taskid
        self.load_task_info()

        # Set the working dir for all jobs
        self.set_jobs_wd(self.taskdir)

        # Set Task specific attributes
        main_job = self.jobs[0]
        self.alg_fasta_file = os.path.join(main_job.jobdir, "alg.fasta")
        self.alg_phylip_file = os.path.join(main_job.jobdir, "alg.iphylip")

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format. Both files, fasta and phylip,
        # remain accessible.
        alg = fasta.read_fasta(self.alg_fasta_file, header_delimiter=" ")
        alg.write(outfile=self.alg_phylip_file, format="iphylip_relaxed")

    def load_jobs(self):
        # Only one Muscle job is necessary to run this task
        args = self.args.copy()
        args["-i"] = self.multiseq_file
        args["-o"] = "alg.fasta"
        job = Job(OCLUSTAL_BIN, args)
        self.jobs.append(job)

    def check(self):
        if os.path.exists(self.alg_fasta_file) and \
                os.path.exists(self.alg_phylip_file):
            return True
        return False
