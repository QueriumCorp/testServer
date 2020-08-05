###############################################################################
# test.py
# Testing module
###############################################################################
from dotenv import load_dotenv
load_dotenv()
import os
import task

def helloWorld():
    print("Hello World!")

def taskNext():
    print("taskNext")
    print(task.next())
    print(task.next(statusCurr="running"))