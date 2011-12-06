import os
import logging
from logger import logindent
log = logging.getLogger("main")

from utils import get_md5, merge_dicts, PhyloTree, SeqGroup
from master_job import Job


### __init__
### init()
###    load_jobs
###    load_task_info
###    set_jobs_wd

class Task(object):
    global_config = {"basedir": "./test"}
    def __repr__(self):
        if self.taskid:
            tid = self.taskid[:6]
        else:
            tid = "?"
        return "Task (%s-%s, %s)" %(self.ttype, self.tname, tid)

    def __init__(self, cladeid, task_type, task_name, base_args={}, 
                 extra_args={}):
        # Cladeid is used to identify the tree node associated with
        # the task. It is calculated as a hash string based on the
        # list of sequence IDs grouped by the node.
        self.cladeid = cladeid

        # task type: "alg|tree|acleaner|mchooser|bootstrap"
        self.ttype = task_type

        # Used only to name directories and identify task in log
        # messages
        self.tname = task_name

        # =============================================================
        # The following attributes are expected to be completed by the
        # subclasses
        # =============================================================

        # List of associated jobs necessary to complete the task. Job
        # and Task classes are accepted as elements in the list.
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

        # Intialize job arguments 
        self.args = merge_dicts(extra_args, base_args, parent=self)

    def get_status(self):
        job_status = self.get_jobs_status()
        if "E" in job_status: 
            return "E"
        elif "W" in job_status: 
            return "E"
        elif set("D") == job_status: 
            self.finish()
            if self.check():
                return "D"
            else:
                return "E"
        else:
            return "?"

    def init(self):
        # Prepare required jobs
        self.load_jobs()

        # Set task information, such as task working dir and taskid
        self.load_task_info()

        # Set the working dir for all jobs
        self.set_jobs_wd(self.taskdir)
        
    def get_jobs_status(self):
        ''' Check the status of all children jobs. '''
        if self.jobs:
            return set([j.get_status() for j in self.jobs])
        else:
            return set(["D"])

    def dump_job_commands(self):
        ''' Generates a shell script (__jobs__) to launch all job
        commands. ''' 
        FILE = open(self.jobs_file, "w")
        for job in self.jobs:
            if isinstance(job, Job):
                job.dump_script()
                FILE.write("sh %s >%s 2>%s\n" %\
                           (job.cmd_file, job.stdout_file, job.stderr_file))
            elif isinstance(job, Task):
                job.dump_job_commands()
                FILE.write("sh %s \n" %\
                           (job.jobs_file))
            else:
                log.error("Unsupported job type", job)
        FILE.close()

    def load_task_info(self):
        ''' Initialize task information. It generates a unique taskID
        based on the sibling jobs and sets task working directory. ''' 

        # Creates a task id based on its jobs
        if not self.taskid:
            unique_id = get_md5(','.join(sorted([getattr(j, "jobid", "taskid") for j in self.jobs])))
            self.taskid = unique_id

        self.taskdir = os.path.join(self.global_config["basedir"], self.cladeid,
                                    self.tname+"_"+self.taskid)
        if not os.path.exists(self.taskdir):
            os.makedirs(self.taskdir)

        self.status_file = os.path.join(self.taskdir, "__status__")
        self.jobs_file = os.path.join(self.taskdir, "__jobs__")

    def set_jobs_wd(self, path):
        ''' Sets working directory of all sibling jobs '''
        for j in self.jobs:
            # Only if job is not another Task instance
            if issubclass(Job, j.__class__):
                j.set_jobdir(path)

    def retry(self):
        self.status = "W"
        for job in self.jobs:
            if job.get_status() == "E":
                job.clean()

    def exec_jobs(self):
        self.status = "R"
        for j in self.jobs:
            if isinstance(j, Job):
                log.info("Running job  %s", j)
                os.system("sh %s >%s 2>%s\n" %\
                              (j.cmd_file, j.stdout_file, j.stderr_file))
            elif isinstance(j, Task):
                log.info("Running subtask %s", j)
                logindent(+2)
                j.exec_jobs()
                log.info("Finishing subtask %s", j)
                self.finish()
                logindent(-2)
            status = j.get_status()
            if status != "D": 
                raise Exception("Error in ", j)

    def load_jobs(self):
        ''' Customizable function. It must create all job objects and add
        them to self.jobs'''

    def finish(self):
        ''' Customizable function. It must process all jobs and set
        the resulting values of the task. For instance, set variables
        pointing to the resulting file '''

    def check(self):
        ''' Customizable function. Return true if task is done and
        expected results are available. '''
        return True




