import os
from time import sleep
from collections import defaultdict
import logging
from logger import set_logindent, logindent
log = logging.getLogger("main")

from utils import get_cladeid, render_tree

def schedule(config, processer, schedule_time, execution, retry):
    """ Main pipeline scheduler """ 

    WAITING_TIME = schedule_time
    config["_alg_conversion"] = {}
    # Pass seed files to processer to generate the initial task
    pending_tasks, main_tree = processer(None, None, 
                                         config)
    clade2tasks = defaultdict(list)
    sort_by_clade = lambda x,y: cmp(x.cladeid, y.cladeid)
    # Then enters into the pipeline. 
    while pending_tasks:
        # A will modify pending_task within the loop, so I create a
        # copy of it
        for task in sorted(pending_tasks, sort_by_clade):
            set_logindent(0)
            log.info(task)
            logindent(2)
            tdir = task.taskdir.replace(config["main"]["basedir"], "")
            tdir = tdir.lstrip("/")
            log.info("TaskDir: %s" %tdir)
            log.info("TaskJobs: %d" %len(task.jobs))
            task.status = task.get_status()

            logindent(2)
            for j in task.jobs:
                if j.status != "D":
                    log.info("%s: %s", j.status, j)
            logindent(-2)

            if task.status == "W":
                log.info("missing %d jobs." %len(set(task.jobs)-task._donejobs))
                task.status = "R"
                for j, cmd in task.launch_jobs():
                    if execution:
                        log.info("Running %s" %j)
                        os.system(cmd)
                    else:
                        print cmd

            elif task.status == "R":
                log.info("Task is marked as Running")

            elif task.status == "D":
                if task.check():
                    logindent(3)
                    new_tasks, main_tree = processer(task, main_tree, 
                                                     config)
                    logindent(-3)
                    pending_tasks.extend(new_tasks)
                    pending_tasks.remove(task)
                    task.status = "D"
                    clade2tasks[task.cladeid].append(task)
                    if main_tree:
                        annotate_tree(main_tree, clade2tasks)
                else: 
                    log.error("Task looks done but result files are not found")
                    task.status = "E"

            elif task.status == "E":
                log.error("Task is marked as ERROR")
                if retry:
                    log.info("Remarking task as undone to retry")
                    task.retry()
                else:
                    raise Exception("ERROR FOUND in", task.taskdir)

            # If last task processed a new tree node, dump snapshots
            if task.ttype == "treemerger":
                nw_file = os.path.join(config["main"]["basedir"],
                                       "tree_snapshots", task.cladeid+".nw")
                main_tree.write(outfile=nw_file, features=[])
                if config["main"]["render_tree_images"]:
                    img_file = os.path.join(config["main"]["basedir"], 
                                            "gallery", task.cladeid+".png")
                    render_tree(main_tree, img_file)
            
        sleep(WAITING_TIME)
        print 

    final_tree_file = os.path.join(config["main"]["basedir"], \
                                       "final_tree.nw")
    main_tree.write(outfile=final_tree_file)
    main_tree.show()

def annotate_tree(t, clade2tasks):
    for n in t.traverse():
        
        cladeid = get_cladeid(n.get_leaf_names())
        n.add_feature("cladeid", cladeid)

        for task in clade2tasks.get(n.cladeid, []):
            params = ["%s %s" %(k,v) for k,v in  task.args.iteritems() 
                      if not k.startswith("_")]
            params = " ".join(params)

            if task.ttype == "msf":
                n.add_features(nseqs=task.nseqs, 
                               msf_file=task.seed_file)
            elif task.ttype == "acleaner":
                n.add_features(clean_alg_conservation=task.mean_conservation, 
                               clean_alg_conservation_std=task.std_conservation, 
                               clean_alg_max_identity=task.max_identity, 
                               clean_alg_type=task.tname, 
                               clean_alg_cmd=params)
            elif task.ttype == "alg":
                n.add_features(alg_conservation=task.mean_conservation, 
                               alg_conservation_std=task.std_conservation, 
                               alg_max_identity=task.max_identity, 
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
                               modeltester_bestmodel=task.best_model, 
                               )
            elif task.ttype == "tree_merger":
                n.add_features(treemerger_type=task.tname, 
                               treemerger_hidden_outgroup=task.outgroup_topology, 
                               )
