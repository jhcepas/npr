import os
import re
import numpy
import sys
sys.path.insert(0, "/home/jhuerta/_Devel/ete/2.2/")
from ete_dev import PhyloTree, SeqGroup
from ete_dev.parser import fasta
from utils import get_md5, merge_dicts
import logging
log = logging.getLogger("main")

class Task(object):
    global_config = {"basedir": "./test"}
    def __repr__(self):
        if self.taskid:
            tid = self.taskid[:6]
        else:
            tid = "?"
        return "Task (%s-%s, %s)" %(self.ttype, self.tname, tid)

    def __init__(self, cladeid, task_type, task_name, base_args={}, extra_args={}):
        # Cladeid is used to identify the tree node associated with
        # the task. It is calculated as a hash string based on the
        # list of sequence IDs grouped by the node.
        self.cladeid = cladeid

        # task type: "alg|tree|acleaner|mchooser|bootstrap"
        self.ttype = task_type

        # Used only to name directories and identify task in log
        # messages
        self.tname = task_name

        # The following attributes are expected to be filled by the
        # different subclasses

        # List of associated jobs necessary to complete the task
        self.jobs = []

        # Working directory for the task
        self.taskdir = None

        # Unique id based on the parameters set for each task
        self.taskid = None

        # Path to the file with job commands
        self.jobs_file = None

        # Path to the file containing task status: (D)one, (R)unning
        # or (W)aiting
        self.status_file = None
        self.status = "W"
        self.args = merge_dicts(extra_args, base_args, parent=self)


    def init(self):
        # Prepare required jobs
        self.load_jobs()

        # Set task information, such as task working dir and taskid
        self.load_task_info()

        # Set the working dir for all jobs
        self.set_jobs_wd(self.taskdir)
        
    def get_jobs_status(self):
        if self.jobs:
            return set([j.status() for j in self.jobs])
        else:
            return set(["D"])

    def dump_job_commands(self):
        JOBS = open(self.jobs_file, "w")
        for job in self.jobs:
            job.dump_script()
            JOBS.write("sh %s >%s 2>%s\n" %\
                           (job.cmd_file, job.stdout_file, job.stderr_file))
        JOBS.close()

    def load_task_info(self):
        # Creates a task id based on its jobs
        if not self.taskid:
            unique_id = get_md5(','.join(sorted([j.jobid for j in self.jobs])))
            self.taskid = unique_id
        self.taskdir = os.path.join(self.global_config["basedir"], self.cladeid,
                                    self.tname+"_"+self.taskid)
        if not os.path.exists(self.taskdir):
            os.makedirs(self.taskdir)

        self.status_file = os.path.join(self.taskdir, "__status__")
        self.jobs_file = os.path.join(self.taskdir, "__jobs__")

    def set_jobs_wd(self, path):
        for j in self.jobs:
            j.set_jobdir(path)

    def retry(self):
        self.status = "W"
        for job in self.jobs:
            if job.status() == "E":
                job.clean()

    def load_jobs(self):
        ''' Customizable function. It must create all job objects and add
        them to self.jobs'''

    def finish(self):
        ''' Customizable function. It must process all jobs and set
        the resulting values of the task. For instance, set variables
        pointing to the resulting file '''



