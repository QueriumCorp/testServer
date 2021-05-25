###############################################################################
# Testing module
# python3 test_mysql.py
###############################################################################
import sys
import dbConn
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
import logging

logging.basicConfig(level=logging.DEBUG)

def getRow():
    tbl = "testSchedule"
    cols = ["status"]
    vals = ["reported"]
    rtrns = ["id", "status"]
    rslt = dbConn.getRow(tbl, cols, vals, rtrns, fltr="")
    print (rslt)

def testConn():
    print("host: {}".format(os.environ.get('DB_HOST')))
    print("host: {}".format(os.environ.get('DB_USER')))
    print("host: {}".format(os.environ.get('DB_PASS')))
    print("host: {}".format(os.environ.get('DB_NAME')))
    print ("good here 0")
    conn = mysql.connector.connect(host=os.environ.get('DB_HOST'),
    user=os.environ.get('DB_USER'), password=os.environ.get('DB_PASS'), database=os.environ.get('DB_NAME'))
    print ("good here 1")
    cursor = conn.cursor()
    print ("good here 2")
    cursor.execute("select id from testSchedule;", ())
    print ("good here 3")
    rslt = cursor.fetchall()
    print ("good here 4")
    print(rslt)


###############################################################################
#   Main
###############################################################################
if __name__ == '__main__':
    testConn()
    # getRow()
