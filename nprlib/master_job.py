import os
import shutil
import re
import sge
import db
import logging
log = logging.getLogger("main")

from nprlib.utils import md5, basename, random_string, strip, pid_up, HOSTNAME

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

    def __init__(self, bin, args, jobname=None, parent_ids=None):
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
        self.exec_type = "insitu"
        self.jobname = jobname
        # generates an unique job identifier based on the params of
        # the app.
        self.jobid = md5(','.join(sorted([md5(str(pair)) for pair in 
                                           self.args.iteritems()])))
        if parent_ids:
            self.jobid = md5(','.join(sorted(parent_ids+[self.jobid])))

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
            host, pid = "", ""
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
 
    def get_status(self, sge_jobs=None):
        # Finished status:
        #  E.rror
        #  D.one
        # In execution status:
        #  W.ating
        #  Q.ueued
        #  R.unning
        #  L.ost
        if self.status not in set("DE"):
            jinfo = db.get_task_info(self.jobid)
            self.host = jinfo.get("host", None) or ""
            self.pid = jinfo.get("pid", None) or ""

            saved_status = jinfo.get("status", None)
            try:
                st = open(self.status_file).read(1)
            except IOError:
                st = saved_status
            
            #if st is None:
            #    db.add_task(self.jobid, status="W")
            #    st = saved_status = "W"

            # If this is in execution, tries to track the job
            if st in set("QRL"):
                if self.host.startswith("@sge"):
                    sge_st = sge_jobs.get(self.pid, {}).get("state", None)
                    log.debug("%s %s", self, sge_st)
                    if not sge_st:
                        log.debug("%s %s %s", self, sge_st, self.pid)
                        st = "L"
                    elif "E" in sge_st:
                        pass
                elif self.host == HOSTNAME and not pid_up(self.pid):
                    st = "L"
        
            if st != saved_status:
                db.update_task(self.jobid, status=st)
            self.status = st
            
        return self.status

    def save_status(self, status):
        open(self.status_file, "w").write(status)
        
    def clean(self):
        shutil.rmtree(self.jobdir)


