import os
import logging
import shutil
log = logging.getLogger("main")

from .master_task import AlgTask
from .master_job import Job
from .utils import SeqGroup, OrderedDict
import __init__ as task

__all__ = ["MetaAligner"]

def seq_reverser_job(multiseq_file, outfile, trimal_bin):
    """ Returns a job reversing all sequences in MSF or MSA. """
    reversion_args = {"-in": multiseq_file,
                      "-out": outfile,
                      "-reverse": "",
                      "-fasta": "",
                      }
    job = Job(trimal_bin, reversion_args)
    return job

class MCoffee(AlgTask):
    def __init__(self, cladeid, seqtype, all_alg_files, conf):
        base_args = OrderedDict({
                "-output": "fasta",
                "-aln": ' '.join(all_alg_files)
                })
        # Initialize task
        AlgTask.__init__(self, cladeid, "alg", "Mcoffee", 
                      base_args, conf["meta_aligner"])

        self.conf = conf
        self.seqtype = seqtype
        self.alg_fasta_file = os.path.join(self.taskdir, "final_alg.fasta")
        self.alg_phylip_file = os.path.join(self.taskdir, "final_alg.iphylip")

        # Load task data
        self.init()

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format.
        alg = SeqGroup(os.path.join(self.jobs[0].jobdir, "alg.fasta"))
        alg.write(outfile=self.alg_fasta_file, format="fasta")
        alg.write(outfile=self.alg_phylip_file, format="iphylip_relaxed")

    def load_jobs(self):
        args = self.args.copy()
        args["-outfile"] = "alg.fasta"
        job = Job(self.conf["app"]["tcoffee"], args)
        self.jobs.append(job)

class MetaAligner(AlgTask):
    def __init__(self, cladeid, multiseq_file, seqtype, conf):
        # Initialize task
        AlgTask.__init__(self, cladeid, "alg", "Meta-Alg", 
                      OrderedDict(), conf["meta_aligner"])

        self.conf = conf
        self.seqtype = seqtype
        self.multiseq_file = multiseq_file
        self.alg_fasta_file = os.path.join(self.taskdir, "final_alg.fasta")
        self.alg_phylip_file = os.path.join(self.taskdir, "final_alg.iphylip")

        # Load task data
        self.init()

    def load_jobs(self):
        multiseq_file_r = self.multiseq_file+".reversed"
        first = seq_reverser_job(self.multiseq_file, multiseq_file_r, 
                                          self.conf["app"]["readal"])
        self.jobs.append(first)
        all_alg_files = []
        for alg in self.conf["meta_aligner"]["_aligners"]:
            _aligner = getattr(task, alg)

            # Normal alg
            task1 = _aligner(self.cladeid, self.multiseq_file, self.seqtype,
                             self.conf)
            self.jobs.append(task1)
            all_alg_files.append(task1.alg_fasta_file)

            # Alg of the reverse
            task2 = _aligner(self.cladeid, multiseq_file_r, self.seqtype,
                             self.conf)
            task2.dependencies.add(first)
            self.jobs.append(task2)

           
            # Restore reverse alg
            task3 = seq_reverser_job(task2.alg_fasta_file,
                                     task2.alg_fasta_file+".reverse", 
                                     self.conf["app"]["readal"])
            task3.dependencies.add(task2)
            self.jobs.append(task3)
            all_alg_files.append(task2.alg_fasta_file+".reverse")

        # Combine signal from all algs using Mcoffee
        self.final_task = MCoffee(self.cladeid, self.seqtype, all_alg_files,
                             self.conf)
        self.final_task.dependencies.update(self.jobs)
        self.jobs.append(self.final_task)
        
    def finish(self):
        shutil.copy(self.final_task.alg_fasta_file, self.alg_fasta_file)
        shutil.copy(self.final_task.alg_fasta_file, self.alg_phylip_file)

