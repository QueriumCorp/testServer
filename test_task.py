###############################################################################
# Testing module
# python3 test_task.py
###############################################################################
import sys
import task
import os
from dotenv import load_dotenv
load_dotenv()
import logging

logging.basicConfig(level=logging.DEBUG)


def getMmaVersion():
    rslt = task.getMmaVersion()
    print(rslt)

def next():
    rslt = task.next()
    print (rslt)

###############################################################################
#   Main
###############################################################################
if __name__ == '__main__':
    next()
    # getMmaVersion()