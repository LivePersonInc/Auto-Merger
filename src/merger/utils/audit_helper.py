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

"""
Every time a commit is made to a branch we record that in an audit file.
    Then when merge server processes this merge it writes another entry to the
"""

from merger.conf import mergeconf
from merger.conf.mergeconf import NA, CSV_FILE_OPEN_TYPE
import csv



TYPE        = 'type'
WHO         = 'who'
FROM_BRANCH = 'frombranch'
TO_BRANCH   = 'tobranch'
RFROM       = 'rfrom'
REND        = 'rend'
RCOMMIT     = 'rcommit'
ISSUEID     = 'issueid'
DETAILS     = 'details'

def audit_write(operation, author=NA, cur_branch=NA, next_branch=NA, startrev=NA, 
                endrev=NA, issueid=NA, commitrev=NA, status=NA):
    """Every time a commit is made to a branch we record that in an audit file.
        Then when merge server processes this merge it writes another entry to the
        audit file of whether that commit has been processed (merged,failed-merge,ignored)
        in this way we can scan the audit file and know exactly the status of branches and merges.
        This is a helper method to write into audit file.

    Args:
      operation: The operation which we are auditing (example: AUDIT_OP_MERGE)
      author: The author which performed that commit.
      cur_branch: The branch name that has the commit.
      next_branch: The next branch which the commit is being merged into.
      startrev: For the merge we wish to perform which is the starting revision to perform the merge from.
      endrev: The end revision for the merge, which means we will do a merge up to this revision, note for
          a single commit startrev will be commit-rev - 1 and end rev will be the commit revision.
      issueid: If you have a convention where for each commit you have a relevant issue id this is the issue id related to the commit.
      commitrev: The commit revision which might trigger the merge or which was detected.
      status: Whether merge was successful / ignored / failed. 

    Returns:
      Nothing, silently appends to the audit file.
    """        
    mergeconf.LOGGER.debug('Writing to csv:\n %s,%s,%s,%s,%s,%s,%s,%s,%s' % 
                           (operation, author, cur_branch, next_branch, startrev, 
                            endrev, issueid, commitrev, status))
    writer = csv.writer(open(mergeconf.MERGE_PRODUCER_CSV, 
                             CSV_FILE_OPEN_TYPE, buffering=0))
    writer.writerows([
        (operation, author, cur_branch, next_branch, startrev, 
         endrev, issueid, commitrev, status)
    ])

