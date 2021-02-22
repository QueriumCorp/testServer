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
logging.basicConfig(level=logging.INFO)

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
    testFile = os.path.join(os.getcwd(), "testScript.wl")
    if not os.path.isfile(testFile):
        logging.warning("Missing: {}".format(testFile))

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
        logging.debug("All licenses are in use")
        return False

    ## Verify availability of of a Mathematica license
    if not gotLicenseQ():
        logging.debug("Unable to acquire a license")
        return False

    return True

def aProcess(lock):
    logging.info("{}: Starting a process".format(os.getpid()))

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
        if env['status']==False:
            dbConn.modMultiVals(
                'testPath',
                ['id'], [aTask['id']],
                ['status', 'msg'], ['failed', env['result']]
            )
            sys.exit(EXITCODE_REPOFAIL)

        ## Make a StepWise image
        img = image.make(aTask, env['result'])
        if img['status']==False:
            dbConn.modMultiVals(
                'testPath',
                ['id'], [aTask['id']],
                ['status', 'msg'], ['failed', img['result']]
            )
            sys.exit(EXITCODE_IMGFAIL)

    except SystemExit as e:
        if e.code == EXITCODE_NOMMA:
            logging.info("{}: No pending task".format(os.getpid()))
        if e.code == EXITCODE_NOLICENSE:
            logging.warning("{}: No Mathematica license".format(os.getpid()))
        if e.code == EXITCODE_IMGFAIL:
            logging.error("{}: Failed on making a StepWise image".format(
                os.getpid()
            ))
        if e.code == EXITCODE_REPOFAIL:
            logging.error(
                "{}: Failed on cloning the CommonCore repo".format(os.getpid()))
        if e.code == EXITCODE_BADMAINPATH:
            logging.error("{}: Invalid main path".format(os.getpid()))
    except:
        logging.error("{}: Unexpected error".format(os.getpid()))
    else:
        ## Add some environment variables into a task
        aTask["dirCommonCore"] = env['result']['dirRepo']
        aTask["loadFromImgOn"] = True \
            if os.environ.get("loadFromImgOn").lower()=="true" else False
        aTask["img"] = img['result']

        logging.info("{}: running a task in mma .....".format(os.getpid()))
        task.run(aTask)
        time.sleep(5)
    finally:
        lock.release()


#######################################
# Testing
#######################################
def testing():
    # test.modByPriority()
    # test.taskNext()
    # test.modMultiVals()
    # test.repoDir()
    # test.repo()
    # test.allDir()
    # test.mkImg()
    test.runTask()

    sys.exit(0)

###############################################################################
#   Main
###############################################################################
if __name__ == '__main__':

    ### testing code
    # testing()

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
            killRougeProcesses()

            ## Start process if any free license and pending task
            if not startProcQ():
                time.sleep(int(os.environ.get('sleepTime')))
                continue

            aProc = multiprocessing.Process(target=aProcess, args=(LOCK,))
            PROCESSES.append(aProc)
            aProc.start()
        except KeyboardInterrupt:
            ### Add cleanup code if needed
            terminateQ = True
        except multiprocessing.ProcessError as err:
            logging.error(err)

