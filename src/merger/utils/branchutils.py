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
Helper methods for branching management.  While merging we need to take 
decisions such as if to merge BRANCHES or not, this decision making 
branching related logic is encapsulated here.
"""

from audit_helper import audit_write
from merge_messages import get_nextbranch_codefreeze_subject, \
    get_nextbranch_codefreeze_text, get_subject_excluded, get_text_excluded, \
    get_next_excluded_subject, get_next_excluded_text, get_auto_not_allowed_subject, \
    get_auto_not_allowed_text
from merger.conf import mergeconf, mergeconfhelper
from merger.conf.mergeconf import BRANCHES_TO_EXCLUDE, NOMERGE_KEY, \
    AUDIT_OP_MERGE, NA, AUDIT_EXPL_CODE_FREEZE, AUDIT_EXPL_EXCLUDED, \
    AUDIT_EXPL_AUTO_NOT_ALLOWED, KEY_REV_START, KEY_CURRENT_BRANCH, KEY_NEXT_BRANCH, \
    KEY_MESSAGE, KEY_FILES_TO_IGNORE, LOGGER, KEY_AUTHOR, KEY_AUTHORS_TO_IGNORE, \
    KEY_LOOK_RESULT, KEY_IS_MANUAL
from merger.svn.svnutils import get_branch_col
from merger.utils import mailutils, loggerutils

def is_excluded(branch_name):
    """
        We may want to explicitly exclude some BRANCHES from the list
        of BRANCHES to be merged, check if the branch name supplied
        is excluded if yes then do not perform merging into it.
        
        Args:
            branch_name: The branch to check if to be incorporated
                in branching or not.
        Retruns:
            True if branch should be excluded, in this case no merges
            will be performed into this branch, otherwise False.
    """
    return branch_name in BRANCHES_TO_EXCLUDE

def is_code_freeze(branch_name, branches_in_codefreeze):
    """
        Check if this branch is in code freeze, if it is then
        do not incorporate it in BRANCHES to be merged,
        also there is the possibility to send special mails
        for BRANCHES which are in code freeze while commits
        are performed on these BRANCHES.
        
        Args:
            branch_name: The branch to check if in code freeze or not.
        Retruns:
            True if branch is in code freeze, in this case no
            merges are performed into it, otherwise False.
    """
    return branch_name in branches_in_codefreeze

def handle_merge_conditions(merge_item):
    """We do not want always a merge to occur.  If committer specified in commit message
        that he does not want his commit to be auto merged then this method will return False
        All checks:
        1. Is no merge keyword in description? (of commit).
        2. Are files to ignore (in conjunction with author).
        3. Is next branch in code freeze?
        4. Is branch in exclusion for auto merger?
        5. Is automatic merging allowed?
    """
    to_merge = True
    if is_nomerge_key(merge_item[KEY_REV_START], merge_item[KEY_CURRENT_BRANCH], merge_item[KEY_NEXT_BRANCH], merge_item[KEY_MESSAGE]): 
        to_merge = False

    if are_commit_files_to_ignore(merge_item): 
        to_merge = False
    elif handle_code_freeze_next_branch(merge_item): 
        to_merge = False
    elif handle_excluded_cur_branch(merge_item): 
        to_merge = False
    elif handle_excluded_next_branch(merge_item): 
        to_merge = False
    elif not is_automatic_allowed(merge_item): 
        to_merge = False
    handle_code_freeze_cur_branch(merge_item)
    return to_merge

def is_nomerge_key(revstart, current_branch, next_branch, message):
    """Check if commit message has no merge keyword in it.
        In that case we would not be interested in doing auto merging.
        
        Args:
            revstart: Revision for original commit.
            current_branch: The branch on which a commit has been performed.
            next_branch: The branch we are supposed to perform auto merging into.
            message: The message the user has committed with.
        Retruns:
            True if no merge key was found otherwise false.
    """
    is_nomerge = False
    if message.find(NOMERGE_KEY) != -1:
        audit_write(AUDIT_OP_MERGE, NA, current_branch, next_branch, revstart, revstart, NA, NA, NOMERGE_KEY)
        mergeconf.LOGGER.debug(
                NOMERGE_KEY + ' keyword found in commit, not merging from ' + current_branch + ' to: ' + next_branch + ' revision: ' + revstart
        )
        is_nomerge = True
    return is_nomerge


def are_commit_files_to_ignore(merge_item):
    """Check if to ignore this commit for auto merging based on the files which were committed.
        
        Args:
            files_to_ignore: If any of the files committed is in this list in conjunction with authors, do not merge.
            with_authors_to_ignore: If the files in conjunction with these authors were committed then do not auto merge.
            revstart: Revision for original commit.
            current_branch_name: The branch on which a commit has been performed.
            next_branch_name: The branch we are supposed to perform auto merging into.
            lookresult: The result fro svn look on this commit.
            author: The one who performed this commit
        Retruns:
            True means to ignore this commit for merging.
    """
    status = False
    if merge_item[KEY_FILES_TO_IGNORE] is not None:
        for file_in_commit in merge_item[KEY_FILES_TO_IGNORE]:
            loggerutils.log(LOGGER,"are_commit_files_to_ignore: author: " + merge_item[KEY_AUTHOR])
            loggerutils.log(LOGGER,"are_commit_files_to_ignore: with_authors_to_ignore: " + str(merge_item[KEY_AUTHORS_TO_IGNORE]))
            loggerutils.log(LOGGER,"lookresult: " + merge_item[KEY_LOOK_RESULT]
            + " checking if file_in_commit " + file_in_commit +
            " is in filestoignore: " + str(merge_item[KEY_FILES_TO_IGNORE]) + " : " +
            str(merge_item[KEY_LOOK_RESULT].find(file_in_commit)) +
            " and if author: " + merge_item[KEY_AUTHOR] +
            " is in authors to ignore: " + str(merge_item[KEY_AUTHORS_TO_IGNORE]) +
            " : " + str(merge_item[KEY_AUTHOR] in merge_item[KEY_AUTHORS_TO_IGNORE]))
            if merge_item[KEY_LOOK_RESULT].find(file_in_commit) != -1 and merge_item[KEY_AUTHOR] in merge_item[KEY_AUTHORS_TO_IGNORE]:
                audit_write(AUDIT_OP_MERGE, NA, merge_item[KEY_CURRENT_BRANCH], merge_item[KEY_NEXT_BRANCH], 
                            merge_item[KEY_REV_START], merge_item[KEY_REV_START], NA, NA,
                            file_in_commit + ' ' + merge_item[KEY_AUTHOR])
                mergeconf.LOGGER.debug('its a ' + file_in_commit + ' commit and author is ' + merge_item[KEY_AUTHOR] + 
                        ' therefore not merging please verify no other commits with this ' + 
                        merge_item[KEY_CURRENT_BRANCH] + ' to: ' + merge_item[KEY_NEXT_BRANCH] + ' revision: ' + str(merge_item[KEY_REV_START]))
                status = True
                break
    return status

def handle_code_freeze_cur_branch(merge_item):
    """If branch is in code freeze send an email if commit was made to it, otherwise
        do not merge into it.
        
        Args:
            merge_item: Details of commit to be merged.
    """
    if is_code_freeze(merge_item[KEY_CURRENT_BRANCH], mergeconf.BRANCHES_IN_CODE_FREEZE):
        mergeconf.LOGGER.debug(merge_item[KEY_CURRENT_BRANCH] + " is in code freeze")
        audit_write(AUDIT_OP_MERGE, merge_item[KEY_AUTHOR], merge_item[KEY_CURRENT_BRANCH], merge_item[KEY_NEXT_BRANCH], 
                    merge_item[KEY_REV_START], merge_item[KEY_REV_START], NA, NA,
                    AUDIT_EXPL_CODE_FREEZE)
        mailutils.mail(mergeconfhelper.get_dl(merge_item[KEY_AUTHOR], mergeconf.ENUM_CODE_FREEZE),
                       'Commit made to branch ' + merge_item[KEY_CURRENT_BRANCH] + 
                       ' which is below code freeze branch',
                       'Commit made to branch ' + merge_item[KEY_CURRENT_BRANCH] + 
                       ' which is below code freeze branch\r\n' + 'By: ' + merge_item[KEY_AUTHOR] + '\r\n' + 
                       'Revision: ' + merge_item[KEY_REV_START] + '\r\n' + 'Message: ' + merge_item[KEY_MESSAGE] + '\r\n' + 
                       merge_item[KEY_LOOK_RESULT]
        )

def handle_code_freeze_next_branch(merge_item):
    """In case of code freeze do not merge, however send an 
    email notification that a commit was taking place into a code freeze branch.
        
        Args:
            merge_item: Details of commit to be merged.
    """
    in_freeze = False
    if is_code_freeze(merge_item[KEY_CURRENT_BRANCH], mergeconf.BRANCHES_IN_CODE_FREEZE):
        mergeconf.LOGGER.debug(merge_item[KEY_NEXT_BRANCH] + " is in code freeze")
        audit_write(AUDIT_OP_MERGE, merge_item[KEY_AUTHOR], merge_item[KEY_NEXT_BRANCH], 
                    merge_item[KEY_NEXT_BRANCH], merge_item[KEY_REV_START], merge_item[KEY_REV_START], NA, NA,
                    AUDIT_EXPL_CODE_FREEZE)
        mailutils.mail(mergeconfhelper.get_dl(merge_item[KEY_AUTHOR], mergeconf.ENUM_CODE_FREEZE),
                       get_nextbranch_codefreeze_subject(merge_item[KEY_NEXT_BRANCH]),
                       get_nextbranch_codefreeze_text(merge_item[KEY_REV_START], 
                                                      merge_item[KEY_CURRENT_BRANCH], merge_item[KEY_LOOK_RESULT], 
                                                      merge_item[KEY_NEXT_BRANCH], merge_item[KEY_MESSAGE],
                                                      merge_item[KEY_AUTHOR]))
        in_freeze = True
    return in_freeze


def handle_excluded_cur_branch(merge_item):
    f_excluded = False
    if is_excluded(merge_item[KEY_CURRENT_BRANCH]):
        mergeconf.LOGGER.debug(merge_item[KEY_CURRENT_BRANCH] + " is in exclusion")
        audit_write(AUDIT_OP_MERGE, merge_item[KEY_AUTHOR], merge_item[KEY_CURRENT_BRANCH], merge_item[KEY_NEXT_BRANCH], merge_item[KEY_REV_START], merge_item[KEY_REV_START], NA, NA,
                    AUDIT_EXPL_EXCLUDED)
        mailutils.mail(mergeconfhelper.get_dl(merge_item[KEY_AUTHOR], mergeconf.ENUM_EXCLUDED), get_subject_excluded(merge_item[KEY_CURRENT_BRANCH]),
                       get_text_excluded(merge_item[KEY_REV_START], merge_item[KEY_CURRENT_BRANCH], merge_item[KEY_LOOK_RESULT], merge_item[KEY_MESSAGE], merge_item[KEY_AUTHOR]))
        f_excluded = True
    return f_excluded


def handle_excluded_next_branch(merge_item):
    f_excluded = False
    if is_excluded(merge_item[KEY_CURRENT_BRANCH]):
        mergeconf.LOGGER.debug(merge_item[KEY_CURRENT_BRANCH] + " is in exclusion")
        audit_write(AUDIT_OP_MERGE, merge_item[KEY_AUTHOR], merge_item[KEY_CURRENT_BRANCH], merge_item[KEY_NEXT_BRANCH], merge_item[KEY_REV_START], merge_item[KEY_REV_START], NA, NA,
                    AUDIT_EXPL_EXCLUDED)
        mailutils.mail(mergeconfhelper.get_dl(merge_item[KEY_AUTHOR], mergeconf.ENUM_EXCLUDED), get_next_excluded_subject(merge_item[KEY_NEXT_BRANCH]),
                       get_next_excluded_text(merge_item[KEY_REV_START], merge_item[KEY_LOOK_RESULT], merge_item[KEY_NEXT_BRANCH], merge_item[KEY_MESSAGE], merge_item[KEY_AUTHOR]))
        f_excluded = True
    return f_excluded

def is_automatic_allowed(merge_item):
    is_allowed = True
    if not mergeconf.IS_AUTOMATIC and not merge_item[KEY_IS_MANUAL]:
        mergeconf.LOGGER.debug("Automatic merge is not allowed")
        audit_write(AUDIT_OP_MERGE, merge_item[KEY_AUTHOR], merge_item[KEY_CURRENT_BRANCH], merge_item[KEY_NEXT_BRANCH], merge_item[KEY_REV_START], merge_item[KEY_REV_START], NA, NA,
                    AUDIT_EXPL_AUTO_NOT_ALLOWED)
        mailutils.mail(mergeconfhelper.get_dl(merge_item[KEY_AUTHOR], mergeconf.ENUM_EXCLUDED), get_auto_not_allowed_subject(merge_item[KEY_NEXT_BRANCH]),
                       get_auto_not_allowed_text(merge_item[KEY_REV_START], merge_item[KEY_CURRENT_BRANCH], merge_item[KEY_LOOK_RESULT], merge_item[KEY_MESSAGE], merge_item[KEY_AUTHOR]))
        is_allowed = False
    return is_allowed

def get_branch_index(BRANCHES, branch_name):
    """
    Get the place of the branch name in the array of BRANCHES so will know into which next branch to merge - the next one in array.
    """
    i = 0
    for branch in BRANCHES:
        if branch_name == branch:
            return i
        else:
            i = i + 1

def get_branch_url(name):
    return mergeconf.BASE_REPOSITORY_PATH + '/' + name 
    
def get_next_branch(svnLookLine, BRANCHES_MAP):
    branches_col = get_branch_col(svnLookLine, BRANCHES_MAP)
    for index, branch in enumerate(branches_col):
        if (svnLookLine.find(branch) != -1):
            if len(branches_col) > (index + 1):
                return branches_col[index + 1]
    return None 