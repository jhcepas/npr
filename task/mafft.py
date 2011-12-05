import os
import logging
log = logging.getLogger("main")

from .ordereddict import OrderedDict

from .master_task import Task
from .master_job import Job
from .utils import SeqGroup

__all__ = ["Mafft"]

class Mafft(Task):
    def __init__(self, cladeid, multiseq_file, seqtype, conf):
        self.conf = conf
        self.seqtype = seqtype
        self.nseqs = 0
        self.multiseq_file = multiseq_file
        # Mafft command needs ordered arguments. This is, input file
        # must be the last argument. Extra args come from config file
        # sections, which are already ordered. By using an OrderedDict
        # as a base of arguments, I keep such order and I can add the
        # input file at the last position.
        base_args = OrderedDict()
        # Initialize task
        Task.__init__(self, cladeid, "alg", "mafft", 
                      base_args, conf["mafft"])

        # Init task information, such as taskname, taskid, etc.
        self.init()

        # Set Task specific attributes
        main_job = self.jobs[0]
        self.alg_fasta_file = os.path.join(main_job.jobdir, "alg.fasta")
        self.alg_phylip_file = os.path.join(main_job.jobdir, "alg.iphylip")

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format. Both files, fasta and phylip,
        # remain accessible.
        alg = SeqGroup(self.jobs[0].stdout_file)
        self.nseqs = len(alg.id2seq)
        alg.write(outfile=self.alg_fasta_file, format="fasta")
        alg.write(outfile=self.alg_phylip_file, format="iphylip_relaxed")

    def load_jobs(self):
        args = self.args.copy()
        # Mafft redirects resulting alg to std.output. Order of
        # arguments is important, input file must be the last
        # one. Read above.
        args[""] = self.multiseq_file
        job = Job(self.conf["app"]["mafft"], args)
        self.jobs.append(job)

    def check(self):
        if os.path.exists(self.alg_fasta_file) and \
                os.path.exists(self.alg_phylip_file):
            return True
        return False
