###############################################################################
# repo.py
# Install the following module
# python3 -m pip install gitpython
###############################################################################
from dotenv import load_dotenv
load_dotenv()
import logging
import os
import sys
import json
import subprocess
from subprocess import TimeoutExpired

###############################################################################
# Support functions
###############################################################################

#######################################
# Generate arguments
#######################################
def mkArgs(dirs):
    argInTesting = os.environ.get("InTesting").lower()
    result = {
        "dirCommonCore": dirs['dirRepo'],
        "img": os.path.join(dirs['dirImg'], os.environ.get("fileImg")),
        "InTesting": True if argInTesting=="true" else False,
    }

    return result

#######################################
#
#######################################
def toStr(data):
    if sys.platform == 'linux':
        return json.dumps(json.dumps(data, separators=(',', ':')))

    return json.dumps(data, separators=(',', ':'))

###############################################################################
# Main logic
###############################################################################
def make(aTask, dirs):
    ## Arguments to mkImg
    args = mkArgs(dirs)
    print("args:", args)

    ## Run the imaging script to generate a StepWise image
    try:
        subprocess.run([
            os.environ.get("wolframscript"),
            "-script",
            os.environ.get("mkImg"),
            toStr(args)],
            timeout=int(os.environ.get("mkImgTime")), check=True
        )
    except subprocess.CalledProcessError as err:
        return {
            "status": False,
            "result": "Error from the mkImg script"
        }
    except TimeoutExpired as err:
        return {
            "status": False,
            "result": "Timeout error in making image"
        }

    ## Verify the StepWise image was generated
    if not os.path.isfile(args['img']):
        return {
            "status": False,
            "result": "Failed to make a StepWise image"
        }

    return {
        "status": True,
        "result": args['img']
    }