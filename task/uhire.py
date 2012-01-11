import os
import logging
log = logging.getLogger("main")

from .master_task import AlgTask
from .master_job import Job
from .utils import SeqGroup, OrderedDict

__all__ = ["Uhire"]

class Uhire(AlgTask):
    def __init__(self, cladeid, multiseq_file, seqtype, conf):
        # Initialize task
        AlgTask.__init__(self, cladeid, "alg", "Usearch-Uhire", 
                      OrderedDict(), conf["uhire"])

        self.conf = conf
        self.seqtype = seqtype
        self.multiseq_file = multiseq_file
        self.alg_fasta_file = os.path.join(self.taskdir, "final_alg.fasta")
        self.alg_phylip_file = os.path.join(self.taskdir, "final_alg.iphylip")

        # Load jobs
        self.init()

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format. 
        alg = SeqGroup(self.alg_fasta_file)
        alg.write(outfile=self.alg_phylip_file, format="iphylip_relaxed")

    def load_jobs(self):
        # split the original set of sequences in clusters.
        uhire_args = {
            "--clumpfasta": "../",
            "--maxclump": "%s" %self.conf["uhire"]["_maxclump"],
            "--usersort": "",
            "--uhire": self.multiseq_file,
            }
        uhire_job = Job(self.conf["app"]["usearch"], uhire_args, "usearch-uhire")

        # Builds a muscle alignment for each of those clusters. (This
        # is a special job to align all clumps independently. The
        # whole shell command is used as job binary, so it is very
        # important that there is no trailing lines at the end of the
        # command.)
        cmd = """
        (cd ../;
        mkdir clumpalgs/;
        for fname in clump.* master;
           do %s -in $fname -out clumpalgs/$fname -maxiters %s;
        done;) """ %(self.conf["app"]["muscle"], 
                     self.conf["uhire"]["_muscle_maxiters"])

        alg_job = Job(cmd, {}, "uhire_muscle_algs")
        alg_job.dependencies.add(uhire_job)

        # Merge the cluster alignemnts into a single one
        umerge_args = {
            "--mergeclumps": "../clumpalgs/",
            "--output": self.alg_fasta_file,
            }
        umerge_job = Job(self.conf["app"]["usearch"], umerge_args, "usearch-umerge")
        umerge_job.dependencies.add(alg_job)
        
        # Add all jobs to the task queue queue
        self.jobs.extend([uhire_job, alg_job, umerge_job])
