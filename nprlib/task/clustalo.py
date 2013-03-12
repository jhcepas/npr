import os
import sys
import logging
log = logging.getLogger("main")

from nprlib.master_task import AlgTask
from nprlib.master_job import Job

from nprlib.utils import read_fasta, OrderedDict, GLOBALS, CLUSTALO_CITE

__all__ = ["Clustalo"]

class Clustalo(AlgTask):
    def __init__(self, nodeid, multiseq_file, seqtype, conf, confname):
       
        GLOBALS["citator"].add(CLUSTALO_CITE)
        
        if seqtype != "aa":
            raise ValueError("Clustal Omega does only support nt seqtype")
        
        base_args = OrderedDict({
                '-i': None,
                '-o': None,
                '--outfmt': "fa",
                })
        self.confname = confname
        self.conf = conf
        # Initialize task
        AlgTask.__init__(self, nodeid, "alg", "Clustal-Omega", 
                      base_args, self.conf[self.confname])


        self.seqtype = "aa" # only aa supported
        self.multiseq_file = multiseq_file

        self.init()
        self.alg_fasta_file = os.path.join(self.taskdir, "final_alg.fasta")
        self.alg_phylip_file = os.path.join(self.taskdir, "final_alg.iphylip")

    def load_jobs(self):
        appname = self.conf[self.confname]["_app"]
        # Only one Muscle job is necessary to run this task
        args = OrderedDict(self.args)
        args["-i"] = self.multiseq_file
        args["-o"] = "alg.fasta"
        job = Job(self.conf["app"][appname], args, parent_ids=[self.nodeid])
        self.jobs.append(job)

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format.
        alg_file = os.path.join(self.jobs[0].jobdir, "alg.fasta")
        # ClustalO returns a tricky fasta file
        alg = read_fasta(alg_file, header_delimiter=" ")
        alg.write(outfile=self.alg_fasta_file, format="fasta")
        alg.write(outfile=self.alg_phylip_file, format="iphylip_relaxed")
        AlgTask.finish(self)
