###############################################################################
# Testing module
# python3 test_mysql.py
###############################################################################
import logging
import main

logging.basicConfig(level=logging.DEBUG)


###############################################################################
#   Main
###############################################################################
if __name__ == '__main__':
    result = main.gotLicenseQ()
    print(result)
