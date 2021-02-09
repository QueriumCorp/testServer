###############################################################################
# test.py
# Testing module
###############################################################################
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
import dbConn
import logging
import os
import subprocess
from subprocess import TimeoutExpired
import util
import sys


def next(statusCurr="pending", statusNext="acquired", queryAdd="LIMIT 1"):
    tbl = "testPath"
    colsRtrn = dbConn.getFields("testPath")
    rslt = dbConn.getRow(
        tbl,
        ["status"], [statusCurr],
        colsRtrn, queryAdd)
    ## If no pending task return {}
    if rslt==None or len(rslt)<1:
        return []
    ## Make a dictionary of the result
    rslt = dbConn.mkObj(colsRtrn, rslt[0])
    logging.debug("task-next id: {}".format(rslt["id"]))

    ## Update status and started fields
    dbConn.modMultiVals(
        tbl,
        ["id"], [rslt["id"]],
        ["status", "host", "pid"],
        [statusNext, os.environ.get('serverHost'), os.getpid()]
    )
    return rslt

def run(aTask):
    logging.debug('run tasks')
    logging.debug(aTask)

    ## Remove some fields
    for f in ['started', 'finished']:
        aTask.pop(f)

    ## Run the testing script on a task
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