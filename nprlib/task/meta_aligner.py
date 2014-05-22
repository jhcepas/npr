import os
import logging
import shutil
log = logging.getLogger("main")

from nprlib.master_task import AlgTask, Task
from nprlib.master_job import Job
from nprlib.utils import (SeqGroup, OrderedDict, checksum, pjoin,
                          GLOBALS, MCOFFEE_CITE, DATATYPES)
from nprlib.apps import APP2CLASS, CLASS2MODULE
from nprlib import db

import __init__ as task

__all__ = ["MetaAligner"]

def seq_reverser_job(multiseq_file, outfile, parent_ids, trimal_bin):
     """ Returns a job reversing all sequences in MSF or MSA. """
     reversion_args = {"-in": multiseq_file, "-out": outfile,
                       "-reverse": "", "-fasta": ""}
     job = Job(trimal_bin, reversion_args, "TrimalAlgReverser",
               parent_ids=parent_ids)
     return job

class MCoffee(AlgTask):
    def __init__(self, nodeid, seqtype, all_alg_files, conf, confname, parent_ids):
        GLOBALS["citator"].add(MCOFFEE_CITE)
        base_args = OrderedDict({
                "-output": "fasta",
                })
        # Initialize task
        self.confname = confname
        self.conf = conf
        AlgTask.__init__(self, nodeid, "alg", "Mcoffee", 
                         base_args, self.conf[confname])
        self.all_alg_files = all_alg_files
        self.parent_ids = parent_ids
        self.seqtype = seqtype
        self.init()
        
    def load_jobs(self):
        args = self.args.copy()
        args["-outfile"] = "mcoffee.fasta"

        alg_paths = [pjoin(GLOBALS["input_dir"], algid)
                     for algid in self.all_alg_files]
        args["-aln"] = ' '.join(alg_paths)
        job = Job(self.conf["app"]["tcoffee"], args, parent_ids=self.parent_ids)
        for key in self.all_alg_files:
            job.add_input_file(key)
        self.jobs.append(job)

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format.
        alg = SeqGroup(os.path.join(self.jobs[0].jobdir, "mcoffee.fasta"))
        fasta = alg.write(format="fasta")
        phylip = alg.write(format="iphylip_relaxed")

        alg_list_string = '\n'.join([pjoin(GLOBALS["input_dir"],
                                           aname) for aname in self.all_alg_files])
        db.add_task_data(self.taskid, DATATYPES.alg_list, alg_list_string)
        
        AlgTask.store_data(self, fasta, phylip)
        
    def init_output_info(self):
        self.alg_list_file = "%s.%s" %(self.taskid, DATATYPES.alg_list)
        AlgTask.init_output_info(self)
        
        
class MetaAligner(AlgTask):
    def __init__(self, nodeid, multiseq_file, seqtype, conf, confname):
        self.confname = confname
        self.conf = conf
        # Initialize task
        AlgTask.__init__(self, nodeid, "alg", "Meta-Alg", 
                         OrderedDict(), self.conf[self.confname])

        self.seqtype = seqtype
        self.multiseq_file = multiseq_file
        self.size = conf["_nodeinfo"][nodeid].get("size", 0)
        self.all_alg_files = None
        self.init()

        #if self.conf[confname]["_alg_trimming"]:
        #    self.alg_list_file = pjoin(self.taskdir, "alg_list.txt")
        #    open(self.alg_list_file, "w").write("\n".join(self.all_alg_files))
        #    trim_job = self.jobs[-1]
        #    trim_job.args["-compareset"] = self.alg_list_file
        #    trim_job.args["-out"] = pjoin(self.taskdir, "final_trimmed_alg.fasta")
        #    trim_job.alg_fasta_file = trim_job.args["-out"]
        #    trim_job.alg_phylip_file = None
                        
        
    def load_jobs(self):
        readal_bin = self.conf["app"]["readal"]
        trimal_bin = self.conf["app"]["trimal"]
        input_dir = GLOBALS["input_dir"]
        multiseq_file = pjoin(input_dir, self.multiseq_file)
        multiseq_file_r = pjoin(input_dir, self.multiseq_file+"_reversed")
        
        first = seq_reverser_job(multiseq_file, multiseq_file_r, 
                                 [self.nodeid], readal_bin)
        #print self.multiseq_file
        first.add_input_file(self.multiseq_file)
        self.jobs.append(first)
        
        all_alg_names = []
        mcoffee_parents = []
        for aligner_name in self.conf[self.confname]["_aligners"]:
            _classname = APP2CLASS[self.conf[aligner_name]["_app"]]

            _module = __import__(CLASS2MODULE[_classname], globals(), locals(), [], -1)
            _aligner = getattr(_module, _classname)

            # Normal alg
            task1 = _aligner(self.nodeid, self.multiseq_file, self.seqtype,
                             self.conf, aligner_name)
            task1.size = self.size
            self.jobs.append(task1)
            all_alg_names.append(task1.alg_fasta_file)
           
            
            # Alg of the reverse
            task2 = _aligner(self.nodeid, self.multiseq_file+"_reversed",
                             self.seqtype, self.conf, aligner_name)
            task2.size = self.size
            task2.dependencies.add(first)
            self.jobs.append(task2)
            
            # Restore reverse alg
            reverse_out = pjoin(input_dir, task2.alg_fasta_file)
            task3 = seq_reverser_job(reverse_out,
                                     reverse_out+"_restored",
                                     [task2.taskid], readal_bin)
            task3.dependencies.add(task2)
            task3.add_input_file(task2.alg_fasta_file)
            all_alg_names.append(reverse_out+"_restored")
            self.jobs.append(task3)
            mcoffee_parents.extend([task1.taskid, task2.taskid])
            
        # Combine signal from all algs using Mcoffee
        mcoffee_task = MCoffee(self.nodeid, self.seqtype, all_alg_names,
                               self.conf, self.confname, parent_ids=mcoffee_parents)
        # reversed algs are not actually saved into db, but it should
        # be present since the reverser job is always executed
        mcoffee_task.dependencies.update(list(self.jobs)) 
        self.jobs.append(mcoffee_task)

        if self.conf[self.confname]["_alg_trimming"]:
            trimming_cutoff = 1.0 / len(all_alg_names)
            targs = {}
            targs["-forceselect"] = pjoin(input_dir, mcoffee_task.alg_fasta_file)
            targs["-compareset"] = pjoin(input_dir, mcoffee_task.alg_list_file)
            targs["-out"] = "mcoffee.trimmed.fasta"
            targs["-fasta"] = ""
            targs["-ct"] = trimming_cutoff
            trim_job = Job(trimal_bin, targs, parent_ids=[mcoffee_task.taskid])
            trim_job.jobname = "McoffeeTrimming"
            trim_job.dependencies.add(mcoffee_task)
            trim_job.alg_fasta_file = targs["-out"]
            for key in all_alg_names:
                trim_job.add_input_file(key)
            trim_job.add_input_file(mcoffee_task.alg_fasta_file)
            trim_job.add_input_file(mcoffee_task.alg_list_file)
            self.jobs.append(trim_job)      

    def finish(self):
        if self.conf[self.confname]["_alg_trimming"]:
            # If trimming happened after mcoffee, let's save the
            # resulting output
            trim_job = self.jobs[-1]
            alg = SeqGroup(pjoin(trim_job.jobdir, trim_job.alg_fasta_file))
            fasta = alg.write(format="fasta")
            phylip = alg.write(format="iphylip_relaxed")
            AlgTask.store_data(self, fasta, phylip)
        else:
            # If no post trimming, output is just what Mcoffee
            # produced, so we can recycle its data ids.
            mc_task = self.jobs[-1]
            fasta_id = db.get_dataid(mc_task.taskid, DATATYPES.alg_fasta)
            phylip_id = db.get_dataid(mc_task.taskid, DATATYPES.alg_phylip)
            db.register_task_data(self.taskid, DATATYPES.alg_fasta, fasta_id)
            db.register_task_data(self.taskid, DATATYPES.alg_phylip, phylip_id)
