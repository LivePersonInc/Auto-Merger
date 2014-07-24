__author__ = 'tomerb'

from merger.conf.mergeconf import ARG_CLIENT

def is_client(argv): return len(argv) > 1 and argv[1] == ARG_CLIENT
