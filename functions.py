import time
import os

# Function used for logging messages to stdout and a disk file
def log(content, type):
    logfile = 'dum.log'
    print(str(time.strftime("%d/%m/%Y") + " " + time.strftime("%I:%M:%S") + " [" + type + "] " + content))
    if os.path.exists(logfile):
        log = open(logfile, 'a')
    else:
        log = open(logfile, 'w')
    log.write(str(time.strftime("%d/%m/%Y") + " " + time.strftime("%I:%M:%S") + " [" + type + "] " + content) + '\n')
    log.close()
