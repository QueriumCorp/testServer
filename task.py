###############################################################################
# test.py
# Testing module
###############################################################################
import sys
import util
from subprocess import TimeoutExpired
import subprocess
import os
import logging
import dbConn
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

#######################################
# Test any pending task
#######################################
def taskInStatusQ(status="pending"):
    tbl = "testPath"

    # Get the ID of a pending task
    rslt = dbConn.getRow(tbl, ["status"], ["pending"],["id"])

    # If no pending task return False
    if rslt == None or len(rslt) < 1:
        return False

    return True

#######################################
# To prevent multiple testServers acquiring the same task, change
# status, host, and pid fields to "acquired", serverHost, and process ID,
# respectively. Then get the task
# parameters:
# taskId: return a given task ID
#######################################
def next(
    statusCurr="pending", statusNext="acquired", taskId=0, queryAdd="LIMIT 1"):
    tbl = "testPath"

    # Update status and started fields
    pid = os.getpid()
    if taskId>0:
        dbConn.modMultiVals(
            tbl,
            ["id"], [taskId],
            ["status", "host", "pid"],
            [statusNext, os.environ.get('serverHost'), pid],
            fltr="LIMIT 1"
        )
    else:
        dbConn.modMultiVals(
            tbl,
            ["status"], [statusCurr],
            ["status", "host", "pid"],
            [statusNext, os.environ.get('serverHost'), pid],
            fltr="ORDER BY priority DESC LIMIT 1"
        )

    # Get the task
    colsRtrn = dbConn.getFields("testPath")
    if taskId > 0:
        rslt = dbConn.getRow(
            tbl,
            ["id"],[taskId],
            colsRtrn, queryAdd)
    else:
        rslt = dbConn.getRow(
            tbl,
            ["status", "host", "pid"],
            [statusNext, os.environ.get('serverHost'), pid],
            colsRtrn, queryAdd)

    # If no pending task return {}
    if rslt == None or len(rslt) < 1:
        return {}

    # Make a dictionary of the result
    rslt = dbConn.mkObj(colsRtrn, rslt[0])
    logging.debug("task-next id: {}".format(rslt["id"]))

    return rslt

#######################################
# Run a test task
# parameters:
#######################################


#######################################
# Run a test task
# parameters:
#######################################
def run(aTask):
    logging.debug(aTask)

    # Remove some fields
    for f in ['started', 'finished']:
        aTask.pop(f)

    # Run the testing script on a task
    try:
        # Configure stdout setting for Mma
        mmaPrompt = subprocess.DEVNULL
        if os.environ.get("mmaPromptOn").lower() == "true":
            mmaPrompt = None

        subprocess.run([
            os.environ.get("wolframscript"),
            "-script",
            os.environ.get("runTask"),
            util.toJsonStr(aTask)],
            timeout=int(aTask["limitPathTime"])+60,
            check=True,
            stdout=mmaPrompt
        )

    except subprocess.CalledProcessError:
        msg = "Error from runTask.wl"
        dbConn.modMultiVals("testPath", ["id"], [aTask["id"]],
            ["status", "msg"], ["fail", msg])
        logging.error("Task {id} failed: {msg}".format(
            id=aTask["id"], msg=msg))
    except TimeoutExpired:
        msg = "runTask.wl didn't end in time"
        dbConn.modMultiVals("testPath", ["id"], [aTask["id"]],
            ["status", "msg"], ["fail", msg])
        logging.error("Task {id} failed: {msg}".format(
            id=aTask["id"], msg=msg))
    except:
        msg = "Unknown error"
        dbConn.modMultiVals("testPath", ["id"], [aTask["id"]],
            ["status", "msg"], ["fail", msg])
        logging.error("Task {id} failed: {msg}".format(
            id=aTask["id"], msg=msg))