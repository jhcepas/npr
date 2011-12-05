import os
import logging
log = logging.getLogger("main")

from .master_task import Task
from .master_job import Job
from .utils import SeqGroup
import .task 

__all__ = ["MetaAligner"]

# Convert and Reverse 
# Creates a Task for each aligner. 
# Execute
# Restore the reversed alignments
# Creates an MCoffee task and execute
# Trimal selection of columns based on all the alignments

class AlgReverser(Task):
    def __init__(self, cladeid, multiseq_file, seqtype):
        Task.__init__(self, cladeid, "utils", "reverse-alg")

        # Set task options
        self.seqtype = seqtype
        self.multiseq_file = multiseq_file
        self.multiseq_file_r = multiseq_file+".reverse"
        # Load task data
        self.init()

    def load_jobs(self):
        reversion_args = {"-in": self.multiseq_file,
                          "-out": self.multiseq_file_r,
                          "-reverse",
                          "-fasta",
                          }
        job = Job(self.bin_trimal, reversion_args)
        self.jobs.append(job)

    def check(self):
        try:
            SeqGroup(self.multiseq_file_r)
        except:
            return False
        else:
            return True

class MCoffee(Task):
    def __init__(self, cladeid, multiseq_file, seqtype, args):
        base_args = OrderedDict({
                "-n_core": 1, 
                "-output": fasta

                })
        Task.__init__(self, cladeid, "utils", "reverse-alg", base_args, args)

        # Set task options
        self.seqtype = seqtype
        self.multiseq_file = multiseq_file
        self.multiseq_file_r = multiseq_file+".reverse"
        # Load task data
        self.init()
        
    def finish(self):
        pass

    def load_jobs(self):
        args = self.args.copy()
        args[""] = self.multiseq_file
        args[""]
        job = Job(self.bin_trimal, args)
        self.jobs.append(job)

    def check(self):
        try:
            SeqGroup(self.multiseq_file_r)
        except:
            return False
        else:
            return True


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
                      base_args, conf["meta_aligner"])
        # Load task data
        self.init()

        # Set Task specific attributes
        main_job = self.jobs[0]
        self.alg_fasta_file = os.path.join(main_job.jobdir, "alg.fasta")
        self.alg_phylip_file = os.path.join(main_job.jobdir, "alg.iphylip")
        self.sub_tasks

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format. Both files, fasta and phylip,
        # remain accessible.
        alg = SeqGroup(self.alg_fasta_file)
        alg.write(outfile=self.alg_phylip_file, format="iphylip_relaxed")

    def load_jobs(self):

        AlgReverser(self.cladeid, self.multiseq_file_r)
        m = Muscle(self.cladeid, self.multiseq_file, "aa", config["muscle"])
        m_r = Muscle(self.cladeid, self.multiseq_file_r, "aa", config["muscle"])
        Mafft(self.cladeid, self.multiseq_file, "aa", config["mafft"])
        Mafft(self.cladeid, self.multiseq_file_r, "aa", config["mafft"])
        AlgReverser(self.cladeid, self.muscle_r.alg_fasta_file)
        AlgReverser(self.cladeid, self.mafft_r.alg_fasta_file)

        MCoffee(self.cladeid, self.multiseq_file, )


        for n in self.config["metaaligner"]["aligners"]:
            if n in self.config and n in appbindings:
                appbindding[n](cladeid, self.multi)

            self.multiseq_file
            self.multiseq_file+".reverse"
            job = Job(bin)
            job = Job(bin)

    def check(self):
        if os.path.exists(self.alg_fasta_file) and \
                os.path.exists(self.alg_phylip_file):
            return True
        return False
