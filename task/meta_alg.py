import os
import logging
log = logging.getLogger("main")

from .master_task import Task
from .master_job import Job
from .utils import SeqGroup, OrderedDict
from . import *

__all__ = ["MetaAligner"]

class MCoffee(Task):
    def __init__(self, cladeid, seqtype, all_alg_files, conf):
        self.conf = conf
        self.seqtype = seqtype
        self.alg_fasta_file =  "alg.fasta"
        self.alg_phylip_file = "alg.iphylip"

        base_args = {
            "-output": "fasta",
            "-aln": ' '.join(all_alg_files)
            }
        
        # Initialize task
        Task.__init__(self, cladeid, "alg", "mcoffee", 
                      base_args, self.conf["meta_aligner"])

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
        alg.write(outfile=self.alg_phylip_file, format="iphylip_relaxed")

    def load_jobs(self):
        args = self.args.copy()
        args["-outfile"] = self.alg_fasta_file
        job = Job(self.conf["app"]["tcoffee"], args)
        self.jobs.append(job)

    def check(self):
        if os.path.exists(self.alg_fasta_file) and \
                os.path.exists(self.alg_phylip_file):
            return True
        return False

def seq_reverser_job(multiseq_file, outfile, trimal_bin):
    reversion_args = {"-in": multiseq_file,
                      "-out": outfile,
                      "-reverse": "",
                      "-fasta": "",
                      }
    job = Job(trimal_bin, reversion_args)
    return job


class MetaAligner(Task):
    def __init__(self, cladeid, multiseq_file, seqtype, conf):
        self.conf = conf
        self.seqtype = seqtype
        self.multiseq_file = multiseq_file
        # fixed options for running this task
        base_args = {
            }
        # Initialize task
        Task.__init__(self, cladeid, "alg", "meta-alg", 
                      base_args, self.conf["meta_aligner"])

        # Load task data
        self.init()

        # Set Task specific attributes
        main_job = self.jobs[0]
        self.alg_fasta_file = os.path.join(main_job.jobdir, "alg.fasta")
        self.alg_phylip_file = os.path.join(main_job.jobdir, "alg.iphylip")

    def load_jobs(self):
        multiseq_file_r = self.multiseq_file+".reversed"
        self.jobs.append(seq_reverser_job(self.multiseq_file, multiseq_file_r, 
                                          self.conf["app"]["readal"]))
        all_alg_files = []
        for alg in self.conf["meta_aligner"]["_aligners"]:
            _aligner = Muscle

            # Normal alg
            task1 = _aligner(self.cladeid, self.multiseq_file, "aa",
                             self.conf)
            self.jobs.append(task1)
            all_alg_files.append(task1.alg_fasta_file)

            # Alg of the reverse
            task2 = _aligner(self.cladeid, multiseq_file_r, "aa",
                             self.conf)
            self.jobs.append(task2)

            # Restore reverse alg
            self.jobs.append(seq_reverser_job(task2.alg_fasta_file,
                                              task2.alg_fasta_file+".reverse", 
                                              self.conf["app"]["readal"]))
            all_alg_files.append(task2.alg_fasta_file+".reverse")


        # Combine signal from all algs using Mcoffee

        self.final_task = MCoffee(self.cladeid,"aa", all_alg_files,
                             self.conf)
        self.jobs.append(self.final_task)
        
    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format. Both files, fasta and phylip,
        # remain accessible.
        self.alg_fasta_file = self.final_task.alg_fasta_file
        self.alg_phylip_file = self.final_task.alg_phylip_file
        return 

    def check(self):
        return True
