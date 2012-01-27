import logging 

__LOGINDENT__ = 0

class IndentedFormatter(logging.Formatter):
    def __init__( self, fmt=None, datefmt=None ):
        logging.Formatter.__init__(self, fmt, datefmt)

    def format(self, rec ):
        rec.indent = ' ' * __LOGINDENT__
        out = logging.Formatter.format(self, rec)
        return out

def set_logindent(x):
    global __LOGINDENT__
    __LOGINDENT__ = x

def logindent(x):
    global __LOGINDENT__
    __LOGINDENT__ += x

def get_main_log(handler):
    # Prepares main log
    log = logging.getLogger("main")
    log.setLevel(26)
    log_format = IndentedFormatter("%(levelname) 7s@@1: - %(indent)s %(message)s")
    logging.addLevelName(10, "@@3,2:DEBUG")
    logging.addLevelName(20, "@@1,3:INFO")
    logging.addLevelName(22, "@@1,2:INFO")
    logging.addLevelName(24, "@@1,3:INFO")
    logging.addLevelName(26, "@@1,3:INFO")
    logging.addLevelName(28, "@@1,3:INFO")
    logging.addLevelName(30, "@@2,4:WARNING")
    logging.addLevelName(40, "@@2,5:ERROR")
    logging.addLevelName(50, "@@2,6:CRITICAL")
    log_handler = logging.StreamHandler(handler)
    log_handler.setFormatter(log_format)
    log.addHandler(log_handler)
    return log
  
