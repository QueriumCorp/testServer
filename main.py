###############################################################################
# main.py
# The main module

# Requirements
# Python >= 3.4
# Git 1.7.0 or newer

# Need the following modules
# python3 -m pip install python-dotenv
# python3 -m pip install PyMySQL
# python3 -m pip install psutil
# python3 -m pip install gitpython

# To run
# python3 main.py
###############################################################################
from dotenv import load_dotenv
load_dotenv()
import logging
from multiprocessing import log_to_stderr, get_logger
import multiprocessing
import subprocess
from subprocess import TimeoutExpired

import os
import time
import sys
import json

import task
import gitRepo
import dbConn
import image

EXITCODE_NOMMA = 5
EXITCODE_NOLICENSE = 6
EXITCODE_IMGFAIL = 7
EXITCODE_REPOFAIL = 8
EXITCODE_BADMAINPATH = 9
EXITCODE_INVALIDREF = 10

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, %(process)d-%(levelname)s: %(message)s')
# log_to_stderr()
# logger = get_logger()
# logger.setLevel(logging.INFO)

###############################################################################
# Support functions
###############################################################################

#######################################
# Initialize a server
#######################################
def init():
    ## Create a directory for the CommonCore repos
    if not os.path.isdir(os.environ.get('dirTest')):
        os.mkdir(os.environ.get('dirTest'))
        logging.info("Created a testing directory: {}".format(
            os.environ.get('dirTest')))

#######################################
# Manage dead processes
#######################################
def manageDead():
    ## Locate dead processes
    deadList = []
    for i in range(len(PROCESSES)):
        if not PROCESSES[i].is_alive():
            logging.debug("PROCESS is DEAD: {}".format(i))
            deadList.append(i)
        else:
            logging.debug("PROCESS is ALIVE: {}".format(i))
    ## Pop the dead PROCESSES in the descending order by their index:
    ## largest to smallest index, Otherwise, running processes can get popped
    deadList.sort(reverse=True)
    for i in deadList:
        PROCESSES.pop(i)

###############################################################################
# Check for Mathematica license availability
###############################################################################
def gotLicenseQ():

    ## Verify the test script
    if not os.path.isfile(os.environ.get('testScript')):
        logging.warning("gotLicenseQ - Missing testScript: {}".format(
            os.environ.get('testScript')))

    ## Run wolframScript to test Mathematica license availability
    try:
        rslt = subprocess.check_output([
            os.environ.get('wolframscript'),
            "-script",
            os.environ.get('testScript')], timeout=5
        )
    except subprocess.TimeoutExpired:
        logging.error("gotLicenseQ - TimeoutExpired")
        return False
    except:
        logging.error("gotLicenseQ - Unknown error")
        return False
    else:
        if os.environ.get('testResult') not in rslt.decode("utf-8"):
            logging.warning("gotLicenseQ - No license is available")
            return False
        else:
            return True

    return False

#######################################
# Check any pending tasks in testPath
#######################################
def gotPendingTaskQ(status="pending"):

    logging.info("{}: gotPendingTask".format(os.getpid()))
    time.sleep(5)
    return []

#######################################
# Handle bad processes
#######################################
def killRougeProcesses():
    logging.debug("killRougeProcesses")
    ## Kill Mathematica processes that got stuck
    ## Kill Mathematica processes that are hang after completing their tasks

#######################################
# Start a new process
#######################################
def startProcQ():
    # Manage dead processes
    manageDead()

    ## Verify not all of the license are used
    if len(PROCESSES)>=int(os.environ.get('licenseLimit')):
        logging.info("All licenses are in use")
        return False

    ## Verify availability of of a Mathematica license
    if not gotLicenseQ():
        return False

    ## Check if there is any pending tasks in testPath
    if not task.taskInStatusQ():
        logging.debug("No pending tasks")
        return False

    return True

def aProcess(lock):
    logging.info("Starting a process")

    runTestingQ = True
    lock.acquire()
    try:
        ## Is there a Mathematica license
        if not gotLicenseQ():
            sys.exit(EXITCODE_NOLICENSE)

        ## Get a pending mma info
        aTask = task.next()
        if len(aTask)<1:
            sys.exit(EXITCODE_NOMMA)

        ## Clone the CommonCore repo
        env = gitRepo.mkEnv(aTask)
        if env['status'] == False:
            dbConn.modMultiVals(
                'testPath',
                ['id'], [aTask['id']],
                ['status', 'msg'], ['fail', env['result']]
            )
            sys.exit(EXITCODE_REPOFAIL)

        ## Make a StepWise image
        img = image.make(aTask, env['result'])
        if img['status'] == False:
            dbConn.modMultiVals(
                'testPath',
                ['id'], [aTask['id']],
                ['status', 'msg'], ['fail', img['result']]
            )
            sys.exit(EXITCODE_IMGFAIL)

    except SystemExit as e:
        if e.code == EXITCODE_NOMMA:
            logging.info("No pending task")
        # if e.code == EXITCODE_NOLICENSE:
            # logging.warning("No Mathematica license")
        if e.code == EXITCODE_IMGFAIL:
            logging.error("Failed on making a StepWise image")
        if e.code == EXITCODE_REPOFAIL:
            logging.error("Failed on cloning the CommonCore repo")
        if e.code == EXITCODE_BADMAINPATH:
            logging.error("Invalid main path")
        runTestingQ = False
    except:
        logging.error("Unexpected error")
        runTestingQ = False
    finally:
        lock.release()

    if runTestingQ:
        ## Add some environment variables into a task
        aTask["dirCommonCore"] = env['result']['dirRepo']
        aTask["loadFromImgOn"] = True \
            if os.environ.get("loadFromImgOn").lower()=="true" else False
        aTask["img"] = img['result']

        logging.info("Testing Task {id} .....".format(id=aTask["id"]))
        task.run(aTask)
        time.sleep(5)


###############################################################################
#   Main
###############################################################################
if __name__ == '__main__':

    ### init the environment
    init()

    ## Create a lock for handling critical section among multiple processes
    LOCK = multiprocessing.Lock()
    ## Number of processes depends on # of available Mathematica licenses
    PROCESSES = []

    terminateQ = False
    while not terminateQ:
        try:
            ## Kill expired and hang processes
            # killRougeProcesses() - may need to be implemented in the future

            ## Start process if any free license and pending task
            if not startProcQ():
                time.sleep(int(os.environ.get('sleepTime')))
                continue

            aProc = multiprocessing.Process(target=aProcess, args=(LOCK,))
            PROCESSES.append(aProc)
            aProc.start()
            # aProc.join()
        except KeyboardInterrupt:
            ### Add cleanup code if needed
            # wait for all the process to finish
            for p in PROCESSES:
                p.join()
            terminateQ = True
        except multiprocessing.ProcessError as err:
            logging.error(err)

