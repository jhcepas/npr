import os
import sys
import logging
log = logging.getLogger("main")

from .master_task import Task
from .master_job import Job

from .utils import read_fasta

__all__ = ["Clustalo"]

class Clustalo(Task):
    def __init__(self, cladeid, multiseq_file, seqtype, conf):
        if seqtype != "aa":
            raise Exception("Clustal Omega does only support aa seqtype")
        self.seqtype = "aa" # only aa supported
        self.multiseq_file = multiseq_file
        self.conf = conf
        self.nseqs = 0
        base_args = {
            '-i': None,
            '-o': None,
            '--outfmt': "fa",
            }
        # Initialize task
        Task.__init__(self, cladeid, "alg", "clustal_omega", 
                      base_args, conf["clustalo"])

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
        alg = read_fasta(self.alg_fasta_file, header_delimiter=" ")
        self.nseqs = len(alg.id2seq)
        alg.write(outfile=self.alg_phylip_file, format="iphylip_relaxed")

    def load_jobs(self):
        # Only one Muscle job is necessary to run this task
        args = self.args.copy()
        args["-i"] = self.multiseq_file
        args["-o"] = "alg.fasta"
        job = Job(self.conf["app"]["clustalo"], args)
        self.jobs.append(job)

    def check(self):
        if os.path.exists(self.alg_fasta_file) and \
                os.path.exists(self.alg_phylip_file):
            return True
        return False
