# Doesn't work :(

# from multiprocessing import Pool, Lock
import multiprocessing
import os
import time
from functools import partial


def target(lock, item):
    lock.aquire()
    print("Worker process {pid}: {arg}".format(pid=os.getpid(), arg=item))
    time.sleep(5)
    lock.release()
    return item*item

###############################################################################
#   Main
###############################################################################
if __name__ == '__main__':
    print("Master process {pid}".format(pid=os.getpid()))
    with multiprocessing.Pool(processes=4) \
        as pool:
        mngr = multiprocessing.Manager()
        l = mngr.Lock()
        func = partial (target, l)
        for r in pool.imap_unordered(func, range(10)):
            print("result: {}".format(r))
        # print (pool.get())
