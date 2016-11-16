# Copyright (c) 2012 Liveperson. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#   * Neither the name of Liveperson. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import ConfigParser
import logging
import os

"""
Nice helper methods to load configuration file, to load defaults in conf...
"""



def get_config(config, section, option, ctype=str, default=None):
    confdict = config.__dict__.get('_sections')
    if confdict.get(section) is None:
        ret = default
    else:
        if confdict.get(section) is not None:
            ret = confdict.get(section).get(option, default)
        else:
            ret = default
    if ret is not None:
        ret = ctype(ret)
    logging.debug('option: ' + option + ' value: ' + str(ret))
    return ret

def load_conf(primary_path, secondary_path):
    """
    Locate auto merger configuration file and load it.
    Performed during initialization of auto merger server.
    
    Args:
      primary_path: Configuration file by convention is either in relative location.
      secondary_path: If not found will search in absolute path such as /etc/merger.conf
    """
    logging.basicConfig(format='%(asctime)s %(levelname)s' + 
        ' %(module)s %(lineno)d %(message)s', level=logging.DEBUG)
    configreader = ConfigParser.ConfigParser()
    merge_conf_file = primary_path
    logging.info('trying conf file: ' + merge_conf_file)
    results = configreader.read(merge_conf_file)
    if results == []:
        merge_conf_file = secondary_path
        logging.info('trying secondary conf file: ' + merge_conf_file)
        results = configreader.read(merge_conf_file)
        if results == []:
            logging.info("could not load configreader file from " + merge_conf_file)
            exit(1)
    return configreader

def get_branches_map(branchitems):
    """
    Get list of branches from configuration to be auto merged, only these branches
    are going to be taken into account when auto merging.
    
    Args:
      branchitems: The list of branches to be analyzed.
    """
    branchesmap = {}
    logging.debug('get_branches_map: str(branchitems): ' + str(branchitems))
    if len(branchitems) > 0:
        for branches in sorted(branchitems):
            if (branches[0].startswith('branches-')):
                branchesmap[branches[0]] = branches[1].split(',')
    logging.info('branchesmap: ' + str(branchesmap))
    return branchesmap


