import os
import logging
log = logging.getLogger("main")

from .master_task import Task
from .master_job import Job
from .utils import SeqGroup

__all__ = ["Uhire"]

class Uhire(Task):
    def __init__(self, cladeid, multiseq_file, seqtype, conf):
        self.conf = conf
        self.seqtype = seqtype
        self.multiseq_file = multiseq_file

        base_args = {}
        # Initialize task
        Task.__init__(self, cladeid, "alg", "Usearch-Uhire", 
                      base_args, conf["uhire"])

        # Set Task specific attributes
        self.alg_fasta_file = os.path.join(self.taskdir, "final_alg.fasta")
        self.alg_phylip_file = os.path.join(self.taskdir, "final_alg.iphylip")

        # Load task data
        self.init()


    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format. Both files, fasta and phylip,
        # remain accessible.
        alg = SeqGroup(self.alg_fasta_file)
        self.nseqs = len(alg.id2seq)
        alg.write(outfile=self.alg_phylip_file, format="iphylip_relaxed")

    def load_jobs(self):
        uhire_args = {
            "--clumpfasta": "../",
            "--maxclump": "5000",
            "--usersort": "",
            "--uhire": self.multiseq_file,
            }
        uhire_job = Job(self.conf["app"]["usearch"], uhire_args)

        # This is a special job to align all clumps independently
        cmd = """
        (cd ../;
        mkdir clumpalgs/;
        for fname in clump.* master;
           do %s -in $fname -out clumpalgs/$fname -maxiters 4;
        done;) """ %(self.conf["app"]["muscle"])
        alg_job = Job(cmd, {}, "uhire_muscle_algs")
        alg_job.dependencies.add(uhire_job)

        # Merge the alignemnts
        umerge_args = {
            "--mergeclumps": "../clumpalgs/",
            "--output": self.alg_fasta_file,
            }
        umerge_job = Job(self.conf["app"]["usearch"], umerge_args)
        umerge_job.dependencies.add(alg_job)

        self.jobs.extend([uhire_job, alg_job, umerge_job])

    def check(self):
        if os.path.exists(self.alg_fasta_file) and \
                os.path.exists(self.alg_phylip_file):
            return True
        return False



