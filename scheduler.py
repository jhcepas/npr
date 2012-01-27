import os
from subprocess import call, Popen
from time import sleep
from collections import defaultdict
import logging
from logger import set_logindent, logindent
log = logging.getLogger("main")

from utils import get_cladeid, render_tree, launch_detached, HOSTNAME
from errors import ConfigError, DataError, TaskError

def schedule(config, processer, schedule_time, execution, retry):
    # Send seed files to processer to generate the initial task
    pending_tasks, main_tree = processer(None, None, 
                                         config)
    clade2tasks = defaultdict(list)
    sort_by_cladeid = lambda x,y: cmp(x.cladeid, y.cladeid)
    # Then enters into the pipeline.
    cores_total = config["main"]["_max_cores"]

    while pending_tasks:
        cores_used = 0
        wait_time = 0.1 # Try to go fast unless running tasks
        set_logindent(0)
        log.log(28, "Checking the status of %d tasks" %len(pending_tasks))
        # Check task status and compute total cores being used
        for task in pending_tasks:
            task.status = task.get_status()
            cores_used += task.cores_used
        
        for task in sorted(pending_tasks, sort_by_cladeid):
            set_logindent(0)
            log.log(28, "(%s) %s" %(task.status, task))
            set_logindent(3)
            st_info = ', '.join(["%s=%d" %(k,v) for k,v in task.job_status.iteritems()])
            log.log(28, "%d jobs: %s" %(len(task.jobs), st_info))
            tdir = task.taskdir.replace(config["main"]["basedir"], "")
            tdir = tdir.lstrip("/")

            log.debug("TaskDir: %s" %tdir)
            
            if task.status == "L":
                log.warning("Some jobs within the task [%s] are marked as (L)ost,"
                            " meaning that although they look as running,"
                            " its execution cannot be tracked. NPR will"
                            " continue execution with other pending tasks."
                            %task)
            
            if task.status in set("WRL"):
                # shows info about unfinished jobs
                logindent(1)
                for j in task.jobs:
                    if j.status != "D":
                        log.log(26, "%s: %s", j.status, j)
                logindent(-1)

                # Tries to send new jobs from this task
                pids = []
                for j, cmd in task.iter_waiting_jobs():
                    if not check_cores(j, cores_used, cores_total, execution):
                        continue
                    if execution:
                        log.log(28, "Launching %s" %j)
                        try:
                            launch_detached(cmd, j.pid_file)
                        except Exception:
                            task.save_status("E")
                            task.status = "E"
                            raise
                        else:
                            pids.append(1)
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
                log.error("Task contains errors")
                if retry:
                    log.log(28, "Remarking task as undone to retry")
                    task.retry()
                else:
                    raise TaskError(task)

            else:
                wait_time = schedule_time
                log.error("Unknown task state [%s].", task.status)
                continue
            set_logindent(-2)
            log.log(26, "Cores in use: %s" %cores_used)
            # If last task processed a new tree node, dump snapshots
            if task.ttype == "treemerger":
                #log.info("Annotating tree")
                #annotate_tree(main_tree, clade2tasks)
                #nw_file = os.path.join(config["main"]["basedir"],
                #                       "tree_snapshots", task.cladeid+".nw")
                #main_tree.write(outfile=nw_file, features=[])
                
                if config["main"]["render_tree_images"]:
                    log.log(28, "Rendering tree image")
                    img_file = os.path.join(config["main"]["basedir"], 
                                            "gallery", task.cladeid+".svg")
                    render_tree(main_tree, img_file)

        #log.debug(wait_time)
        sleep(wait_time)
        print 

    final_tree_file = os.path.join(config["main"]["basedir"], \
                                       "final_tree.nw")
    main_tree.write(outfile=final_tree_file)
    log.debug(str(main_tree))
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
        log.log(24, "Job [%s] will be postponed until [%d] core(s) are available." 
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
