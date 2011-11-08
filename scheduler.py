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
    # Then enters into the pipeline. 
    while pending_tasks:
        # A will modify pending_task within the loop, so I create a
        # copy of it
        for task in list(pending_tasks):
            set_logindent(0)
            log.info(task)
            logindent(2)
            tdir = task.taskdir.replace(config["main"]["basedir"], "")
            tdir = tdir.lstrip("/")
            log.info("TaskDir: %s" %tdir)
            log.info("TaskJobs: %d" %len(task.jobs))
            logindent(2)
            for j in task.jobs:
                log.info(j)
            logindent(-2)

            if task.status == "W":
                task.dump_job_commands()
                task.status = "R"
                if execution: 
                    log.info("Running jobs..")
                    os.system("sh %s" %task.jobs_file)

            if task.status == "R":
                log.info("Task is marked as Running")
                jobs_status = task.get_jobs_status()
                log.info("JobStatus: %s" %jobs_status)
                if jobs_status == set("D"):
                    task.finish()
                    if task.check():
                        logindent(3)
                        new_tasks, main_tree = processer(task, main_tree, 
                                                         config)
                        logindent(-3)
                        pending_tasks.extend(new_tasks)
                        pending_tasks.remove(task)
                        task.status = "D"
                        clade2tasks[task.cladeid].append(task)
                    else: 
                        log.error("Task looks done but result files are not found")
                        task.status = "E"
                elif "E" in jobs_status:
                    task.status = "E"

            elif task.status == "E":
                log.error("Task is marked as ERROR")
                if retry:
                    log.info("Remarking task as undone to retry")
                    task.retry()
                else:
                    raise Exception("ERROR FOUND")
            elif task.status == "D":
                log.info("Task is DONE")

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
    for n in main_tree.traverse():
        n.cladeid = get_cladeid(n.get_leaf_names())
        print n.cladeid
        for ts in clade2tasks.get(n.cladeid, []):
            print "   ", ts

