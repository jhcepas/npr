import os
import logging
log = logging.getLogger("main")
from collections import defaultdict

from nprlib.logger import logindent
from nprlib.utils import (md5, merge_arg_dicts, PhyloTree, SeqGroup,
                          checksum, read_time_file, generate_runid,
                          GLOBALS, DATATYPES)
from nprlib.master_job import Job
from nprlib.errors import RetryException, TaskError
from nprlib import db
import shutil

isjob = lambda j: isinstance(j, Job)
istask = lambda j: isinstance(j, Task)

def thread_name(task):
    tid = getattr(task, "threadid", None)
    return "@@13:%s@@1:" %GLOBALS.get(tid, {}).get("_name", "?")

def genetree_class_repr(cls, cls_name):
    """ Human readable representation of NPR genetree tasks.""" 
    return "%s (%s seqs, %s, %s/%s)" %\
        (cls_name, getattr(cls, "size", None) or 0,
         cls.tname, 
         (getattr(cls, "taskid", None) or "?")[:6],
         thread_name(cls))

def sptree_class_repr(cls, cls_name):
    """ Human readable representation of NPR sptree tasks.""" 
    return "%s (%s species, %s, %s/%s)" %\
        (cls_name,
         getattr(cls, "size", None) or 0,
         cls.tname, 
         (getattr(cls, "taskid", None) or "?")[:6],
         thread_name(cls))

def concatalg_class_repr(cls, cls_name):
    """ Human readable representation of NPR  concat alg tasks.""" 
    return "%s (%s species, %s COGs, %s, %s/%s)" %\
        (cls_name, getattr(cls, "size", None) or 0,
         getattr(cls, "used_cogs", None) or "?",
         cls.tname, 
         (getattr(cls, "taskid", None) or "?")[:6],
         thread_name(cls))

def generic_class_repr(cls, cls_name):
    """ Human readable representation of NPR sptree tasks.""" 
    return "%s (%s tips, %s, %s/%s)" %\
        (cls_name, getattr(cls, "size", None) or 0,
         cls.tname, 
         (getattr(cls, "taskid", None) or "?")[:6],
         thread_name(cls))

class Task(object):
    def _get_max_cores(self):
        return max([j.cores for j in self.jobs]) or 1
            
    cores = property(_get_max_cores,None)
    
    def __repr__(self):
        return generic_class_repr(self, "Task")

    def print_summary(self):
        print "Type:", self.ttype
        print "Name:", self.tname
        print "Id:", self.taskid
        print "Dir:", self.taskdir
        print "Jobs", len(self.jobs)
        print "Status", self.status
        for tag, value in self.args.iteritems():
            print tag,":", value

    def __init__(self, nodeid, task_type, task_name, base_args=None, 
                 extra_args=None):

        if not base_args: base_args = {}
        if not extra_args: extra_args = {}
        
        # This define which task-processor should be used
        # (i.e. genetree, sptree).
        self.task_processor = None
        
        # Nodeid is used to identify the tree node associated with
        # the task. It is calculated as a hash string based on the
        # list of sequence IDs grouped by the node.
        self.nodeid = nodeid

        # task type: "alg|tree|acleaner|mchooser|etc."
        self.ttype = task_type

        # Used only to name directories and identify task in log
        # messages
        self.tname = task_name

        # Unique id based on the parameters set for each task
        self.taskid = None

        # Path to the file containing task status: (D)one, (R)unning
        # or (W)aiting or (Un)Finished
        #self.status_file = None
        #self.inkey_file = None
        #self.info_file = None
        self.status = "W"
        self.all_status = None

        # keeps a counter of how many cores are being used by running jobs
        self.cores_used = 0
        
        self.job_status = {}
        
        # Set arguments that could be sent to jobs
        self.args = merge_arg_dicts(extra_args, base_args, parent=self)
        # extract all internal config values associated to this task
        # and generate its unique id (later used to generate taskid)
        self._config_id = md5(','.join(sorted(["%s %s" %(str(pair[0]),str(pair[1])) for pair in
                                       extra_args.iteritems() if pair[0].startswith("_")])))
        
    def get_status(self, sge_jobs=None):
        # If another tasks with the same id (same work to be done) has
        # been checked in the same cycle, reuse its information
        if self.taskid in GLOBALS["cached_status"]:
            return GLOBALS["cached_status"][self.taskid]

        # Otherwise check the status or all its children jobs and
        # tasks
        logindent(2)

        last_status = db.get_last_task_status(self.taskid)
        task_saved = db.task_is_saved(self.taskid)

        # If task is processed and saved, just return its state
        # without checking children
        if task_saved and last_status == "D":
            print "DATA SAVED AND PROCESSED"
            self.status = "D"
        # If I have just noticed the task is done and saved, load its
        # stored data.
        elif task_saved and last_status != "D":
            print "DATA SAVED. LOADING......"
            self.status = "D"
            self.load_stored_data()
        else:
            # Otherwise, we need to check for all children
            self.job_status = self.get_jobs_status(sge_jobs)
            job_statuses = set(self.job_status.keys())
            # If all children jobs have just finished, we process the
            # task, and save it into the database
            if job_statuses == set("D"):
                logindent(-2)
                log.log(22, "Processing done task: %s", self)
                logindent(2)
                try:
                    self.finish()
                except Exception, e:
                    raise TaskError(self, e)
                else:
                    #store in database .......
                    if self.check():
                        self.status = "D"
                    else:
                        raise TaskError(self, "Task check not passed")
            # Otherwise, update the ongoing task status, but do not
            # store result yet.
            else: 
                # Order matters
                if "E" in job_statuses:
                    self.status = "E"
                elif "L" in job_statuses:
                    self.status = "L"
                elif "R" in job_statuses: 
                    self.status =  "R"
                elif "Q" in job_statuses: 
                    self.status =  "Q"
                elif "W" in job_statuses: 
                    self.status = "W"
                else:
                    log.error("unknown task state")

        logindent(-2)
        
        GLOBALS["cached_status"][self.taskid] = self.status
        print "REPORTED", self.taskid, self.status, task_saved, last_status
        return self.status

    def init(self):

        # List of associated jobs necessary to complete the task. Job
        # and Task classes are accepted as elements in the list.
        self.jobs = []
       
        self._donejobs = set()
        self._running_jobs = set()
        self.dependencies = set()
       
        # Prepare required jobs
        self.load_jobs()
        
        # Set task information, such as task working dir and taskid
        self.load_task_info()
        
    def get_saved_status(self):
        try:
            return open(self.status_file, "ru").read(1)
        except IOError: 
            return "?"
        

    def get_jobs_status(self, sge_jobs=None):
        ''' Check the status of all children jobs. '''
        self.cores_used = 0
        all_states = defaultdict(int)
        jobs_to_check = set(reversed(self.jobs))
        while jobs_to_check:
            j = jobs_to_check.pop()
            logindent(1)
            jobid = j.taskid if istask(j) else j.jobid
            
            if jobid in GLOBALS["cached_status"]:
                log.log(22, "@@8:Recycling status@@1: %s" %j)
                st = GLOBALS["cached_status"][jobid]
                all_states[st] += 1
                
            elif j not in self._donejobs:
                st = j.get_status(sge_jobs)
                GLOBALS["cached_status"][jobid] = st
                all_states[st] += 1
                if st == "D":
                    self._donejobs.add(j)
                    # If task has an internal worflow processor,
                    # launch it and populate with new jobs
                    if istask(j) and j.task_processor:
                        for new_job in j.task_processor(j):
                            jobs_to_check.add(new_job)
                            self.jobs.append(new_job)
                elif st in set("QRL"):
                    if isjob(j) and not j.host.startswith("@sge"):
                        self.cores_used += j.cores
                    elif istask(j):
                        self.cores_used += j.cores_used
                elif st == "E":
                    errorpath = j.jobdir if isjob(j) else j.taskid
                    raise TaskError(j, "Job execution error %s" %errorpath)
            else:
                all_states["D"] += 1
                
            logindent(-1)              
        if not all_states:
            all_states["D"] +=1

        return all_states

    def load_task_info(self):
        ''' Initialize task information. It generates a unique taskID
        based on the sibling jobs and sets task working directory. ''' 

        # Creates a task id based on its target node and job
        # arguments. The same tasks, including the same parameters
        # would raise the same id, so it is easy to check if a task is
        # already done in the working path. Note that this prevents
        # using.taskdir before calling task.init()
        if not self.taskid:
            args_id = md5(','.join(sorted(["%s %s" %(str(pair[0]),str(pair[1])) for pair in
                       self.args.iteritems()])))
             
            unique_id = md5(','.join([self.nodeid, self._config_id, args_id]+sorted(
                        [getattr(j, "jobid", "taskid") for j in self.jobs])))

            self.taskid = unique_id

    def retry(self):
        for job in self.jobs:
            if job.get_status() == "E":
                if isjob(job):
                    job.clean()
                elif istask(job):
                    job.retry()
        self.status = "W"
        #self.post_init()

    def iter_waiting_jobs(self):
        for j in self.jobs:
            # Process only  jobs whose dependencies are satisfied
            st = j.status
            #if isjob(j):
            #    print "jobid", j.jobid, st
            if st == "W" and not (j.dependencies - self._donejobs): 
                if isjob(j):
                    j.dump_script()
                    cmd = "sh %s >%s 2>%s" %\
                        (j.cmd_file, j.stdout_file, j.stderr_file)
                    yield j, cmd
                elif istask(j):
                    for subj, cmd in j.iter_waiting_jobs():
                        yield subj, cmd

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

    def post_init(self):
        '''Customizable function. Put here or the initialization steps
        that must run after init (load_jobs, taskid, etc). 
        '''
    def store_data(self, DB):
        ''' This should store in the database all relevant data
        associated to the task '''
        pass
            

class MsfTask(Task):
    def __repr__(self):
        return genetree_class_repr(self, "@@6:MultiSeqTask@@1:")

    def load_stored_data(self):
        self.multiseq_file = db.get_dataid(self.taskid, DATATYPES.msf)
        
    def store_data(self, msf):
        self.multiseq_file = db.add_task_data(self.taskid, DATATYPES.msf, msf)
        
    def check(self):
        if self.multiseq_file:
            return True
        return False
        
class AlgTask(Task):
    def __repr__(self):
        return genetree_class_repr(self, "@@5:AlgTask@@1:")

    def check(self):
        if self.alg_fasta_file and self.alg_phylip_file:
            return True
        return False
    
    def load_stored_data(self):
        self.alg_fasta_file = db.get_dataid(self.taskid, DATATYPES.alg_fasta)
        self.alg_phylip_file = db.get_dataid(self.taskid, DATATYPES.alg_phylip)
        
    def store_data(self, fasta, phylip):
        self.alg_fasta_file = db.add_task_data(self.taskid, DATATYPES.alg_fasta, fasta)
        self.alg_phylip_file = db.add_task_data(self.taskid, DATATYPES.alg_phylip, phylip)
        
class AlgCleanerTask(Task):
    def __repr__(self):
        return genetree_class_repr(self, "@@4:AlgCleanerTask@@1:")

    def check(self):
        if self.clean_alg_fasta_file and \
                self.clean_alg_phylip_file: 
            return True
        return False
           
    def load_stored_data(self):
        self.clean_alg_fasta_file = db.get_dataid(self.taskid, DATATYPES.clean_alg_fasta)
        self.clean_alg_phylip_file = db.get_dataid(self.taskid, DATATYPES.clean_alg_phylip)
        self.kept_columns = db.get_task_data(self.taskid, DATATYPES.kept_alg_columns)

    def store_data(self, fasta, phylip, kept_columns):
        self.clean_alg_fasta_file = db.add_task_data(self.taskid, DATATYPES.clean_alg_fasta, fasta)
        self.clean_alg_phylip_file = db.add_task_data(self.taskid, DATATYPES.clean_alg_phylip, phylip)
        self.kept_columns = db.add_task_data(self.taskid, DATATYPES.kept_alg_columns, kept_columns)
        
class ModelTesterTask(Task):
    def __repr__(self):
        return genetree_class_repr(self, "@@2:ModelTesterTask@@1:")

    def get_best_model(self):
        return open(self.best_model_file, "ru").read()

    def check(self):
        if not os.path.exists(self.best_model_file) or\
                not os.path.getsize(self.best_model_file):
            return False
        elif self.tree_file:
            if not os.path.exists(self.tree_file) or\
                    not os.path.getsize(self.tree_file):
                return False
        return True

    #def store_data(self, DB):
    #    DB.add_task_data(self.taskid, DATATYPES.best_model, open(self.best_model_file))

    def load_stored_data(self):
        self.best_model = db.get_dataid(self.taskid, DATATYPES.best_model)
        
class TreeTask(Task):
    def __init__(self, nodeid, task_type, task_name, base_args=None, 
                 extra_args=None):
        if not base_args: base_args = {}
        extra_args = {} if not extra_args else dict(extra_args)
        extra_args["_algchecksum"] = self.alg_phylip_file
        extra_args["_constrainchecksum"] = self.constrain_tree
        
        Task.__init__(self, nodeid, task_type, task_name, base_args, 
                      extra_args)
        
    def __repr__(self):
        return generic_class_repr(self, "@@3:TreeTask@@1:")

    def check(self):
        if self.tree_file: 
            return True
        return False

    def load_stored_data(self):
        self.tree_file = db.get_dataid(self.taskid, DATATYPES.tree)

    def store_data(self, newick):
        self.tree_file = db.add_task_data(self.taskid, DATATYPES.tree, newick)
    
class TreeMergeTask(Task):
    def __init__(self, nodeid, task_type, task_name, base_args=None, 
                 extra_args=None):
        # I want every tree merge instance to be unique (avoids
        # recycling and undesired collisions between trees from
        # different threads containing the same topology
        extra_args["_treechecksum"] = generate_runid()
        Task.__init__(self, nodeid, task_type, task_name, base_args, 
                      extra_args)

    def __repr__(self):
        return generic_class_repr(self, "@@3:TreeMergeTask@@1:")
       

class ConcatAlgTask(Task):
    def __repr__(self):
        return concatalg_class_repr(self, "@@5:ConcatAlgTask@@1:")

    def check(self):
        if self.alg_fasta_file and self.alg_phylip_file: 
            return True
        return False

    def load_stored_data(self):
        self.partitions_file = db.get_dataid(self.taskid, DATATYPES.model_partitions)
        self.alg_fasta_file = db.get_dataid(self.taskid, DATATYPES.concat_alg_fasta)
        self.alg_phylip_file = db.get_dataid(self.taskid, DATATYPES.concat_alg_phylip)
    
    def store_data(self, fasta, phylip, partitions):
        self.partitions_file = db.add_task_data(self.taskid, DATATYPES.model_partitions, partitions)
        self.alg_fasta_file = db.add_task_data(self.taskid, DATATYPES.concat_alg_fasta, fasta)
        self.alg_phylip_file = db.add_task_data(self.taskid, DATATYPES.concat_alg_phylip, phylip)
    
class CogSelectorTask(Task):
    def __repr__(self):
        return sptree_class_repr(self, "@@6:CogSelectorTask@@1:")

    def check(self):
        if self.cogs:
            return True
        return False

    def load_stored_data(self):
        self.cogs = db.get_task_data(self.taskid, DATATYPES.cogs)
        self.cog_analysis = db.get_task_data(self.taskid, DATATYPES.cog_analysis)
    
    def store_data(self, cogs, cog_analysis):
        db.add_task_data(self.taskid, DATATYPES.cogs, cogs)
        db.add_task_data(self.taskid, DATATYPES.cog_analysis, cog_analysis)
        
def register_task_recursively(task, parentid=None):
    db.add_task(tid=task.taskid, nid=task.nodeid, parent=parentid,
                status=task.status, type="task", subtype=task.ttype, name=task.tname)
    for j in task.jobs:
        if isjob(j):
            db.add_task(tid=j.jobid, nid=task.nodeid, parent=task.taskid,
                        status="W", type="job", name=j.jobname)
            
        else:
            register_task_recursively(j, parentid=parentid)
    
def update_task_states_recursively(task):
    task_start = 0
    task_end = 0
    for j in task.jobs:
        if isjob(j):
            start, end = update_job_status(j)
        else:
            start, end = update_task_states_recursively(j)
        task_start = min(task_start, start) if task_start > 0 else start
        task_end = max(task_end, end)
        
    db.update_task(task.taskid, status=task.status, tm_start=task_start, tm_end=task_end)
    return task_start, task_end

def store_task_data_recursively(task):
    # store task data
    task.store_data(db)
    for j in task.jobs:
        if isjob(j):
            pass
        else:
            store_task_data_recursively(j)

def remove_task_dir_recursively(task):
    # store task data
    for j in task.jobs:
        if isjob(j):
            shutil.rmtree(j.jobdir)
        else:
            remove_task_dir_recursively(j)
    shutil.rmtree(task.taskdir)
            
def update_job_status(j):
    start = None
    end = None
    if j.status == "D":
        try:
            start, end = read_time_file(j.time_file)
        except Exception, e:
            log.warning("Execution time could not be loaded into DB: %s", j.jobid[:6])
            log.warning(e)
    db.update_task(j.jobid, status=j.status, tm_start=start, tm_end=end)
    return start, end
