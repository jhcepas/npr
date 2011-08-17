import os
import hashlib
from string import strip
import logging as log

from ete2a1 import PhyloTree, SeqGroup

log.basicConfig(level=log.DEBUG, \
                    format="%(levelname)s - %(message)s" )

# Aux functions
get_md5 = lambda x: hashlib.md5(x).hexdigest()
get_raxml_mem = lambda taxa,sites: (taxa-2) * sites * (80 * 8) * 9.3132e-10
get_cladeid = lambda seqids: get_md5(','.join(sorted(map(strip, seqids))))

# Program binary paths 
PHYML_BIN= "phyml3"
RAXML_BIN = "raxml728"
MUSCLE_BIN = "muscle"
BASE_DIR = "/prueba/"

# ########## App types ############# #
class Process(object):
    ''' A generic program launcher prepared to interact with the Task
    class. '''
    def __init__(self, bin, args):
        # Used at execution time
        self.jobdir = None
        self.status_file = None
        # How to run the app
        self.bin = bin
        self.args = args
        # generates an unique job identifier based on the params of the app.
        self.jobid = get_md5(','.join(sorted([get_md5(str(pair)) for pair in self.args.iteritems()])))

    def set_jobdir(self, basepath):
        self.jobdir = os.path.join(basepath, self.jobid)
        self.status_file = os.path.join(self.jobdir, "__status__")
        self.time_file = os.path.join(self.jobdir, "__time__")
        self.cmd_file = os.path.join(self.jobdir, "__cmd__")

    def dump_script(self):
        app_call = ' '.join([self.bin] + ["%s %s" %(k,v) for k,v in self.args.iteritems() if v is not None])
        lines = [
          "#!/bin/sh",
          "(mkdir -p %s && echo R > %s && date > %s) &&" %(self.jobdir, self.status_file, self.time_file),
          "(%s && echo D > %s || echo E > %s) &&" %(app_call, self.status_file, self.status_file), 
          "date >> %s; " %(self.time_file),
          ]
        script = '\n'.join(lines)
        return script
        #open(self.cmd_file, "w").write(script)
 
    def status(self):
        if not os.path.exists(self.status_file):
            return "M"
        else:
            return open(self.status_file).read(1)
   
class Task(object):
    def __init__(self, cladeid, task_type, task_name):
        self.cladeid = cladeid
        # task type: "alg|tree|acleaner|mchooser|bootstrap"
        self.ttype = task_type 
        self.tname = task_name
        # To be filled by the subtypes
        self.jobs = []
        self.taskdir = None
        self.taskid = None
        self.jobs_file = None
        self.status_file = None

    def get_jobs_status(self):
        if self.jobs:
            return set([j.status() for j in self.jobs])
        else:
            return set(["D"])

    def dump_job_commands(self):
        JOBS = open(self.jobs_file, "w")
        for job in self.jobs:
            print >>JOBS, "sh %s" %job.cmd_file
        JOBS.close()

    def load_task_info(self):
        # Creates a task id based on its jobs
        unique_id = get_md5(','.join(sorted([j.jobid for j in self.jobs])))
        self.taskid = '_'.join([self.tname, unique_id])
        self.taskdir = os.path.join(BASE_DIR, self.cladeid, self.taskid)
        if not os.path.exists(self.taskdir):
            os.makedirs(self.taskdir)
           

        self.status_file = os.path.join(self.taskdir, "__status__")
        self.jobs_file = os.path.join(self.taskdir, "__jobs__")

    def set_jobs_wd(self, path):
        for j in self.jobs:
            j.set_jobdir(path)

    def load_jobs(self):
        ''' Customizable function. It must create all job objects and add
        them to self.jobs'''

    def finish(self):
        ''' Customizable function. It must process all jobs and set
        the resulting values of the task. For instance, set variables
        pointing to the resulting file '''
    
class MsfTask(Task):
    def __init__(self, seed_file, format="fasta"):

        self.seed_file = seed_file
        self.seed_file_format = format
        self.msf = SeqGroup(self.seed_file, format=self.seed_file_format)
        cladeid = get_cladeid(self.msf.id2name.values())
        self.nseqs = len(self.msf)
        Task.__init__(self, cladeid, "alg", "initial_msf")
        # Sets task information, such as taskdir and taskid
        self.load_task_info()
        # Sets the path of output file
        self.multiseq_file = os.path.join(self.taskdir, "msf.fasta")


    def finish(self):
        self.msf.write(outfile=self.multiseq_file)

class MuscleAlgTask(Task):
    def __init__(self, cladeid, multiseq_file):
        Task.__init__(self, cladeid, "alg", "muscle_alg")

        # set app arguments and options
        self.multiseq_file = multiseq_file
        self.muscle_args = {
            '-in': self.multiseq_file,
            '-out': "alg.fasta",
            '-maxhours': 24,
            }

        # Prepare needed jobs
        self.load_jobs()
        # Sets task information, such as taskdir and taskid
        self.load_task_info()
        # Sets the working dir for all jobs
        self.set_job_wd(self.taskdir)

        # set output file 
        self.alg_file = os.path.join(self.taskdir, "alg.fasta")
       
    def load_jobs(self):
        muscle_args = self.muscle_args.copy()
        job = Process(MUSCLE_BIN, muscle_args)
        self.jobs.append(job)
      
class RaxmlTreeTask(Task):
    def __init__(self, cladeid, alg_file, model):
        Task.__init__(self, cladeid, "tree", "raxml_tree")
        # set app arguments and options
        self.alg_file = alg_file
        seqtype = "PROT"
        cpus = 1
        partitions_file = None
        self.raxml_args = {
            '-f': "d", # Normal ML algorithm 
            '-T': '%d' %cpus, 
            '-m': '%sGAMMA%s' %(seqtype, model),
            '-s': self.alg_file,
            '-n': self.cladeid, 
            '-q': partitions_file,
            }

        self.load_jobs()
        self.load_task_info()
        self.set_job_wd(self.taskdir)

        
    def load_jobs(self):
        tree_job = Process(RAXML_BIN, self.raxml_args)
        self.jobs.append(tree_job)

    def finish(self):
        # first job is the raxml tree
        tree_job = self.jobs[0]
        self.tree_file = os.path.join(tree_job.jobdir, "RAxML_bestTree."+self.cladeid)

class ModelChooserTask(Task):
    def __init__(self, alg_file):
        Task.__init__(self, "mchooser")
        self.best_model = None
        self.models = ["JTT", "DcMut", "Blosum62", "MtRev"]
        # Arguments used to start phyml jobs. Note that models is a
        # list, so the dictionary will be used to submit several
        # phyml_jobs
        self.phyml_args = {
            "--datatype": "aa",
            "--input": alg_file,
            "--bootstrap": "0",
            "-f": "m", # char freq (m)odel or (e)stimated
            "--pinv": "e",
            "--alpha": "e",
            "-o": "lr",
            "--nclasses": "4",
            "--model": None, # I will iterate over this value when
                            # creating jobs
            "--quiet": "" }

        # Prepare jobs and task
        self.load_jobs()
        self.load_task_info()
        self.set_job_wd(self.taskdir)

    def load_jobs(self):
        for m in self.models:
            args = self.phyml_args.copy()
            args["--model"] = m
            job = self.job_builder(PHYML_BIN, args)
            self.jobs.append(job)

    def finish(self):
        lks = []
        for j in self.jobs():
            tree = j.get_tree()
            lks.append([float(tree.lk), tree.model])
        lks.sort()
        self.best_model = lks[-1][1] # model with higher likelihood 


def processer(task):
    """ This function defines the algorithm followed by the pipeline. It
    creates new jobs and decides what programs to run and when to run
    them. """

    new_tasks = []
    if task.get_jobs_status() == set(["D"]):
        task.finish()
        if task.ttype == "msf":
            new_tasks.append(\
                MuscleAlgTask(task.cladeid, task.multiseq_file))

        elif task.ttype == "alg":
            new_tasks.append(\
                AlgCleanerTask(task.cladeid, task.alg_file))
            
        elif task.ttype == "acleaner":
            new_tasks.append(\
                ModelChooserTask(task.cladeid, task.clean_alg_file))

        elif task.ttype == "mchooser":
            new_tasks.append(\
                RaxmlTreeTask(task.alg_file, task.best_model))
        
        elif job.ttype == "tree":
            new_tasks.append(\
                MsfTask(task.alg_file, task.msf_file1))
            new_tasks.append(\
                MsfTask(task.alg_file, task.msf_file2))

    return new_tasks
   
def pipeliner(processer, schedule_time, seed_file):
    """ Main pipeline scheduler """ 
    WAITING_TIME = schedule_time
    
    pending_tasks = [MsfTask(seed_file)]
    while True:
        for task in pending_tasks:
            if task.done():
                processer(job)           
            else:
                task.execute()

        time.sleep(WAITING_TIME)

