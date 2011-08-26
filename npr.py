import os
import time
import logging
from collections import deque

from argparse import ArgumentParser

from utils import del_gaps
from task import *

try:
    module_path = os.path.split(__file__)[0]
    __VERSION__ = open(os.path.join(module_path, "VERSION")).read().strip()
except: 
    __VERSION__ = "unknown"

__DESCRIPTION__ = """ 
Nested Phylogenetic Reconstruction program.  
NPR-1.0%s (Aug, 2011).

If you use this program for published work, please cite: 

  Jaime Huerta-Cepas and Toni Gabaldon. Nested Phylogenetic
  Reconstruction. XXX-XX. 2011.

Contact: jhuerta (at) crg.es, tgabaldon (at) crg.es

""" %__VERSION__

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
    parser = ArgumentParser(description=__DESCRIPTION__)
    # name or flags - Either a name or a list of option strings, e.g. foo or -f, --foo.
    # action - The basic type of action to be taken when this argument is encountered at the command line. (store, store_const, store_true, store_false, append, append_const, version)
    # nargs - The number of command-line arguments that should be consumed. (N, ? (one or default), * (all 1 or more), + (more than 1) )
    # const - A constant value required by some action and nargs selections. 
    # default - The value produced if the argument is absent from the command line.
    # type - The type to which the command-line argument should be converted.
    # choices - A container of the allowable values for the argument.
    # required - Whether or not the command-line option may be omitted (optionals only).
    # help - A brief description of what the argument does.
    # metavar - A name for the argument in usage messages.
    # dest - The name of the attribute to be added to the object returned by parse_args().

    parser.add_argument("-s", "--seed-file", dest="init_msf_file", 
                        type=str, 
                        help=""" Initial multi sequence file""")
 
    args = parser.parse_args()
    
    print __DESCRIPTION__

    # Prepares main log
    log = logging.getLogger("main")
    log.setLevel(logging.DEBUG)
    log_format = IndentFormatter("%(levelname) 6s -%(indent)s %(message)s")
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(log_format)
    log.addHandler(log_handler)

    # Example run
    schedule(my_pipeline, 1, "./Phy0007XAR_HUMAN.msf.fasta")

