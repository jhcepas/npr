import os
import shutil
import hashlib
import time
from string import strip
import logging
import numpy
from collections import deque
import re
from ete2a1 import PhyloTree, SeqGroup


# Aux functions
get_md5 = lambda x: hashlib.md5(x).hexdigest()
get_raxml_mem = lambda taxa,sites: (taxa-2) * sites * (80 * 8) * 9.3132e-10
get_cladeid = lambda seqids: get_md5(','.join(sorted(map(strip, seqids))))
del_gaps = lambda seq: seq.replace("-","").replace(".", "")
basename = lambda path: os.path.split(path)[-1]
# Program binary paths 
PHYML_BIN= "phyml"
RAXML_BIN = "raxml728"
MUSCLE_BIN = "muscle"
BASE_DIR = os.path.abspath("./prueba/")
RETRY_WHEN_ERRORS = True
EXECUTE = False

def set_logindent(x):
    global __LOGINDENT__
    __LOGINDENT__ = x

def inc_logindent(x):
    global __LOGINDENT__
    __LOGINDENT__ += x

def dec_logindent(x):
    global __LOGINDENT__
    __LOGINDENT__ -= x

__LOGINDENT__ = 0

class IndentFormatter(logging.Formatter):
    def __init__( self, fmt=None, datefmt=None ):
        logging.Formatter.__init__(self, fmt, datefmt)

    def format( self, rec ):
        rec.indent = ' '*__LOGINDENT__
        out = logging.Formatter.format(self, rec)
        return out

class Process(object):
    ''' A generic program launcher prepared to interact with the Task
    class. '''
    def __repr__(self):
        return "Process (%s-%s)" %(basename(self.bin), self.jobid[:8])

    def __init__(self, bin, args):
        # Used at execution time
        self.jobdir = None
        self.status_file = None
        # How to run the app
        self.bin = bin
        self.args = args
        # generates an unique job identifier based on the params of
        # the app.
        self.jobid = get_md5(','.join(sorted([get_md5(str(pair)) for pair in 
                                              self.args.iteritems()])))
        self.ifdone_cmd = ""
        self.iffail_cmd = ""

    def set_jobdir(self, basepath):
        self.jobdir = os.path.join(basepath, self.jobid)
        if not os.path.exists(self.jobdir):
            os.makedirs(self.jobdir)
        self.status_file = os.path.join(self.jobdir, "__status__")
        self.time_file = os.path.join(self.jobdir, "__time__")
        self.cmd_file = os.path.join(self.jobdir, "__cmd__")
        self.stdout_file = os.path.join(self.jobdir, "__stdout__")
        self.stderr_file = os.path.join(self.jobdir, "__stderr__")
        
    def dump_script(self):
        launch_cmd = ' '.join([self.bin] + ["%s %s" %(k,v) for k,v in self.args.iteritems() if v is not None])
        lines = [
          "#!/bin/sh",
          "(echo R > %s && date > %s) &&" %(self.status_file, self.time_file),
          "(cd %s && %s && (echo D > %s; %s) || (echo E > %s; %s));" %\
              (self.jobdir, launch_cmd,  self.status_file, self.ifdone_cmd, 
               self.status_file, self.iffail_cmd), 
          "date >> %s; " %(self.time_file),
          ]
        script = '\n'.join(lines)
        if not os.path.exists(self.jobdir):
            os.makedirs(self.jobdir)
        open(self.cmd_file, "w").write(script)

 
    def status(self):
        if not os.path.exists(self.status_file):
            return "W"
        else:
            return open(self.status_file).read(1)
   
    def clean(self):
        shutil.rmtree(self.jobdir)
        
class Task(object):
    def __repr__(self):
        return "Task (%s-%s-%s)" %(self.ttype, self.tname, self.taskid[:8])

    def __init__(self, cladeid, task_type, task_name):
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

    def get_jobs_status(self):
        if self.jobs:
            return set([j.status() for j in self.jobs])
        else:
            return set(["D"])

    def dump_job_commands(self):
        inc_logindent(2)
        JOBS = open(self.jobs_file, "w")
        for job in self.jobs:
            job.dump_script()
            
            print >>JOBS, "sh %s >%s 2>%s" %\
                (job.cmd_file, job.stdout_file, job.stderr_file)
        JOBS.close()
        dec_logindent(2)

    def load_task_info(self):
        # Creates a task id based on its jobs
        if not self.taskid: 
            unique_id = get_md5(','.join(sorted([j.jobid for j in self.jobs])))
            self.taskid = unique_id
        self.taskdir = os.path.join(BASE_DIR, self.cladeid, 
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

class MsfTask(Task):
    def __init__(self, cladeid, seed_file, format="fasta"):
        # Initialize task
        Task.__init__(self, cladeid, "msf", "msf-task")

        # Set basic information 
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
        self.load_task_info()

        # Sets the path of output file
        self.multiseq_file = os.path.join(self.taskdir, "msf.fasta")

    def finish(self):
        # Dump msf file to the correct path
        self.msf.write(outfile=self.multiseq_file)
        
    def check(self):
        if os.path.exists(self.multiseq_file):
            return True
        return False
       
class MuscleAlgTask(Task):
    def __init__(self, cladeid, multiseq_file):
        # Initialize task
        Task.__init__(self, cladeid, "alg", "muscle_alg")

        # Arguments and options used to executed the associated muscle
        # jobs. This will identify different Tasks of the same type
        self.multiseq_file = multiseq_file
        self.muscle_args = {
            '-in': None,
            '-out': None,
            '-maxhours': 24,
            }

        # Prepare required jobs
        self.load_jobs()

        # Set task information, such as task working dir and taskid
        self.load_task_info()

        # Set the working dir for all jobs
        self.set_jobs_wd(self.taskdir)

        # Set Task specific attributes
        main_job = self.jobs[0]
        self.alg_fasta_file = os.path.join(main_job.jobdir, "alg.fasta")        
        self.alg_phylip_file = os.path.join(main_job.jobdir, "alg.iphylip")        

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format. Both files, fasta and phylip,
        # remain accessible.
        alg = SeqGroup(self.alg_fasta_file)
        alg.write(outfile=self.alg_phylip_file, format="iphylip_relaxed")

    def load_jobs(self):
        # Only one Muscle job is necessary to run this task
        muscle_args = self.muscle_args.copy()
        muscle_args["-in"] = self.multiseq_file
        muscle_args["-out"] = "alg.fasta"
        job = Process(MUSCLE_BIN, muscle_args)
        self.jobs.append(job)

    def check(self):
        if os.path.exists(self.alg_fasta_file) and \
                os.path.exists(self.alg_phylip_file):
            return True
        return False

class TrimalTask(Task):
    pass

class MergeTreeTask(Task):
    def __init__(self, cladeid, task_tree, main_tree,
                 rooting_dict=None):
        # Initialize task
        Task.__init__(self, cladeid, "mergetree", "tree_merger")
        print "task tree", task_tree
        print "main_tree", main_tree
        # Process current main tree and the new generated tree
        # (task_tree) to find out the outgroups used in task_tree. The
        # trick lies on the fact that cladeid is always calculated
        # ignoring the IDs of outgroups seqs.
        if main_tree:
            target_node = main_tree.search_nodes(cladeid=cladeid)[0]
            core_seqs = set(target_node.get_leaf_names())
            outgroup_seqs = set(task_tree.get_leaf_names()) - core_seqs
        else:
            outgroup_seqs = None

        t = task_tree
        print "pruned task_tree", t
        # Root task_tree. If outgroup_seqs are available, uses manual
        # rooting. Otherwise, it means that task_tree is the result of
        # the first iteration, so it will try automatic rooting based
        # on dictionary or midpoint. 
        if outgroup_seqs: 
            log.info("Rooting new tree using %d custom seqs" %
                     len(outgroup_seqs))
            outgroup = t.get_common_ancestor(outgroup_seqs)
            # If outcrop_seqs are split by current root node, outgroup
            # cannot be found. Let's find it from a different
            # perspective using non-outgroup seqs.
            if outgroup is t: 
                outgroup = t.get_common_ancestor(core_seqs)

            t.set_outgroup(outgroup)
            t = t.get_common_ancestor(core_seqs)
            # Let's forget about outgroups, we want only the
            # informative topology
            t.detach() 

        elif rooting_dict:
            log.info("Rooting new tree using a rooting dictionary")
            t.set_outgroup(t.get_farthest_oldest_node(rooting_dict))
        else:
            log.info("Rooting new tree using midpoint outgroup")
            t.set_outgroup(t.get_midpoint_outgroup())

        # Extract the two new partitions (potentially representing two
        # new iterations in the pipeline). Note that outgroup node was
        # detached previously.
        a = t.children[0]
        b = t.children[1]
        
        # Sequences grouped by each of the new partitions
        seqs_a = a.get_leaf_names()
        seqs_b = b.get_leaf_names()

        # To detect the best outgroups of each of the new partitions
        # (a and b), I calculate the branch length distances from them
        # (a and b) to all leaf nodes in its corresponding sister
        # node.
        to_b_dists = []
        to_a_dists = []
        for b_leaf in b.iter_leaves():
            dist = b_leaf.get_distance(a)
            to_a_dists.append([dist, b_leaf.name])
        for a_leaf in a.iter_leaves():
            dist = a_leaf.get_distance(b)
            to_b_dists.append([dist, a_leaf.name])

        # Then we can sort outgroups prioritizing sequences whose
        # distances are close to the mean (avoiding the closest and
        # farthest sequences).
        mean_to_b_dist = numpy.mean([d[0] for d in  to_b_dists])
        mean_to_a_dist = numpy.mean([d[0] for d in  to_a_dists])
        rank_outs_a = sorted(to_a_dists, lambda x,y: cmp(abs(x[0] - mean_to_a_dist),
                                                        abs(y[0] - mean_to_a_dist),
                                                        ))

        rank_outs_b = sorted(to_b_dists, lambda x,y: cmp(abs(x[0] - mean_to_b_dist),
                                                        abs(y[0] - mean_to_b_dist),
                                                        ))
        outs_a = [e[1] for e in rank_outs_a]
        outs_b = [e[1] for e in rank_outs_b]
        log.debug("Mean distance to node A: %s" %mean_to_a_dist)
        log.debug("Best outgroup for A: %s" %rank_outs_a[:2])
        log.debug("Mean distance to node B: %s" %mean_to_b_dist)
        log.debug("Best outgroup for B: %s" %rank_outs_b[:2])

        # Annotate current tree
        for n in t.traverse():
            n.add_features(cladeid=get_cladeid(n.get_leaf_names()))

        # Updates main tree with the results extracted from task_tree
        if main_tree is None:
            main_tree = t
        else:
            log.info("Merging trees")
            target = main_tree.search_nodes(cladeid=cladeid)[0] 
            # Switch nodes in the main_tree so current tree topology
            # is incorporated.
            up = target.up
            target.detach()
            up.add_child(t)
        
        self.set_a = [a.cladeid, seqs_a, outs_a]
        self.set_b = [b.cladeid, seqs_b, outs_b]
        self.main_tree = main_tree
        print "final main_tree", main_tree

class RaxmlTreeTask(Task):
    def __init__(self, cladeid, alg_file, model):
        Task.__init__(self, cladeid, "tree", "raxml_tree")
        # set app arguments and options
        self.alg_file = alg_file
        seqtype = "PROT"
        cpus = 2
        partitions_file = None
        self.raxml_args = {
            '-f': "d", # Normal ML algorithm 
            '-T': '%d' %cpus, 
            '-m': '%sGAMMA%s' %(seqtype, model.upper()),
            '-s': self.alg_file,
            '-n': self.cladeid, 
            '-q': partitions_file,
            }

        self.load_jobs()
        self.load_task_info()
        self.set_jobs_wd(self.taskdir)
        
    def load_jobs(self):
        tree_job = Process(RAXML_BIN, self.raxml_args)
        self.jobs.append(tree_job)

    def finish(self):
        # first job is the raxml tree
        tree_job = self.jobs[0]
        self.tree_file = os.path.join(tree_job.jobdir, 
                                      "RAxML_bestTree."+self.cladeid)

    def check(self):
        if os.path.exists(self.tree_file) and PhyloTree(self.tree_file):
            return True
        return False

class ModelChooserTask(Task):
    def __init__(self, cladeid, alg_file):
        Task.__init__(self, cladeid, "mchooser", "model_chooser")
        self.best_model = None
        self.alg_file = alg_file
        self.alg_basename = basename(self.alg_file)
        self.models = ["JTT", "DcMut"]#, "Blosum62", "MtRev"]
        # Arguments used to start phyml jobs. Note that models is a
        # list, so the dictionary will be used to submit several
        # phyml_jobs
        self.phyml_args = {
            "--datatype": "aa",
            "--input": self.alg_basename,
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
        self.set_jobs_wd(self.taskdir)

        # Phyml cannot write the output in a different directory that
        # the original alg file. So I use relative path to alg file
        # for processes and I create a symlink for each of the
        # instances.
        for j in self.jobs:
            fake_alg_file = os.path.join(j.jobdir, self.alg_basename)
            if os.path.exists(fake_alg_file):
                os.remove(fake_alg_file)
                    
            os.symlink(self.alg_file, fake_alg_file)

    def load_jobs(self):
        for m in self.models:
            args = self.phyml_args.copy()
            args["--model"] = m
            job = Process(PHYML_BIN, args)
            self.jobs.append(job)

    def finish(self):
        lks = []
        for j in self.jobs:
            tree_file = os.path.join(j.jobdir, 
                                     self.alg_basename+"_phyml_tree.txt")
            stats_file = os.path.join(j.jobdir, 
                                      self.alg_basename+"_phyml_stats.txt")
            tree = PhyloTree(tree_file)
            m = re.search('Log-likelihood:\s+(-?\d+\.\d+)', 
                          open(stats_file).read())
            lk = float(m.groups()[0])
            tree.add_feature("lk", lk)
            tree.add_feature("model", j.args["--model"])
            lks.append([float(tree.lk), tree.model])
        lks.sort()
        lks.reverse()
        # choose the model with higher likelihood
        self.best_model = lks[-1][1] 

    def check(self):
        if self.best_model != None:
            return True
        return False

def schedule(processer, schedule_time, seed_file):
    """ Main pipeline scheduler """ 
    WAITING_TIME = schedule_time
    main_tree = None
    # Initial task hangs from the seed msf file. Note that empty
    # cladeid force cladeid to be generated using all seqs in file.
    init_task = MsfTask(None, seed_file)
    pending_tasks = deque([init_task])
    while pending_tasks:
        for task in list(pending_tasks):
            set_logindent(0)
            log.info(task)
            inc_logindent(2)
            log.info("TaskDir: %s" %task.taskdir)
            log.info("TaskJobs: %d" %len(task.jobs))
            inc_logindent(2)
            for j in task.jobs:
                log.info(j)
            inc_logindent(-2)

            if task.status == "W":
                task.dump_job_commands()
                task.status = "R"
                if EXECUTE: 
                    log.info("Running jobs..")
                    os.system("sh %s" %task.jobs_file)

            if task.status == "R":
                log.info("Task is marked as Running")
                jobs_status = task.get_jobs_status()
                log.info("JobStatus: %s" %jobs_status)
                if jobs_status == set("D"):
                    task.finish()
                    if task.check():
                        inc_logindent(3)
                        new_tasks, main_tree = processer(task, main_tree)
                        inc_logindent(-3)
                        pending_tasks.extend(new_tasks)
                        pending_tasks.remove(task)
                        task.status = "D"
                    else: 
                        log.error("Task looks done but result files are not found")
                        task.status = "E"
                elif "E" in jobs_status:
                    task.status = "E"

            elif task.status == "E":
                log.info("Task is marked as ERROR")
                if RETRY_WHEN_ERRORS:
                    log.info("Remarking task as undone to retry")
                    task.retry()
            elif task.status == "D":
                log.info("Task is DONE")
            
        time.sleep(WAITING_TIME)
        print

def my_pipeline(task, main_tree):
    """ This function defines the pipeline that will be applied. You
    can configure rules to decide which steps follow the others and
    make decisions about when to stop or continue the optimization.
    """
    new_tasks = []
    if task.ttype == "msf":
        new_tasks.append(MuscleAlgTask(task.cladeid,
                                       task.multiseq_file))

    elif task.ttype == "alg":
        #new_tasks.append(\
        #    TrimalTask(task.cladeid, task.alg_file))
        new_tasks.append(ModelChooserTask(task.cladeid, 
                                          task.alg_phylip_file))

    elif task.ttype == "acleaner":
        new_tasks.append(ModelChooserTask(task.cladeid,
                                          task.clean_alg_file))

    elif task.ttype == "mchooser":
        new_tasks.append(RaxmlTreeTask(task.cladeid, 
                                       task.alg_file, task.best_model))

    elif task.ttype == "tree":
        t = PhyloTree(task.tree_file)
        merge = MergeTreeTask(task.cladeid, t, main_tree)
        main_tree = merge.main_tree
        alg = SeqGroup(task.alg_file, "iphylip_relaxed")
        for part in [merge.set_a, merge.set_b]:
            set_cladeid, seqs, outgroups = part
            if len(seqs)>4 and len(outgroups)>2:
                msf_seqs = seqs + outgroups[:3]
                new_msf_file = os.path.join(task.taskdir, "children_%s.msf" %set_cladeid)
                fasta = '\n'.join([">%s\n%s" %
                                   (n,del_gaps(alg.get_seq(n)))
                                   for n in msf_seqs])
                open(new_msf_file, "w").write(fasta)
                new_tasks.append(\
                    MsfTask(set_cladeid, new_msf_file))
    return new_tasks, main_tree

if __name__ == "__main__":
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    log_handler = logging.StreamHandler()
    log_format = IndentFormatter("%(levelname) 6s -%(indent)s %(message)s")

    log_handler.setFormatter(log_format)
    log = logging.Logger("main")
    log.addHandler(log_handler)
    schedule(my_pipeline, 1, "./Phy0007XAR_HUMAN.msf.fasta")

