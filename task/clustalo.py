import os
import sys
import logging
log = logging.getLogger("main")

from .master_task import Task
from .master_job import Job

__all__ = ["Clustalo"]

class Clustalo(Task):
    def __init__(self, cladeid, multiseq_file, args):
        self.seqtype = "aa" # only aa supported
        self.multiseq_file = multiseq_file
        self.bin = args["_path"]
        base_args = {
            '-i': None,
            '-o': None,
            '--outfmt': "fa",
            }
        # Initialize task
        Task.__init__(self, cladeid, "alg", "clustal_omega", base_args, args)

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
