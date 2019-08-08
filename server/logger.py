import logging
import server.constants as constants
import os
import sys

def create_logger(name, silent=False, verbose=False):
    '''Creates a logger instance that can be used to log console and file level outputs.'''
    root = logging.getLogger()
    logger = logging.getLogger(name=name)
    root.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)

    if not os.path.exists(constants.LOG_PATH):
        os.umask(000)
        os.mkdir(constants.LOG_PATH)

    formatter = logging.Formatter(constants.LOG_FMT)
    fh = logging.FileHandler(constants.LOG_FILE)
    ch = logging.StreamHandler(sys.stdout)
    
    ch.setLevel(logging.INFO) if not silent else ch.setLevel(logging.WARNING)
    fh.setLevel(logging.INFO) if not silent else fh.setLevel(logging.WARNING)

    if verbose:
        ch.setLevel(logging.DEBUG)
        fh.setLevel(logging.DEBUG)

    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger