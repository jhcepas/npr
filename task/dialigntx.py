import os
import logging
log = logging.getLogger("main")

from .master_task import Task
from .master_job import Job
from .utils import SeqGroup, OrderedDict

__all__ = ["Dialigntx"]

class Dialigntx(Task):
    def __init__(self, cladeid, multiseq_file, seqtype, conf):
        self.conf = conf
        self.seqtype = seqtype
        self.multiseq_file = multiseq_file
        self.nseqs = 0
        self.alg_fasta_file = "alg.fasta"
        self.alg_phylip_file = "alg.iphylip"

        # fixed options for running this task
        base_args = OrderedDict({
                '': None,
            })
        # Initialize task
        Task.__init__(self, cladeid, "alg", "dialigntx", 
                      base_args, conf["dialigntx"])

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
        args[''] = "%s %s" %(self.multiseq_file, self.alg_fasta_file)
        job = Job(self.conf["app"]["dialigntx"], args)
        self.jobs.append(job)

    def check(self):
        if os.path.exists(self.alg_fasta_file) and \
                os.path.exists(self.alg_phylip_file):
            return True
        return False
