import os
import logging
from logger import logindent
log = logging.getLogger("main")

from utils import get_md5, merge_dicts, PhyloTree, SeqGroup, checksum
from master_job import Job

isjob = lambda j: isinstance(j, Job)
istask = lambda j: isinstance(j, Task)

class Task(object):
    global_config = {"basedir": "./test"}

    def __repr__(self):
        if self.taskid:
            tid = self.taskid[:6]
        else:
            tid = "?"
        return "Task (%s: %s, %s)" %(self.ttype, self.tname, tid)

    def summary(self):
        print "Type:", self.ttype
        print "Name:", self.tname
        print "Id:", self.taskid
        print "Dir:", self.taskdir
        print "Jobs", len(self.jobs)
        print "Status", self.status
        for tag, value in self.args.iteritems():
            print tag,":", value

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
        # or (W)aiting or (Un)Finished
        self.status_file = None
        self.key_file = None
        self.status = "W"
        self._donejobs = set()
        self.dependencies = set()
        # Initialize job arguments 
        self.args = merge_dicts(extra_args, base_args, parent=self)

    def get_status(self):
        job_status = self.get_jobs_status()
        # Order matters
        if "E" in job_status: 
            st = "E"
        elif "W" in job_status: 
            st =  "W"
        elif "R" in job_status: 
            st = "R"
        elif set("D") == job_status: 
            self.finish()
            if self.check():
                st = "D"
            else:
                st = "E"
        else:
            st = "?"
        self.status = st
        return st

    def get_taskdir(self, *files):
        input_key = checksum(*files)

        taskdir = os.path.join(self.global_config["basedir"], self.cladeid,
                               self.tname+"_"+input_key)
        return taskdir

    def init(self):
        # Prepare required jobs
        self.load_jobs()

        # Set task information, such as task working dir and taskid
        self.load_task_info()

        # Set the working dir for all jobs
        self.set_jobs_wd(self.taskdir)

    def get_jobs_status(self):
        ''' Check the status of all children jobs. '''
        all_states = set()

        if self.jobs:
            for j in self.jobs:
                if j not in self._donejobs:
                    st = j.get_status()
                    all_states.add(st)
                    if st == "D": 
                        self._donejobs.add(j)
                        
        if not all_states:
            all_states.add("D")
        return all_states

    def load_task_info(self):
        ''' Initialize task information. It generates a unique taskID
        based on the sibling jobs and sets task working directory. ''' 

        # Creates a task id based on its jobs and arguments. The same
        # tasks, including the same parameters would raise the same
        # id, so it is easy to check if a task is already done in the
        # working path. Note that this prevents using.taskdir before
        # calling task.init()
        if not self.taskid:
            unique_id = get_md5(','.join(sorted(
                        [getattr(j, "jobid", "taskid") for j in self.jobs])))
            self.taskid = unique_id

        self.taskdir = os.path.join(self.global_config["basedir"], self.cladeid,
                               self.tname+"_"+self.taskid)

        if not os.path.exists(self.taskdir):
            os.makedirs(self.taskdir)

        self.status_file = os.path.join(self.taskdir, "__status__")
        self.jobs_file = os.path.join(self.taskdir, "__jobs__")
        self.key_file = os.path.join(self.taskdir, "__input__")

    def set_jobs_wd(self, path):
        ''' Sets working directory of all sibling jobs '''
        for j in self.jobs:
            # Only if job is not another Task instance
            if issubclass(Job, j.__class__):
                j.set_jobdir(path)

    def retry(self):
        for job in self.jobs:
            if job.get_status() == "E":
                job.clean()

    def launch_jobs(self):
        for j in self.jobs:
            # Skip done jobs and those that depend on unfinished jobs
            if j in self._donejobs or \
                    (j.dependencies - self._donejobs): 
                continue
            # Process the rest
            if isjob(j):
                j.dump_script()
                cmd = "sh %s >%s 2>%s\n" %\
                    (j.cmd_file, j.stdout_file, j.stderr_file)
                yield j, cmd
            elif istask(j):
                for subj, cmd in j.launch_jobs():
                    yield j, cmd

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


class AlgTask(Task):
    def __repr__(self):
        return "AlgTask (%s seqs, %s, %s)" %\
            (getattr(self, "nseqs", 0),
             self.tname, 
             getattr(self, "taskid", "?")[:6])

    def check(self):
        if os.path.exists(self.alg_fasta_file) and \
                os.path.exists(self.alg_phylip_file) and \
                os.path.getsize(self.alg_fasta_file) and \
                os.path.getsize(self.alg_phylip_file):
            return True
        return False


class AlgCleanerTask(Task):
    def __repr__(self):
        return "AlgCleanerTask (%s seqs, %s, %s)" %\
            (getattr(self, "nseqs", 0),
             self.tname, 
             getattr(self, "taskid", "?")[:6])

    def check(self):
        if os.path.exists(self.clean_alg_fasta_file) and \
                os.path.exists(self.clean_alg_phylip_file) and \
                os.path.getsize(self.clean_alg_fasta_file) and \
                os.path.getsize(self.clean_alg_phylip_file):
            return True
        return False

class ModelTesterTask(Task):
    def __repr__(self):
        return "ModelTesterTask (%s seqs, %s, %s)" %\
            (getattr(self, "nseqs", 0),
             self.tname, 
             getattr(self, "taskid", "?")[:6])

    def check(self):
        if (self.tree_file and not 
            (os.path.exists(self.tree_file) and
             PhyloTree(self.tree_file))) or not self.best_model:
            return False
        return True


class TreeTask(Task):
    def __repr__(self):
        return "TreeTask (%s seqs, %s, %s)" %\
            (getattr(self, "nseqs", 0),
             self.tname, 
             (getattr(self, "taskid", None) or "?")[:6])

    def check(self):
        if os.path.exists(self.tree_file) and \
                os.path.getsize(self.tree_file):
            return True
        return False

