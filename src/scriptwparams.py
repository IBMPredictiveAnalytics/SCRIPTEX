#/***********************************************************************
# * Licensed Materials - Property of IBM 
# *
# * IBM SPSS Products: Statistics Common
# *
# * (C) Copyright IBM Corp. 1989, 2020
# *
# * US Government Users Restricted Rights - Use, duplication or disclosure
# * restricted by GSA ADP Schedule Contract with IBM Corp. 
# ************************************************************************/
# post parameters for script
"""This module provides a parameter passing mechanism for Python scripts run with the SCRIPT command via a PROGRAM
and a mechanism for the script to return a value.
The PROGRAM calls the runscript function with a parameter dictionary and script name.
The script call the getscriptparams function to retrieve a parameter dictionary"""

__version__ = '1.0.2'
__author__ = 'SPSS, JKP'

# history
#22-Oct-2008 Change mmap setup to support *nix os's.


import mmap, pickle, os, tempfile
import spss, spssaux

if os.sys.platform == "darwin":
    tempfile.tempdir="/tmp"

def runscript(scriptname, params={}):
    """Construct a parameter dictionary and run a Python script.
    
    scriptname is the path to run.
    params is a Python dictionary of parameter names and values.
    
    The total size of the parameter dictionary is limited to 4K (after pickling).
    
    This function returns a dictionary of values set by the script via setreturnvalue.
    If the script sets no return value, the result is an empty dictionary."""
    
    fnparams = tempfile.gettempdir() + os.sep + "__SCRIPT__"
    fnreturn = tempfile.gettempdir() + os.sep + "__SCRIPTRETURN__"
    f = open(fnparams, "w+")
    # ensure file size is 4096 for *nix os's.
    f.write(1024*"0000")
    f.flush()

    shmem = mmap.mmap(f.fileno(), 4096, access=mmap.ACCESS_WRITE)
    shmem.write(pickle.dumps(params))
    f.close()
    try:
        os.remove(fnreturn)   # ensure that no stale returns file exists
    except:
        pass
    ###import wingdbstub
    spss.Submit("SCRIPT " + spssaux._smartquote(scriptname))
    shmem.close()
    
    # The _SYNC command is required in order to ensure that the script has completed
    spss.Submit("_SYNC")
    
    # The parameter file will be removed by the script if it calls getscriptparam, but
    # the following code will clean up in case the script doesn't make that call.
    try:
        os.remove(fnparams)
    except:
        pass

    # get the return value, if any
    ###import wingdbstub
    try:
        f = open(fnreturn, "r")
        shmem = mmap.mmap(f.fileno(), 4096, access=mmap.ACCESS_READ)
        ret = pickle.loads(shmem.read(4096))
        shmem.close()
        f.close()
        os.remove(fnreturn)
    except:
        ret = {}
    return ret

def getscriptparams():
    """Return the script parameters, if any.
    
    The parameters are assumed to be set by the runscript function.
    The return value is a dictionary of parameter names and values.
    The parameter set is read-once.  Calling this function again will return
    an empty dictionary.
    
    If no parameters were set, the return value is an empty dictionary.
    """

    fnparams = tempfile.gettempdir() + os.sep + "__SCRIPT__"
    fnreturn = tempfile.gettempdir() + os.sep + "__SCRIPTRETURN__"
    try:
        f = open(fnparams, "r")
        shmem = mmap.mmap(f.fileno(), 4096, access=mmap.ACCESS_READ)
        ps = shmem.read(4096)
        try:
            f.close()
            shmem.close()
            os.remove(fnparams)
        except:
            pass
        try:
            os.remove(fnreturn)
        except:
            pass
    except:
        return {}
    if ord(ps[0]) == 0:
        return {}
    d =pickle.loads(ps)
    return d

def setreturnvalue(returns):
    """Create a dictionary of return values for use by the program that invoked the script.
    
    returns is a dictionary to be made available to the calling program.
    If no return value is set, retrieving it will produce an empty dictionary."""
    
    fnreturn = tempfile.gettempdir() + os.sep + "__SCRIPTRETURN__"
    f = file(fnreturn, "w+")
    # ensure file size is 4096 for *nix os's.
    f.write(1024*"0000")
    f.flush()
    shmem = mmap.mmap(f.fileno(), 4096, access=mmap.ACCESS_WRITE)
    shmem.write(pickle.dumps(returns))
    shmem.close()
    f.close()