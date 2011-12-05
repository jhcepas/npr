import os
import logging
log = logging.getLogger("main")

from .master_task import Task
from .master_job import Job
from .utils import SeqGroup

__all__ = ["Muscle"]

class Muscle(Task):
    def __init__(self, cladeid, multiseq_file, seqtype, conf):
        self.conf = conf
        self.seqtype = seqtype
        self.multiseq_file = multiseq_file
        self.nseqs = 0
        # fixed options for running this task
        base_args = {
            '-in': None,
            '-out': None,
            }
        # Initialize task
        Task.__init__(self, cladeid, "alg", "muscle", 
                      base_args, conf["muscle"])

        # Load task data
        self.init()

        # Set Task specific attributes
        main_job = self.jobs[0]
        self.alg_fasta_file = os.path.join(main_job.jobdir, "alg.fasta")
        self.alg_phylip_file = os.path.join(main_job.jobdir, "alg.iphylip")

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format. Both files, fasta and phylip,
        # remain accessible.
        alg = SeqGroup(self.alg_fasta_file)
        self.nseqs = len(alg.id2seq)
        alg.write(outfile=self.alg_phylip_file, format="iphylip_relaxed")

    def load_jobs(self):
        # Only one Muscle job is necessary to run this task
        args = self.args.copy()
        args["-in"] = self.multiseq_file
        args["-out"] = "alg.fasta"
        job = Job(self.conf["app"]["muscle"], args)
        self.jobs.append(job)

    def check(self):
        if os.path.exists(self.alg_fasta_file) and \
                os.path.exists(self.alg_phylip_file):
            return True
        return False
