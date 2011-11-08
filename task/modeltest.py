import os
import logging
log = logging.getLogger("main")

from .master_task import Task
from .master_job import Job
from .utils import basename, PhyloTree

__all__ = ["JModeltest"]

class JModeltest(Task):
    def __init__(self, cladeid, alg_fasta_file, alg_phylip_file, args):
        base_args = {
            '-d': alg_fasta_file, 
            }

        if args.get("-t", "ML") == "ML":
            task_type = "tree"
        else:
            task_type = "mchooser"
            
        Task.__init__(self, cladeid, task_type, "jmodeltest", base_args, args)
        # set app arguments and options
        self.bin = args["_path"]
        self.alg_fasta_file = alg_fasta_file
        self.alg_phylip_file = alg_phylip_file
        self.seqtype = "nt"
        self.best_model = None
        self.tree_file = None
        # Load task data
        self.init()

    def load_jobs(self):
        tree_job = Job(self.bin, self.args)
        self.jobs.append(tree_job)

    def finish(self):
        # first job is the raxml tree
        best_model = None
        best_model_in_next_line = False
        t = None
        for line in open(self.jobs[-1].stdout_file, "rU"):
            line = line.strip()
            if best_model_in_next_line and line.startswith("Model"):
                pass#best_model = line.split("=")[1].strip()
            elif best_model_in_next_line and line.startswith("partition"):
                best_model = line.split("=")[1].strip()
                best_model_in_next_line = False
            elif line.startswith("Model selected:"):
                best_model_in_next_line = True
            elif line.startswith("ML tree (NNI) for the best AIC model ="): 
                nw = line.replace("ML tree (NNI) for the best AIC model =", "")
                t = PhyloTree(nw)
        if t: 
            tree_job = self.jobs[-1]
            self.tree_file = os.path.join(tree_job.jobdir,
                                          "jModelTest_tree."+self.cladeid)
            t.write(outfile=self.tree_file)

        self.best_model = best_model
        self.model = best_model
        log.info("Best model: %s" %self.best_model)

    def check(self):
        if not self.best_model or (self.tree_file and not \
                                      (os.path.exists(self.tree_file) and\
                                           PhyloTree(self.tree_file))):

            return False
        return True

