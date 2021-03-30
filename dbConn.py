###############################################################################
# dbConn.py
# MySQL module

# Requirements
# Python >= 3.4

# Need the following modules
# python3 -m pip install mysql-connector-python

###############################################################################
from dotenv import load_dotenv
load_dotenv()
from mysql.connector import errorcode
import mysql.connector
import os
import json
import logging
import sys

###############################################################################
# Support functions
###############################################################################

#######################################
# Make objects
#######################################
def mkObj(keys, data):
    return dict(zip(keys, data))

def mkObjs(keys, data):
    return list(map(lambda aRow: dict(zip(keys, aRow)), data))

#######################################
# Get fiedls in a table
#######################################
def getFields(tbl):
    switcher = {
        "testSchedule": [
            "id","name","jira","author","gradeStyle","policies","skipStatuses",
            "status","limitPaths","priority","limitPathTime","host","pid","gitBranch","gitHash","mmaVersion","timeOutTime",
            "ruleMatchTimeOutTime","msg","jiraResp","started","finished","created"
            ],
        "testPath": [
            "id","schedule_id","question_id","path_id","trace_id","diff_id","author",
            "gradeStyle","policies","status","ref_id","priority",
            "limitPathTime","pid","stepCount","stepsCompleted","timeCompleted",
            "host","gitBranch","gitHash","mmaVersion","timeOutTime",
            "ruleMatchTimeOutTime","msg","started","finished"
            ]
    }

    return switcher.get(tbl, [])

###############################################################################
# Main logic
###############################################################################

#######################################
# Execute an sql query and return fetchall
# parameters:
# query: sql query in string
# vals: a tuple of values
#######################################
def exec(query, cmd="fetchall", vals=tuple()):
    try:
        conn = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASS'),
            database=os.environ.get('DB_NAME'),
        )
        with conn.cursor() as cursor:
            cursor.execute(query, vals)
            if (cmd == "fetchall"):
                return cursor.fetchall()
            elif (cmd == "fetchone"):
                return cursor.fetchone()
            elif (cmd == "commit"):
                conn.commit()
            else:
                logging.error("Invalid cmd")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    finally:
        conn.close()

#######################################
# Get a row from a table based on the condition pair of
# cols and vals
# parameters:
# tbl: a table name
# cols: a list of fields for query condition
# vals: a list of values for the fields
# colsRtrn: a list of fields to be returned
# [fltr]: additional query attributes
#######################################
def getRow(tbl, cols, vals, colsRtrn, fltr="LIMIT 1"):
    sqlRtrn = ",".join(colsRtrn)
    sqlCond = "=%s AND ".join(cols) + "=%s "
    sql = "SELECT {flds} FROM {tbl} WHERE {cond} {fltr};".format(
        flds=sqlRtrn, tbl=tbl, cond=sqlCond, fltr=fltr)
    logging.debug("getRow-sql: {}".format(sql))

    rslt = exec(sql, vals=tuple(vals))
    return rslt

#######################################
# Get paths in a question
# parameters:
# identifier: unq or id of a question
# statuses: a list of path status to get
# colsRtrn: a list of fields to be returned
# [fltr]: additional query attributes
# [flat]: flatten the result
#######################################
def getPathsInQstn(identifier, statuses, colsRtrn, fltr="", flat=True):
    rtrn = ",".join(colsRtrn)
    stts = "\"" + "\",\"".join(statuses) + "\""

    sqlQstn = identifier
    if isinstance(identifier, str):
        sqlQstn = "SELECT id FROM question WHERE unq='{unq}'".format(
            unq=identifier)
    sqlPath = "SELECT path_id FROM question_path WHERE "
    sqlPath += "question_id IN ({sqlQstn})".format(sqlQstn=sqlQstn)
    sqlStts = "" if len(
        statuses) == 0 else "status NOT IN ({stts}) AND ".format(stts=stts)

    sql = "SELECT {rtrn} FROM path WHERE {sqlStts} id IN ({sqlPath}) {fltr};".format(
        rtrn=rtrn, sqlStts=sqlStts, sqlPath=sqlPath, fltr=fltr)
    logging.debug("getPathsInQstn - sql: {sql}".format(sql=sql))

    rslt = exec(sql)
    return [item[0] for item in rslt] if flat else rslt


#######################################
# Add rows in testPath
# parameters:
# data: list of dictionaries. The dictionary keys are fields in testPath.
# NOTE: some keys may not be valid fields, so extract only field keys from dict
#######################################
def addTestPaths(data):
    tbl = "testPath"
    # Get only valid field keys in data because data may contain keys that
    # are not valid fields in testPath.
    keys = set(getFields(tbl)).intersection(set(data[0].keys()))

    # Build a sql query for inserting multiple rows
    sqlKeys = ",".join(keys)
    sqlPh = ",".join(["("+",".join(["%s"]*len(keys))+")"]*len(data))
    sqlVals = [i for row in data for i in [row[k] for k in keys]]
    sql = "INSERT INTO {tbl} ({sqlKeys}) VALUES {sqlPh}".format(
        tbl=tbl, sqlKeys=sqlKeys, sqlPh=sqlPh)
    # logging.debug("addTestPaths - sql: {sql}".format(sql=sql))

    exec(sql, cmd="commit", vals=tuple(sqlVals))


#######################################
# Fetch all in a sql query
# parameters:
#######################################
def fetchallQuery(sql, vals, fldsRtrn=[], mkObjQ=False):
    valTuple = tuple(vals) if not isinstance(vals, tuple) else vals
    result = exec(sql, cmd="fetchall", vals=valTuple)

    if mkObjQ:
        return mkObjs(fldsRtrn, result)

    return result


#######################################
# Run a sql query
# parameters:
#######################################
def execQuery(sql, vals, fldsRtrn=[], mkObjQ=False):
    valTuple = tuple(vals) if not isinstance(vals, tuple) else vals
    exec(sql, cmd="commit", vals=valTuple)


#######################################
# Update a table in the database
# parameters:
#######################################
def modTbl(tbl, colsCond, valsCond, col, val):
    sqlCond = "=%s AND ".join(colsCond)+"=%s "
    sql = "UPDATE {tbl} SET {col}='{val}' WHERE {sqlCond};".format(
        tbl=tbl, col=col, val=val, sqlCond=sqlCond)
    logging.debug("modTbl - sql: {sql}".format(sql=sql))

    exec(sql, cmd="commit", vals=tuple(valsCond))

def modMultiVals(tbl, colsCond, valsCond, cols, vals, fltr=""):
    sqlSet = "=%s,".join(cols)+"=%s"
    sqlCond = "=%s AND ".join(colsCond)+"=%s "
    sql = "UPDATE {tbl} SET {sqlSet} WHERE {sqlCond} {fltr};".format(
        tbl=tbl, sqlSet=sqlSet, sqlCond=sqlCond, fltr=fltr)
    logging.debug("modMultiVals - sql: {sql}".format(sql=sql))

    exec(sql, cmd="commit", vals=tuple(vals + valsCond))