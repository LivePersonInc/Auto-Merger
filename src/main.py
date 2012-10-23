from Queue import Queue
import sys
from merger.logic.mergeserver import ConsumeFromQueue
from merger.conf.mergeconf import LOGGER
from merger.logic.postcommit import produce_merge
from merger.logic.mergeserver import start_webpy
import web

if __name__ == "__main__":
    for arg in sys.argv:
        LOGGER.debug ('arg: ' + arg)
    if len(sys.argv) > 1 and sys.argv[1] == 'client':
        LOGGER.debug('auto merger client started...')
        produce_merge(sys.argv[2], sys.argv[3])
    else: # its a server.
        start_webpy()

