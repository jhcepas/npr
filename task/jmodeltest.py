import os
import logging
log = logging.getLogger("main")

from .master_task import ModelTesterTask
from .master_job import Job
from .utils import basename, PhyloTree

__all__ = ["JModeltest"]

class JModeltest(ModelTesterTask):
    def __init__(self, cladeid, alg_fasta_file, alg_phylip_file, conf):
        self.conf = conf
        base_args = {
            '-d': alg_fasta_file, 
            }
        args = self.conf["jmodeltest"]
        if args.get("-t", "ML") == "ML":
            task_type = "tree"
        else:
            task_type = "mchooser"
            
        ModelTesterTask.__init__(self, cladeid, task_type, "Jmodeltest", base_args, args)

        # set app arguments and options
        self.alg_fasta_file = alg_fasta_file
        self.alg_phylip_file = alg_phylip_file
        self.seqtype = "nt"
        self.best_model = None
        self.models = "see jmodeltest params"
        self.tree_file = None

        self.init()

    def load_jobs(self):
        tree_job = Job(self.conf["app"]["jmodeltest"], self.args)
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
        ModelTesterTask.finish(self)
