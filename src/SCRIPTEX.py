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
"""This module implements the SCRIPTEX extension command.  It uses
scriptwparams for passing parameter values and retrieving results."""

__author__ = "SPSS, JKP"
__version__ = "1.0.3"


import spss
import scriptwparams
from extension import Template, Syntax, setnegativedefaults
import sys, inspect

helptext = r"""SCRIPTEX SCRIPT=filespecification
[/PARAMETERS parmname = value parmname = value ...]
[/HELP].

filespecification is the name of the Python script to run.

The optional PARAMETERS subcommand accepts one or more specifications of the form
parametername = value
that will be passed to the script.  Note that the case of the parameter name should match
the case expected by the script.

/HELP prints this help and does nothing else.

In a Python program, it is possible for a script to return a value or values, but this is not
accessible through regular syntax."""

def Run(args):
    """Execute the SCRIPTEX command"""

    args = args[list(args.keys())[0]]
   ###print args   #debug

    oobj = Syntax([
        Template("SCRIPT", subc="",  ktype="literal", var="scriptname"),
        Template("", subc="PARAMETERS",  ktype="literal", var="params", islist=True),
        Template("HELP", subc="", ktype="bool")])
    
    # A HELP subcommand overrides all else
    if "HELP" in args:
        #print helptext
        helper()
    else:
        oobj.parsecmd(args)
        try:
            # check for missing required parameters
            args, junk, junk, deflts = inspect.getargspec(scriptwparams.runscript)
            args = set(args[: len(args) - len(deflts)])    # the required arguments
            omitted = [item for item in args if not item in oobj.parsedparams]
            if omitted:
                raise ValueError("The following required parameters were not supplied:\n" + ", ".join(omitted))
            oobj.parsedparams["params"] = dictFromTokenList(oobj.parsedparams.get("params", {}))
            scriptwparams.runscript(**oobj.parsedparams)
        except:
            # Exception messages are printed here, but the exception is not propagated, and tracebacks are suppressed,
            # because as an Extension command, the Python handling should be suppressed.
            print("Error:", sys.exc_info()[1])
            sys.exc_clear()
        
def dictFromTokenList(paramlist):
    """Return a dictionary formed from the terms in paramlist.
    
    paramlist is a sequence of items in the form
    parametername, =, value.
    If there are duplicates, the last one wins."""
    
    ret = {}
    msg = "Ill-formed parameter list: keywords and values must have the form kw = value"
    
    if not len(paramlist) % 3 == 0:
        raise ValueError(msg)
    for i in range(0, len(paramlist), 3):
        if not paramlist[i+1] == "=":
            raise ValueError(msg)
        ret[paramlist[i]] = paramlist[i+2]
    return ret

def helper():
    """open html help in default browser window
    
    The location is computed from the current module name"""
    
    import webbrowser, os.path
    
    path = os.path.splitext(__file__)[0]
    helpspec = "file://" + path + os.path.sep + \
         "markdown.html"
    
    # webbrowser.open seems not to work well
    browser = webbrowser.get()
    if not browser.open_new(helpspec):
        print(("Help file not found:" + helpspec))    
try:    #override
    from extension import helper
except:
    pass    