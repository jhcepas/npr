import sys
import os
import time
import re
from collections import defaultdict

import tempfile
from string import strip, split

def launch_jobs(jobs, conf):
    # Group jobs with identical config
    sge_path = conf["main"]["sge_dir"]
    
    conf2jobs = defaultdict(list)
    for j, cmd in jobs:
        job_config = conf["sge"].copy()
        job_config["-pe smp"] = j.cores
        for k,v in j.sge.iteritems():
            job_config[k] = v
        conf_key = tuple(sorted(job_config.items()))
        conf2jobs[conf_key].append(cmd)

    for job_config, commands in conf2jobs.iteritems():
        job_file = "%s_%d_jobs" %(time.ctime().replace(" ", "_").replace(":","-"),
                                  len(commands))
        cmds_file = os.path.join(sge_path, job_file+".cmds")
        qsub_file = os.path.join(sge_path, job_file+".qsub")

        script =  '''#!/bin/sh\n'''
        for k,v in job_config:
            script += '#$ %s %s\n' %(k,v)
        script += '''#$ -o %s\n''' % sge_path
        script += '''#$ -e %s\n''' % sge_path
        script += '''#$ -N %s\n''' % "NPR%djobs" %len(commands)
        script += '''#$ -t 1-%d\n''' % len(commands)
        script += '''SEEDFILE=%s\n''' % cmds_file
        script += '''sh -c "`cat $SEEDFILE | head -n $SGE_TASK_ID | tail -n 1`" \n'''

        open(cmds_file, "w").write('\n'.join([cmd for cmd in commands]))
        open(qsub_file, "w").write(script)
        print qsub_file
        
    for j, cmd in jobs:
        j.save_status("R")
            
        
        
all_nodes = [ 'gen01', 'gen02', 'gen03', 'gen04', 'gen05', 'gen06',
             'gen07', 'gen08', 'gen09', 'gen10', 'gen11', 'gen12',
             'gen13', 'gen14', 'gen15', 'gen16', 'gen17', 'gen18',
             'gen19', 'gen20' ]

DEFAULT_QUEUE_NAME = "cgenomics"
DEFAULT_SGE_CELL = "cgenomics"

def build_job(commands, params, stdout, stderr, queue_name=DEFAULT_QUEUE_NAME, job_name=""):
    """ Gets a list of commands and generates a single SGE job with
    all such commands """
    os.system("mkdir -p %s" %stdout)
    os.system("mkdir -p %s" %stderr)

    TEMP = tempfile.NamedTemporaryFile(delete=False, dir=stdout)
    TEMP.write('\n'.join(commands))
    TEMP.close()

    job_name += nicepass(6)

    # Create paths....??
    script =  '''#!/bin/sh\n'''
    script += '''#$ -S /bin/bash\n'''
    script += '''#$ -o %s\n''' % stdout
    script += '''#$ -e %s\n''' % stderr
    script += '''#$ -q '%s'\n''' % queue_name
    script += '''#$ -N '%s'\n''' % job_name
    if params.nodes:
        script += '''#$ -l h='%s'\n''' % params.nodes
    script += '''#$ -p %s\n''' % params.prior
    if params.max_time:
        script += '''#$ -l h_cpu=%s\n''' % params.max_time
    if params.min_memory:
        script += '''#$ -l mem_free=%s\n''' % params.min_memory
    script += '''#$ -t 1-%d\n''' % len(commands)
    script += '''SEEDFILE=%s\n''' % TEMP.name
    script += '''sh -c "`cat $SEEDFILE | head -n $SGE_TASK_ID | tail -n 1`" \n'''
    #script += '''SEED=$(cat $SEEDFILE | head -n $SGE_TASK_ID | tail -n 1)\n'''
    #script += '''$SEED'''
    #script += 'IFS=";"\n'
    #script += 'for p in $SEED \n'
    #script += 'do\n'
    #script += '  `$p` \n'
    #script += 'done \n'
    return script

def launch_job(script, sge_cell=DEFAULT_SGE_CELL):
    TEMP = tempfile.NamedTemporaryFile(delete=False)
    TEMP.write(script)
    TEMP.close()
    answer = commands.getoutput("SGE_CELL=%s qsub %s" %(sge_cell, TEMP.name))
    OK_PATTERN = 'Your job-array ([\d]+).\d+\-\d+:\d+ \("[^"]*"\) has been submitted'
    match =  re.search(OK_PATTERN, answer)
    if match:
        jobid = match.groups()[0]
        return jobid
    else:
        raise Exception(answer)

def submit(cmds, params = None, stdout=None, stderr=None, queue_name=DEFAULT_QUEUE_NAME):
    if not stdout:
        stdout = "/users/tg/" + os.environ['USER'] + "/queue/stdout"
    if not stderr:
        stderr = "/users/tg/" + os.environ['USER'] + "/queue/stderr"
    if not params:
        params = JobParams()
    status =  launch_job( build_job(cmds, params, stdout, stderr, queue_name) )
    return status

def queue_has_jobs(sge_cell=DEFAULT_SGE_CELL, queue=None):
    if queue:
        resource = "-q %s" %queue
    else:
        resource = ""
    rawoutput = commands.getoutput("SGE_CELL=%s qstat %s" %(sge_cell, resource))
    if rawoutput:
        return len(rawoutput.split("\n"))
    else:
        return 0

def get_job_status(job, sge_cell=DEFAULT_SGE_CELL):
    ### OUTPUT EXAMPLE:
    ##
    ## job-ID  prior   name       user         state submit/start at     queue                          slots ja-task-ID
    ## -----------------------------------------------------------------------------------------------------------------
    ## 127 0.30007 tmpYW50Rl  jhuerta      r     07/15/2010 18:51:41 cgenomics@gen18.crg.es             1 141
    ## 127 0.30007 tmpYW50Rl  jhuerta      r     07/15/2010 18:51:41 cgenomics@gen19.crg.es             1 142
    ## 127 0.30007 tmpYW50Rl  jhuerta      r     07/15/2010 18:51:41 cgenomics@gen14.crg.es             1 143
    ## 127 0.30007 tmpYW50Rl  jhuerta      r     07/15/2010 18:51:41 cgenomics@gen20.crg.es             1 144
    ## 127 0.30002 tmpYW50Rl  jhuerta      qw    07/15/2010 18:51:35                                    1 145-1038:1

    # Get sge jobs stats
    job = str(job)
    rawoutput = commands.getoutput("SGE_CELL=%s qstat" %(sge_cell))
    jobs = []
    job2status = {}
    for line in rawoutput.split("\n")[2:]:
        fields = map(strip, line.split())
        job2status[fields[0]] = fields[4]
        if len(fields)==10:
            jobs.append(fields)
    # Parses info to have the everything sorted by jobid
    job2info = {}
    for jobid, prior, name, user, state, stime, queue, slots, slot_ja, slot_ta in jobs:
        job2info[jobid] = {"prior":prior, "name":name, "user":user, "state":state, "stime":stime,\
                               "queue":queue, "ja":slot_ja, "ta":slot_ta }
    # Return the state of the requested job, otherwise return "done"
    return job2status.get(job, "done")

def get_job_info(job, sge_cell=DEFAULT_SGE_CELL):
    # Get sge jobs stats
    job = str(job)
    rawoutput = commands.getoutput("SGE_CELL=%s qstat -j %s" %(sge_cell, job))
    if rawoutput.count("\n") > 5:
        return rawoutput
    else:
        return None

def cancel_job(jobid):
    pass

def clean_job_outputs(jobid):
    pass

class JobParams(object):
    def set_time(self, hours):
        try:
            self._max_time = "%d:00:00" %int(hours)
        except ValueError:
            raise ValueError("ERROR. Please specify number of hours")

    def get_time(self):
        return self._max_time

    def set_memory(self, memory):
        try:
            self._min_memory = "%dG" %abs(int(memory)/1024)
        except ValueError:
            raise ValueError("ERROR. Please specify min memory in megabytes")

    def get_memory(self):
        return self._min_memory

    def set_nodes(self, nodes):
        if type(nodes) in set([list,set,tuple,frozenset]):
            self._nodes = '|'.join([n+".crg.es" for n in map(strip, nodes)])
        else:
            raise ValueError("Error. A list of nodes was expected")

    def get_nodes(self):
        return self._nodes

    def set_prior(self, prior):
        try:
            p = int(prior)
            if p>-1 or p<-1023:
                raise ValueError("Error. A prior must be a number from -1023 to -1")
            else:
                self._prior = "%s" %p
        except ValueError:
            raise ValueError("Error. A prior must be a number from -1023 to -1" )

    def get_prior(self):
        return self._prior

    # Properties
    nodes = property(get_nodes, set_nodes)
    prior = property(get_prior, set_prior)
    min_memory = property(get_memory, set_memory)
    max_time = property(get_time, set_time)

    # Default Values
    def __init__(self):
        self._min_memory = None
        self._nodes = None
        self._max_time = None
        self._prior = "-512"
        self.set_nodes(all_nodes)

if __name__ == "__main__":
    import sys
    cmd = ' '.join(sys.argv[1:])
    if cmd:
        print "submitting", cmd
        submit([cmd])

def nicepass(alpha=6, numeric=2):
    """
    returns a human-readble password (say rol86din instead of
    a difficult to remember K8Yn9muL )
    """
    import string
    import random
    vowels = ['a','e','i','o','u']
    consonants = [a for a in string.ascii_lowercase if a not in vowels]
    digits = string.digits

    ####utility functions
    def a_part(slen):
        ret = ''
        for i in range(slen):
            if i%2 ==0:
                randid = random.randint(0,20) #number of consonants
                ret += consonants[randid]
            else:
                randid = random.randint(0,4) #number of vowels
                ret += vowels[randid]
        return ret

    def n_part(slen):
        ret = ''
        for i in range(slen):
            randid = random.randint(0,9) #number of digits
            ret += digits[randid]
        return ret

    ####
    fpl = alpha/2
    if alpha % 2 :
        fpl = int(alpha/2) + 1
    lpl = alpha - fpl

    start = a_part(fpl)
    mid = n_part(numeric)
    end = a_part(lpl)

    return "%s%s%s" % (start,mid,end)
