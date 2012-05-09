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

from merger.conf import mergeconf
from merger.conf.mergeconf import LOGGER
from merger.svn import svnutils
from merger.svn.svnutils import LOOK_CHANGED_TMPL
import csv
import sys
import urllib


def produce_merge():
    """
       This method is called after a user commits to svn repository.
       We get here the repository and revision that was committed.
       We write here to the audit file PRODUCED which means a commit was made.
       Call the server to provide it with information about commit which
       was performed, and let the server continue handling this commit.
       
       Args:
        argv[1]: From post commit hook the repository on which commit was made. 
        argv[2]: From post commit hook the revision number assigned to commit performed.
       
       Returns:
         Result: updates csv audit with commit performed and calls server to treat that merge.
    """
    LOGGER.debug('auto merger %s ' % (mergeconf.VERSION))
    for arg in sys.argv:
        LOGGER.debug ('arg: ' + arg)
    LOGGER.debug('repository: ' + sys.argv[1])
    LOGGER.debug('revision number: ' + sys.argv[2])
    repository = sys.argv[1]
    revision = sys.argv[2]

    lookcmd = LOOK_CHANGED_TMPL % (revision,repository)
    LOGGER.debug('lookcmd: ' + lookcmd)
    result = mergeconf.M_SHU.runshellcmd(lookcmd)
    LOGGER.debug('result: ' + result)
    current_branch_name = svnutils.get_branch_by_look(result, mergeconf.BRANCHES_MAP)
    
    
    # If the branch for which a commit just happended is not relevant to our branches.
    if not current_branch_name:
        LOGGER.debug('Branch changed is not in list of branches to auto merge')
        write_merge_produced(revision, current_branch_name, repository, mergeconf.CSV_STATUS_MERGE_IGNORED)
        return
    
    params = urllib.urlencode({mergeconf.KEY_REV_START: revision, mergeconf.KEY_REPO: repository})
    try:
        url = mergeconf.MERGE_SERVER_URL % params
        LOGGER.debug(url)
        f = urllib.urlopen(mergeconf.MERGE_SERVER_URL % params)
        write_merge_produced(revision, current_branch_name, repository, mergeconf.CSV_STATUS_MERGE_PRODUCED)
        LOGGER.debug(f.read())
    except:
        write_merge_produced(revision, current_branch_name, repository, mergeconf.CSV_STATUS_MERGE_FAILED)
        mergeconf.LOGGER.exception("exception occured")

def write_merge_produced(rev, branch, REPO, status):
    """
       Update audit file that a commit was performed.
       
       Args:
           rev: Revision that has been committed.
           branch: The branch on which this commit has been performed.
           REPO: The repository on which this commit has been performed.
           status: Whether managed to update the server about this commit or not.
       
       Returns:
         Result: Updates audit file with commit details (PRODUCTION of a merge unit).
    """
    LOGGER.debug('Writing merge produce:\n %s,%s,%s,%s,%s' % (mergeconf.MERGE_PRODUCER_CSV, REPO, branch, rev, status))
    writer = csv.writer(open(mergeconf.MERGE_PRODUCER_CSV, 'ab', buffering=0))
    writer.writerows([
        (REPO,branch,rev,status)
    ])
        

if __name__=="__main__":
    LOGGER.debug("postcommit called...")
    produce_merge()

