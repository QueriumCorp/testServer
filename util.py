###############################################################################
# util.py
###############################################################################
import sys
import json
import os
import logging

###############################################################################
# Support functions
###############################################################################

#######################################
# Test a file exists and has data
#######################################
def fileGotDataQ(path):
    try:
        fileSize = os.path.getsize(path)
        if fileSize <= 0:
            logging.error("File has no data {}".format(path))
            return False

    except OSError:
        logging.error("File doesn't exist {}".format(path))
        return False

    return True


#######################################
# Convert a dict to a json string
#######################################
def toStr(data):
    if sys.platform == 'linux':
        return json.dumps(json.dumps(data, separators=(',', ':')))

    return json.dumps(data, separators=(',', ':'))