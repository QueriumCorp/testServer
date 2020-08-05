###############################################################################
# test.py
# Testing module
###############################################################################
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
import dbConn

def next(statusCurr="pending", statusNext="acquired", queryAdd="LIMIT 1"):
    tbl = "testPath"
    colsRtrn = dbConn.getFields("testPath")
    rslt = dbConn.getRow(
        tbl,
        ["status"], [statusCurr],
        colsRtrn, queryAdd)
    ## If no pending task return {}
    if rslt==None or len(rslt)<1:
        return {}
    ## Make a dictionary of the result
    rslt = dbConn.mkObj(colsRtrn, rslt)

    ## Update status and started fields
    dbConn.modMultiVals(
        tbl,
        ["id"], [rslt["id"]],
        ["status"], [statusNext]
    )
    return rslt