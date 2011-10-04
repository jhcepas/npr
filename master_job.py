import os
import shutil
from utils import get_md5, basename

class Job(object):
    ''' A generic program launcher prepared to interact with the Task
    class.

    A job is executed and monitored. Execution time,
    standard output and error are tracked in log files. The final
    status of the application is also logged. Possible status for
    process status are (W)aiting, (R)unning, (E)rror and (D)one.
    '''
    def __repr__(self):
        return "Job (%s-%s)" %(basename(self.bin), self.jobid[:8])

    def __init__(self, bin, args):
        # Used at execution time
        self.jobdir = None
        self.status_file = None
        # How to run the app
        self.bin = bin
        self.args = args
        # generates an unique job identifier based on the params of
        # the app.
        self.jobid = get_md5(','.join(sorted([get_md5(str(pair)) for pair in 
                                              self.args.iteritems()])))
        self.ifdone_cmd = ""
        self.iffail_cmd = ""

    def set_jobdir(self, basepath):
        self.jobdir = os.path.join(basepath, self.jobid)
        if not os.path.exists(self.jobdir):
            os.makedirs(self.jobdir)
        self.status_file = os.path.join(self.jobdir, "__status__")
        self.time_file = os.path.join(self.jobdir, "__time__")
        self.cmd_file = os.path.join(self.jobdir, "__cmd__")
        self.stdout_file = os.path.join(self.jobdir, "__stdout__")
        self.stderr_file = os.path.join(self.jobdir, "__stderr__")
        
    def dump_script(self):
        launch_cmd = ' '.join([self.bin] + ["%s %s" %(k,v) for k,v in self.args.iteritems() if v is not None])
        lines = [
            "#!/bin/sh",
            "(echo R > %s && date > %s) &&" %(self.status_file, self.time_file),
            "(cd %s && %s && (echo D > %s; %s) || (echo E > %s; %s));" %\
                (self.jobdir, launch_cmd,  self.status_file, self.ifdone_cmd, 
                 self.status_file, self.iffail_cmd), 
            "date >> %s; " %(self.time_file),
            ]
        script = '\n'.join(lines)
        if not os.path.exists(self.jobdir):
            os.makedirs(self.jobdir)
        open(self.cmd_file, "w").write(script)
 
    def status(self):
        if not os.path.exists(self.status_file):
            return "W"
        else:
            return open(self.status_file).read(1)
   
    def clean(self):
        shutil.rmtree(self.jobdir)
