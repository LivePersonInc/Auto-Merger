import sys
from merger.conf.mergeconf import LOGGER
from merger.logic.postcommit import produce_merge
from merger.logic.mergeserver import start_webpy
from merger.utils.argutils import is_client


if __name__ == "__main__":
    for arg in sys.argv:
        LOGGER.debug('main arg: ' + arg)
    if is_client(sys.argv):
        LOGGER.debug('auto merger client started...')
        produce_merge(sys.argv[2], sys.argv[3])
    else: # its a server.
        start_webpy()
