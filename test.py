###############################################################################
# test.py
# Testing module
###############################################################################
import sys
import image
import dbConn
import gitRepo
import task
import os
from dotenv import load_dotenv
load_dotenv()
import socket


def modMultiVals():
    tbl = "testPath"
    id = 49
    status = "testing"
    host = socket.gethostbyname(socket.gethostname())
    pid = os.getpid()
    dbConn.modMultiVals(
        tbl,
        ["id"], [id],
        ["status", "host", "pid"],
        [status, host, pid]
    )


def helloWorld():
    print("Hello World!")
    # gitRepo.tmpTest()


def taskNext():
    print("taskNext")
    data = task.next()
    print("status:", data["status"])
    print("host:", data["host"])
    print("pid:", data["pid"])
    # print(task.next(statusCurr="running"))


def repoDir():
    aTask = task.next()
    result = gitRepo.mkAllDir(aTask)
    print(result)


def repo():
    aTask = task.next()
    print('id:', aTask['id'])
    rslt = gitRepo.mkEnv(aTask)
    if rslt['status'] == False:
        dbConn.modMultiVals(
            'testPath',
            ['id'], [aTask['id']],
            ['status', 'msg'], ['failed', rslt['result']]
        )
    print(rslt)


def allDir():
    aTask = task.next()
    tmp = gitRepo.mkAllDir(aTask)
    print(tmp)


def mkImg():
    aTask = task.next()
    # dirs = gitRepo.mkAllDir(aTask)
    rsltEnv = gitRepo.mkEnv(aTask)
    if rsltEnv['status'] == True:
        rsltImg = image.make(aTask, rsltEnv['result'], rmImgQ=False)
        print(rsltImg)
        if rsltImg['status'] == False:
            dbConn.modMultiVals(
                'testPath',
                ['id'], [aTask['id']],
                ['status', 'msg'], ['failed', rsltImg['result']]
            )


def runTask():
    dbConn.modMultiVals(
        'testPath',
        ['id'], [49],
        ['status'], ['pending']
    )
    aTask = task.next()
    rsltEnv = gitRepo.mkEnv(aTask)
    print("rsltEnv:", rsltEnv)
    if rsltEnv['status'] == False:
        print("rsltEnv failed")
        return False
    rsltImg = image.make(aTask, rsltEnv['result'], rmImgQ=False)
    print("rsltImg:", rsltImg)
    aTask["dirCommonCore"] = rsltEnv['result']['dirRepo']
    aTask["loadFromImgOn"] = True if os.environ.get(
        "loadFromImgOn").lower() == "true" else False
    aTask["img"] = rsltImg['result']
    if rsltImg['status'] == False:
        print("rsltImg failed")
        return False
    # print("aTask:", aTask)
    # sys.exit(0)
    task.run(aTask)
