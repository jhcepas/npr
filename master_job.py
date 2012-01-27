import os
import shutil
from utils import get_md5, basename, random_string, strip, pid_up, \
    HOSTNAME
import re
import sge
import logging
log = logging.getLogger("main")

class Job(object):
    ''' A generic program launcher.

    A job is executed and monitored. Execution time, standard output
    and error are tracked into log files. The final status of the
    application is also logged. Possible status for process status are
    (W)aiting, (R)unning, (E)rror and (D)one.

    Each job generates the following info files: 

      self.status_file = join(self.jobdir, "__status__")
      self.time_file = join(self.jobdir, "__time__")
      self.stdout_file = join(self.jobdir, "__stdout__")
      self.stderr_file = join(self.jobdir, "__stderr__")
      self.pid_file = join(self.jobdir, "__pid__")

    In addition, job launching command is stored in: 

      self.cmd_file = join(self.jobdir, "__cmd__")

    '''
    def __repr__(self):
        return "Job (%s, %s)" %(self.jobname, self.jobid[:6])

    def __init__(self, bin, args, jobname=None):
        # Used at execution time
        self.jobdir = None
        self.status_file = None
        self.status = "W"
        # How to run the app
        self.bin = bin
        # command line arguments 
        self.args = args
        # Default number of cores used by the job. If more than 1,
        # this attribute should be changed
        self.cores = 1 
        self.jobname = jobname
        # generates an unique job identifier based on the params of
        # the app.
        self.jobid = get_md5(','.join(sorted([get_md5(str(pair)) for pair in 
                                              self.args.iteritems()])))
        if not self.jobname:
            self.jobname = re.sub("[^0-9a-zA-Z]", "-", basename(self.bin))

        self.ifdone_cmd = ""
        self.iffail_cmd = ""
        self.dependencies = set()

    def set_jobdir(self, basepath):
        ''' Initialize the base path for all info files associated to
        the job. '''
        #self.jobdir = os.path.join(basepath, self.jobid)
        jobname = "%s_%s" %(basename(self.bin), self.jobid[:6])
        jobname = re.sub("[^0-9a-zA-Z]", "-",jobname)

        self.jobdir = os.path.join(basepath, "%s_%s" %\
                                       (self.jobname, self.jobid[:6]))
        if not os.path.exists(self.jobdir):
            os.makedirs(self.jobdir)
        self.status_file = os.path.join(self.jobdir, "__status__")
        self.time_file = os.path.join(self.jobdir, "__time__")
        self.cmd_file = os.path.join(self.jobdir, "__cmd__")
        self.stdout_file = os.path.join(self.jobdir, "__stdout__")
        self.stderr_file = os.path.join(self.jobdir, "__stderr__")
        self.pid_file = os.path.join(self.jobdir, "__pid__")

    def write_pid(self, host, pid):
        open(self.pid_file,"w").write("%s\t%s" %(host, pid))

    def read_pid(self):
        try:
           host, pid = map(strip,
                           open(self.pid_file,"rU").readline().split("\t"))
        except IOError:
            host, pid = None, None
        else:
            pid = int(pid)
            
        return host, pid
        
    def dump_script(self):
        ''' Generates the shell script launching the job. ''' 
       
        launch_cmd = ' '.join([self.bin] + ["%s %s" %(k,v) for k,v in self.args.iteritems() if v is not None])
        lines = [
            "#!/bin/sh",
            " (echo R > %s && date > %s) &&" %(self.status_file, self.time_file),
            " (cd %s && %s && (echo D > %s; %s) || (echo E > %s; %s));" %\
                (self.jobdir, launch_cmd,  self.status_file, self.ifdone_cmd, 
                 self.status_file, self.iffail_cmd), 
            " date >> %s; " %(self.time_file),
            ]
        script = '\n'.join(lines)
        if not os.path.exists(self.jobdir):
            os.makedirs(self.jobdir)
        open(self.cmd_file, "w").write(script)

 
    def get_status(self):
        try:
            st = open(self.status_file).read(1)
        except IOError:
            st = "W"
            
        if st == "R":
            host, pid = self.read_pid()
            if host == HOSTNAME and not pid_up(pid):
                st = "L"
            elif host == "#SGE#" and sge.get_job_status(pid) == "done":
                st = "L"

        self.status = st
        return self.status

    def clean(self):
        shutil.rmtree(self.jobdir)
