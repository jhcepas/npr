import os
from subprocess import call, Popen
from time import sleep
from collections import defaultdict
import logging
from logger import set_logindent, logindent
log = logging.getLogger("main")

from utils import get_cladeid, render_tree
from errors import ConfigError, DataError

def schedule(config, processer, schedule_time, execution, retry):
    """ Main pipeline scheduler """ 

    config["_alg_conversion"] = {}
    # Pass seed files to processer to generate the initial task
    pending_tasks, main_tree = processer(None, None, 
                                         config)
    clade2tasks = defaultdict(list)
    sort_by_cladeid = lambda x,y: cmp(x.cladeid, y.cladeid)
    # Then enters into the pipeline.
    cores_total = config["main"]["_max_cores"]

    while pending_tasks:
        cores_used = 0
        wait_time = 0 # Try to go fast unless running tasks
        set_logindent(0)
        log.info("Checking the status of %d tasks" %len(pending_tasks))
        # Check task status and compute total cores being used
        for task in pending_tasks:
            task.status = task.get_status()
            cores_used += task.cores_used
        
        for task in sorted(pending_tasks, sort_by_cladeid):
            set_logindent(0)
            log.info(task)
            logindent(2)
            tdir = task.taskdir.replace(config["main"]["basedir"], "")
            tdir = tdir.lstrip("/")
            log.info("TaskDir: %s" %tdir)
            log.info("TaskJobs: %d" %len(task.jobs))
            log.info("Task status : %s" %task.status)

            if task.status == "W" or task.status == "R":
                # shows info about unfinished jobs
                logindent(2)
                for j in task.jobs:
                    if j.status != "D":
                        log.info("%s: %s", j.status, j)
                logindent(-2)
                
                log.info("missing %d jobs." %len(set(task.jobs)-task._donejobs))
                # Tries to send new jobs from this task
                pids = []
                for j, cmd in task.iter_waiting_jobs():
                    if not check_cores(j, cores_used, cores_total, execution):
                        continue
                    if execution:
                        log.info("Launching %s" %j)
                        try:
                            P = Popen(cmd, shell=True)
                        except:
                            task.save_status("E")
                            task.status = "E"
                            raise
                        else:
                            pids.append(P.pid)
                            task.status = "R"
                            j.status = "R"
                            cores_used += j.cores
                            #print P
                    else:
                        task.status = "R"
                        j.status = "R"
                        # Do something cool like sending to cluster.
                        print cmd
                        
                if not pids:
                    wait_time = schedule_time
                    
            elif task.status == "D":
                logindent(3)
                new_tasks, main_tree = processer(task, main_tree, config)
                logindent(-3)
                pending_tasks.remove(task)
                pending_tasks.extend(new_tasks)
                clade2tasks[task.cladeid].append(task)

            elif task.status == "E":
                log.error("Task is marked as ERROR")
                if retry:
                    log.info("Remarking task as undone to retry")
                    task.retry()
                else:
                    raise Exception("ERROR FOUND in", task.taskdir)

            else:
                wait_time = schedule_time
                log.error("Unknown task state [%s]", task.status)
                continue

            log.info("Cores used %s" %cores_used)
            # If last task processed a new tree node, dump snapshots
            if task.ttype == "treemerger":
                #log.info("Annotating tree")
                #annotate_tree(main_tree, clade2tasks)
                #nw_file = os.path.join(config["main"]["basedir"],
                #                       "tree_snapshots", task.cladeid+".nw")
                #main_tree.write(outfile=nw_file, features=[])
                
                if config["main"]["render_tree_images"]:
                    log.info("Rendering tree image")
                    img_file = os.path.join(config["main"]["basedir"], 
                                            "gallery", task.cladeid+".svg")
                    render_tree(main_tree, img_file)
            
        sleep(wait_time)
        print 

    final_tree_file = os.path.join(config["main"]["basedir"], \
                                       "final_tree.nw")
    main_tree.write(outfile=final_tree_file)
    main_tree.show()

def annotate_tree(t, clade2tasks):
    n2names = get_node2content(t)
    for n in t.traverse():
        n.add_features(cladeid=get_cladeid(n2names[n]))
    
    clade2node = dict([ (n.cladeid, n) for n in t.traverse()])
    for cladeid, alltasks in clade2tasks.iteritems():
        n = clade2node[cladeid]
        for task in alltasks:

            params = ["%s %s" %(k,v) for k,v in  task.args.iteritems() 
                      if not k.startswith("_")]
            params = " ".join(params)

            if task.ttype == "msf":
                n.add_features(nseqs=task.nseqs, 
                               msf_file=task.seed_file)
            elif task.ttype == "acleaner":
                n.add_features(clean_alg_mean_identn=task.mean_ident, 
                               clean_alg_std_ident=task.std_ident, 
                               clean_alg_max_ident=task.max_ident, 
                               clean_alg_min_ident=task.min_ident, 
                               clean_alg_type=task.tname, 
                               clean_alg_cmd=params)
            elif task.ttype == "alg":
                n.add_features(alg_mean_identn=task.mean_ident, 
                               alg_std_ident=task.std_ident, 
                               alg_max_ident=task.max_ident, 
                               alg_min_ident=task.min_ident, 
                               alg_type=task.tname, 
                               alg_cmd=params)
            elif task.ttype == "tree":
                n.add_features(tree_model=task.model, 
                               tree_seqtype=task.seqtype, 
                               tree_type=task.tname, 
                               tree_cmd=params)
            elif task.ttype == "mchooser":
                n.add_features(modeltester_models=task.models, 
                               modeltester_type=task.tname, 
                               modeltester_params=params, 
                               modeltester_bestmodel=task.get_best_model(), 
                               )
            elif task.ttype == "tree_merger":
                n.add_features(treemerger_type=task.tname, 
                               treemerger_hidden_outgroup=task.outgroup_topology, 
                               )

def check_cores(j, cores_used, cores_total, execution):
    if j.cores > cores_total:
        raise ConfigError("Job [%s] is trying to be executed using [%d] cores."
                          " However, the program is limited to [%d] core(s)."
                          " Use the --multicore option to enable more cores." %
                          (j, j.cores, cores_total))
    elif execution and j.cores > cores_total-cores_used:
        log.info("Job [%s] will be postponed until [%d] core(s) are available." 
                 % (j, j.cores))
        return False
    else:
        return True
    
def get_node2content(node, store={}):
    for ch in node.children:
        get_node2content(ch, store=store)

    if node.children:
        val = []
        for ch in node.children:
            val.extend(store[ch])
        store[node] = val
    else:
        store[node] = [node.name]
    return store
