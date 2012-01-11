import os
import logging
log = logging.getLogger("main")

from .master_task import AlgTask
from .master_job import Job
from .utils import SeqGroup, OrderedDict

__all__ = ["Dialigntx"]

class Dialigntx(AlgTask):
    def __init__(self, cladeid, multiseq_file, seqtype, conf):
        # fixed options for running this task
        base_args = OrderedDict({
                '': None,
                })
        # Initialize task
        AlgTask.__init__(self, cladeid, "alg", "DialignTX", 
                      base_args, conf["dialigntx"])
        
        self.conf = conf
        self.seqtype = seqtype
        self.multiseq_file = multiseq_file
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
        # Only one Muscle job is necessary to run this task
        args = self.args.copy()
        args[''] = "%s %s" %(self.multiseq_file, "alg.fasta")
        job = Job(self.conf["app"]["dialigntx"], args)
        self.jobs.append(job)