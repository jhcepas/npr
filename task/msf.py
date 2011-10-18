import os
import sys
import logging
log = logging.getLogger("main")

from .master_task import Task
from .utils import get_cladeid

sys.path.insert(0, "/home/jhuerta/_Devel/ete/2.2/")
from .master_job import Job
from ete_dev import PhyloTree, SeqGroup

__all__ = ["Msf"]

class Msf(Task):
    def __init__(self, cladeid, seed_file, seqtype, format="fasta"):
        # Initialize task
        Task.__init__(self, cladeid, "msf", "MSF")

        # Set basic information
        self.seqtype = seqtype
        self.seed_file = seed_file
        self.seed_file_format = format
        self.msf = SeqGroup(self.seed_file, format=self.seed_file_format)
        self.nseqs = len(self.msf)
        msf_id = get_cladeid(self.msf.id2name.values())

        # Cladeid is created ignoring outgroup seqs. In contrast,
        # msf_id is calculated using all IDs present in the MSF. If no
        # cladeid is supplied, we can assume that MSF represents the
        # first iteration, so no outgroups must be ignored. Therefore,
        # cladeid=msfid
        if not cladeid:
            self.cladeid = msf_id
        else:
            self.cladeid = cladeid

        # taskid does not depend on jobs, so I set it manually
        self.taskid = msf_id

        # Sets task information, such as taskdir. taskid will kept as
        # it was set manually
        self.init()

        # Sets the path of output file
        self.multiseq_file = os.path.join(self.taskdir, "msf.fasta")

    def finish(self):
        # Dump msf file to the correct path
        self.msf.write(outfile=self.multiseq_file)

    def check(self):
        if os.path.exists(self.multiseq_file):
            return True
        return False
