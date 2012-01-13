import os
import sys
import logging
log = logging.getLogger("main")

from .master_task import AlgCleanerTask
from .master_job import Job
from .utils import SeqGroup

__all__ = ["Trimal"]

class Trimal(AlgCleanerTask):
    def __init__(self, cladeid, seqtype, alg_fasta_file, alg_phylip_file, conf):
        self.conf = conf
        self.seqtype = seqtype
        self.alg_fasta_file = alg_fasta_file
        self.alg_phylip_file = alg_phylip_file
        self.kept_columns = []
        base_args = {
            '-in': None,
            '-out': None,
            '-fasta': "", 
            '-colnumbering': "", 
            }
        # Initialize task
        AlgCleanerTask.__init__(self, cladeid, "acleaner", "Trimal", 
                      base_args, conf["trimal"])

        self.init()
        
        # Set Task specific attributes
        main_job = self.jobs[0]
        self.clean_alg_fasta_file = os.path.join(main_job.jobdir, "clean.alg.fasta")
        self.clean_alg_phylip_file = os.path.join(main_job.jobdir, "clean.alg.iphylip")

    def load_jobs(self):
        args = self.args.copy()
        args["-in"] = self.alg_fasta_file
        args["-out"] = "clean.alg.fasta"
        job = Job(self.conf["app"]["trimal"], args)
        self.jobs.append(job)

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format. Both files, fasta and phylip,
        # remain accessible.
        alg = SeqGroup(self.clean_alg_fasta_file)
        for line in open(self.jobs[0].stdout_file):
            line = line.strip()
            if line.startswith("#ColumnsMap"):
                self.kept_columns = map(int, line.split("\t")[1].split(","))
        alg.write(outfile=self.clean_alg_phylip_file, format="iphylip_relaxed")
        AlgCleanerTask.finish(self)
