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
def run(aTask):
    logging.debug('run tasks')
    logging.debug(aTask)

    # Remove some fields
    for f in ['started', 'finished']:
        aTask.pop(f)

    # Run the testing script on a task
    try:
        subprocess.run([
            os.environ.get("wolframscript"),
            "-script",
            os.environ.get("runTask"),
            util.toStr(aTask)],
            timeout=int(os.environ.get("runTaskTime")), check=True
        )
    except subprocess.CalledProcessError as err:
        return {
            "status": False,
            "result": "Error from runTask.wl"
        }
    except TimeoutExpired as err:
        return {
            "status": False,
            "result": "runTask.wl didn't end in time"
        }
