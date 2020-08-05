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
import multiprocessing
import subprocess
from subprocess import TimeoutExpired

import os
import time
import sys
import json

import test
import task

EXITCODE_NOMMA = 5
EXITCODE_NOLICENSE = 6
EXITCODE_IMGFAIL = 7
EXITCODE_REPOFAIL = 8
EXITCODE_BADMAINPATH = 9
EXITCODE_INVALIDREF = 10

logging.basicConfig(level=logging.DEBUG)

###############################################################################
# Support functions
###############################################################################

#######################################
# Initialize a server
#######################################
def init():
    ## Create a directory for the CommonCore repos
    if not os.path.isdir(os.environ.get('dirTest')):
        print("Created a testing directory:", os.environ.get('dirTest'))
        os.mkdir(os.environ.get('dirTest'))

#######################################
# Manage dead processes
#######################################
def manageDead():
    ## Locate dead processes
    deadList = []
    for i in range(len(PROCESSES)):
        if not PROCESSES[i].is_alive():
            logging.debug(f"PROCESS is DEAD: {i}")
            deadList.append(i)
        else:
            logging.debug(f"PROCESS is ALIVE: {i}")
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
    testFile = os.path.join(os.getcwd(), "testScript.wl")
    if not os.path.isfile(testFile):
        logging.warning(f"Missing: {testFile}")

    ## Run wolframScript to test Mathematica license availability
    try:
        rslt = subprocess.check_output([
            os.environ.get('wolframscript'),
            "-script",
            testFile], timeout=5
        )
    except subprocess.TimeoutExpired as er:
        logging.info("testScrip run too long: TimeoutExpired")
        return False

    if os.environ.get('testResult') not in rslt.decode("utf-8"):
        logging.info("No license is available")
        return False

    return True

#######################################
# Check any pending tasks in testPath
#######################################
def gotPendingTaskQ(status="pending"):

    logging.info(f"{os.getpid()}: gotPendingTask")
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
        logging.debug("All licenses are in use")
        return False

    ## Verify availability of of a Mathematica license
    if not gotLicenseQ():
        logging.debug("Unable to acquire a license")
        return False

    return True

def aProcess(lock):
    logging.info(f"{os.getpid()}: Starting a process")

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

        ## Make a StepWise image

    except SystemExit as e:
        if e.code == EXITCODE_NOMMA:
            logging.info(f"{os.getpid()}: No pending task")
        if e.code == EXITCODE_NOLICENSE:
            logging.info(f"{os.getpid()}: No Mathematica license")
        if e.code == EXITCODE_IMGFAIL:
            logging.info(f"{os.getpid()}: Failed on making a StepWise image")
        if e.code == EXITCODE_REPOFAIL:
            logging.info(f"{os.getpid()}: Failed on cloning the CommonCore repo")
        if e.code == EXITCODE_BADMAINPATH:
            logging.info(f"{os.getpid()}: Invalid main path")
        runTestingQ = False
    finally:
        lock.release()

    if runTestingQ==True:
        logging.info(f"{os.getpid()}: running the test code!")
        time.sleep(5)


###############################################################################
#   Main
###############################################################################
if __name__ == '__main__':

    ### testing code
    test.taskNext()
    sys.exit(0)

    ### init the environment
    init()

    ## Create a lock for handling critical section among multiple processes
    LOCK = multiprocessing.Lock()
    ## Number of processes depends on # of available Mathematica licenses
    PROCESSES = []

    while True:
        ## Kill expired and hang processes
        killRougeProcesses()

        ## Start process if any free license and pending task
        if not startProcQ():
            time.sleep(int(os.environ.get('sleepTime')))
            continue

        aProc = multiprocessing.Process(target=aProcess, args=(LOCK,))
        PROCESSES.append(aProc)
        aProc.start()