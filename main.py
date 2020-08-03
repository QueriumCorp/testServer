###############################################################################
# main.py
# The main module

# Requirements
# Python >= 3.4
# Git 1.7.0 or newer

# Need the following modules
# python3 -m pip install python-dotenv
# python3 -m pip install PyMySQL
# python3 -m pip install psutil
# python3 -m pip install gitpython

# To run
# python3 main.py
###############################################################################
from dotenv import load_dotenv
load_dotenv()
import os
import time
import test
import sys
import json
import logging

logging.basicConfig(level=logging.DEBUG)

###############################################################################
# Support functions
###############################################################################

#######################################
# Initialize a server
#######################################
def init():
    ## Create a directory for the CommonCore repos
    if not os.path.isdir(os.environ.get('dirTest')):
        print("Created a testing directory:", os.environ.get('dirTest'))
        os.mkdir(os.environ.get('dirTest'))


###############################################################################
#   Main
###############################################################################
if __name__ == '__main__':

    ### testing code
    test.helloWorld()
    # sys.exit(0)

    ### init a server
    init()