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
import util

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

###############################################################################
# Main logic
###############################################################################
def make(aTask, dirs, rmImgQ=True):
    ## Arguments to mkImg
    args = mkArgs(dirs)
    logging.debug("args: {}".format(args))

    ## If an old image is present, delete it
    if rmImgQ and os.path.isfile(args['img']):
        os.remove(args['img'])
        logging.info("Removed an old image: {}".format(args['img']))

    ## No need to create a new image case
    if rmImgQ==False and os.path.isfile(args['img']):
        logging.info("StepWise image already exists: {}".format(args['img']))
        return {
            "status": True,
            "result": args['img']
        }

    ## Run the imaging script to generate a StepWise image
    try:
        subprocess.run([
            os.environ.get("wolframscript"),
            "-script",
            os.environ.get("mkImg"),
            util.toStr(args)],
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