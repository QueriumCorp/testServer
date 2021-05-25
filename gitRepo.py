###############################################################################
# Manage repository
###############################################################################
from datetime import datetime
import logging
import os
import math
import time
import git
import sys
from dotenv import load_dotenv
load_dotenv()

###############################################################################
# Support functions
###############################################################################
def mkDir(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)
    return dir
#######################################
# Make directories for the root, the repository, and the image
#######################################
def mkAllDir(task):
    dirRoot = os.path.join(mkDir(os.environ.get("dirTest")), task['gitHash'])
    dirRepo = os.path.join(mkDir(dirRoot), os.environ.get("repoName"))
    dirImg = mkDir(os.path.join(dirRoot, "image"))

    return {
        "dirRoot": dirRoot,
        "dirRepo": dirRepo,
        "dirImg": dirImg
    }

#######################################
# Checkout a github reference
#######################################
def checkoutRef(repo, aRef):
    refBranch = str(math.ceil(time.time()))
    ## Create a branch for a new reference
    newBranch = repo.create_head(refBranch, aRef)
    logging.info("{pid}: Created a branch: {refBranch}".format(
        pid=os.getpid(), refBranch=refBranch))
    ## Checking out the branch that points to the given reference
    repo.heads[refBranch].checkout()
    logging.info("{pid}: Checkout the branch for the ref - {aRef}".format(
        pid=os.getpid(), aRef=aRef
    ))
    assert repo.active_branch.commit.hexsha == aRef

#######################################
# Clone the CommonCore repo from GitHub
#######################################
def cloneRepo(dir, task):
    repo = git.Repo.clone_from(
        os.environ.get("repoUrl"),
        dir,
        branch=task['gitBranch']
    )
    ## Validate the repo
    assert repo.active_branch.name == task['gitBranch']

    ## Make sure the repo and the task is at the same codebase (git Hash)
    logging.debug("repo hash: {}".format(repo.active_branch.commit.hexsha))
    logging.debug("task hash: {}".format(task['gitHash']))
    if task['gitHash']!=repo.active_branch.commit.hexsha:
        checkoutRef(repo, task['gitHash'])

###############################################################################
# Main
###############################################################################
def mkEnv(task):
    ## Create a root directory for the repo and image
    dirs = mkAllDir(task)

    pid = os.getpid()
    try:
        ## If the repo doesn't exist, clone it
        if not os.path.isdir(
            os.path.join(dirs["dirRepo"], ".git")):
            logging.debug("Cloning a repo .....")
            cloneRepo(dirs["dirRepo"], task)
        ## Make sure the repo reference is the same as task['gitHash']
        aRepo = git.Repo(dirs["dirRepo"])
        if aRepo.active_branch.commit.hexsha!=task['gitHash']:
            checkoutRef(aRepo, task['gitHash'])
    except git.GitCommandError:
        logging.error("Invalid branch: {branch}".format(
            branch=task['gitBranch']
        ))
        return {
            "status": False,
            "result": "Invalid gitBranch"
        }
    except git.BadName:
        logging.error("Invalid ref: {hash}".format(
            hash=task['gitHash']
        ))
        return {
            "status": False,
            "result": "Invalid gitHash"
        }
    except:
        logging.error("Some unexpected error")
        return {
            "status": False,
            "result": "Unexpected error: gitRepo-mkEnv"
        }
    else:
        return {
            "status": True,
            "result": dirs
        }