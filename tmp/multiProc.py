# Example multiprocessing code: Works!

# from multiprocessing import Pool, Lock
import multiprocessing
import os
import time
import random

def worker(lock, id):
    lock.acquire()
    sleepTime = random.randint(1, 10)
    print("Worker {id} ({pid}) acquired lock, sleeping for {num}" \
        .format(pid=os.getpid(), id=id, num=sleepTime))
    time.sleep(sleepTime)
    # randNum = random.randint(50, 100)
    # for i in range(randNum):
    #     time.sleep(0.5)
    #     rslt = i * i
    print("Worker {id} ({pid}) is releasing the lock".format(
        pid=os.getpid(), id=id))
    lock.release()

def whoIsAlive():
    print("- - - - - ")
    for i in range(len(PROCESSES)):
        if PROCESSES[i].is_alive():
            timedelta = time.process_time()-STARTTIME[i]
            print("Worker {id} ({pid}) is ALIVE for {timediff}".format(
                id=i, pid=PROCESSES[i].pid, timediff=timedelta))
        else:
            print("Worker {id} ({pid}) is DEAD, exitcode {code}".format(
                id=i, pid=PROCESSES[i].pid, code=PROCESSES[i].exitcode))

###############################################################################
#   Main
###############################################################################
if __name__ == '__main__':
    print("Master process: {pid}".format(pid=os.getpid()))
    workerLimit = 10
    PROCESSES = []
    STARTTIME = []
    LOCK = multiprocessing.Lock()
    stopSpawningQ = False
    workerCount = 1
    terminateQ = False
    while not terminateQ:
        # Start a worker every 1 seconds
        time.sleep(2)
        # Report on workers' status
        whoIsAlive()

        try:
            if stopSpawningQ:
                continue
            # Create a worker process object
            process = multiprocessing.Process(
                target=worker, args=(LOCK, workerCount))
            PROCESSES.append(process)

            # Spawn a worker process
            process.start()
            # Keep track of the starting time of the process
            STARTTIME.append(time.process_time())

        except KeyboardInterrupt:
            ### Add cleanup code if needed
            terminateQ = True

        if workerCount > workerLimit:
            stopSpawningQ = True
        workerCount += 1

    # wait for all the process to finish
    for p in PROCESSES:
        p.join()

    print("Master process: Completed".format(pid=os.getpid()))