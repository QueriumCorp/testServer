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


def modTasks():
    dbConn.modMultiVals(
        'testPath',
        ['id'], [1],
        ['status', 'pid', 'timeCompleted', 'gitBranch', 'gitHash', 'trace_id', 'diff_id','msg'],
        ['pending', '-1', '-1', 'dev', 'de32d05ef5622520d84912ca04c18f031309a6a0', '-1', '-1','']
    )
    dbConn.modMultiVals(
        'testPath',
        ['id'], [2],
        ['status', 'pid', 'timeCompleted', 'gitBranch', 'gitHash', 'trace_id', 'diff_id','msg'],
        ['pending', '-1', '-1', 'dev', 'de32d05ef5622520d84912ca04c18f031309a6a0', '-1', '-1','']
    )
    dbConn.modMultiVals(
        'testPath',
        ['id'], [6],
        ['status', 'pid', 'timeCompleted', 'gitBranch', 'gitHash', 'trace_id', 'diff_id','msg'],
        ['pending', '-1', '-1', 'dev', '57bdb3bfd4a1dd54c036acb3d4239d3bf67ea2d3', '-1', '-1','']
    )
    dbConn.modMultiVals(
        'testPath',
        ['id'], [9],
        ['status', 'pid', 'timeCompleted', 'gitBranch', 'gitHash', 'trace_id', 'diff_id','msg','limitPathTime'],
        ['pending', '-1', '-1', 'dev', '57bdb3bfd4a1dd54c036acb3d4239d3bf67ea2d3', '-1', '-1','','10']
    )

def modByPriority():
    tbl = "testPath"
    status = "acquired"
    host = "testHost"
    pid = os.getpid()
    dbConn.modMultiVals(
        tbl,
        ["status"], ["pending"],
        ["status", "host", "pid"],
        [status, host, pid],
        fltr="ORDER BY priority DESC LIMIT 1"
    )

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
    # data = task.next(taskId=28)
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
    # taskId = 32
    # Update the branch and git hash of a task to be tested.
    # CommonCore repo has a runTask branch
    # dbConn.modMultiVals(
    #     'testPath',
    #     ['id'], [1],
    #     ['status', 'pid', 'gitBranch', 'gitHash','msg'],
    #     ['pending', '-1', 'dev', '57bdb3bfd4a1dd54c036acb3d4239d3bf67ea2d3','']
    # )

    # fail: de32d05ef5622520d84912ca04c18f031309a6a0
    dbConn.modMultiVals(
        'testPath',
        ['id'], [1],
        ['status', 'pid', 'timeCompleted', 'gitBranch', 'gitHash', 'trace_id', 'diff_id','msg','limitPathTime'],
        ['pending', '-1', '-1', 'dev', '57bdb3bfd4a1dd54c036acb3d4239d3bf67ea2d3', '-1', '-1','','5']
    )

    # Get the task for testing
    # aTask = task.next(taskId=taskId)
    aTask = task.next()

    if len(aTask) < 1:
        print("No task to test")
        return

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
