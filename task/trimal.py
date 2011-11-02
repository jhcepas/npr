import os
import sys
import logging
log = logging.getLogger("main")

from .master_task import Task
from .master_job import Job

sys.path.insert(0, "/home/jhuerta/_Devel/ete/2.2/")
from ete_dev import SeqGroup

__all__ = ["Trimal"]

class Trimal(Task):
    def __init__(self, cladeid, alg_fasta_file, alg_phylip_file, seqtype, args):
        self.seqtype = seqtype
        self.alg_fasta_file = alg_fasta_file
        self.alg_phylip_file = alg_phylip_file
        self.bin = args["_path"]
        self.kept_columns = []
        self.nseqs = 0
        base_args = {
            '-in': None,
            '-out': None,
            '-fasta': "", 
            '-colnumbering': "", 
            }
        # Initialize task
        Task.__init__(self, cladeid, "acleaner", "trimal", 
                      base_args, args)

        # Load task data
        self.init()
        
        # Set Task specific attributes
        main_job = self.jobs[0]
        self.clean_alg_fasta_file = os.path.join(main_job.jobdir, "clean.alg.fasta")
        self.clean_alg_phylip_file = os.path.join(main_job.jobdir, "clean.alg.iphylip")

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format. Both files, fasta and phylip,
        # remain accessible.
        alg = SeqGroup(self.clean_alg_fasta_file)
        self.nseqs = len(alg.id2seq)
        for line in open(self.jobs[0].stdout_file):
            line = line.strip()
            if line.startswith("#ColumnsMap"):
                self.kept_columns = map(int, line.split("\t")[1].split(","))
        alg.write(outfile=self.clean_alg_phylip_file, format="iphylip_relaxed")

    def load_jobs(self):
        args = self.args.copy()
        args["-in"] = self.alg_fasta_file
        args["-out"] = "clean.alg.fasta"
        job = Job(self.bin, args)
        self.jobs.append(job)

    def check(self):
        if os.path.exists(self.clean_alg_fasta_file) and \
                os.path.exists(self.clean_alg_phylip_file):
            return True
        return False
