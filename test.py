###############################################################################
# test.py
# Testing module
###############################################################################
from dotenv import load_dotenv
load_dotenv()
import os
import task
import gitRepo
import dbConn

def helloWorld():
    print("Hello World!")
    gitRepo.tmpTest()

def taskNext():
    print("taskNext")
    print(task.next())
    # print(task.next(statusCurr="running"))

def repoDir():
    aTask = task.next()
    result = repo.mkAllDir(aTask)
    print(result)

def repo():
    aTask = task.next()
    print('id:', aTask['id'])
    rslt = gitRepo.mkEnv(aTask)
    if rslt['status']==False:
        dbConn.modMultiVals(
            'testPath',
            ['id'], [aTask['id']],
            ['status', 'msg'], ['failed', rslt['result']]
        )
    print (rslt)