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

from merger.conf import mergeconf, mergeconfhelper
from merger.conf.mergeconf import TMPDIR, M_SHU, NA, ORIG_AUTHOR, ORIG_MESSAGE, \
    AUDIT_OP_MERGE, AUDIT_RES_FAILED_CONFLICT, SPREADSHEET_MERGE_FAILED, \
    SPREADSHEET_AUTHOR_PREFIX, SPREADSHEET_CONFLICT_MSG, CSV_STATUS_MERGE_SUCCESS, \
    SPREADSHEET_MERGE, AUDIT_RES_BRANCH_NOT_INF_CONF, AUDIT_RES_NO_NEXT_BRANCH, \
    AUDIT_EXPL_EXCEPTION, KEY_REPO, KEY_SOURCE_BRANCH_NAME, KEY_REV_START, \
    KEY_CURRENT_BRANCH, KEY_AUTHOR, KEY_NEXT_BRANCH, KEY_LOOK_RESULT, \
    KEY_CURRENT_BRANCH_URL, KEY_NEXT_BRANCH_URL, KEY_MESSAGE, KEY_FILES_TO_IGNORE, \
    KEY_AUTHORS_TO_IGNORE, LOGGER
from merger.svn import svnutils
from merger.svn.svnutils import MESSAGE_ABORT_COMMIT, MESSAGE_SUCCESSFUL_COMMIT, \
    get_commit_rev_by_resp, get_branch_by_look, SVNUTILS
from merger.utils import mailutils, branchutils
from merger.utils.audit_helper import audit_write
from merger.utils.merge_messages import get_failed_mergecommit_subject, \
    get_failed_mergecommit_text, get_merge_success_subject, get_merge_success_text
from merger.utils.spreadsheet import add_row
import os.path
import re

"""
Receives a merge work unit, processes it.
"""


def checkout_target_branch(branch_name, branch_url, svnutilsobj):
    """Given a branch url make sure it is synced with REPO on local disk (either checkout if
        does not exist yet on disk or update if already exist.
        
        Args:
            branch_url: The branch to sync (svn url).
            branch_name: The branch name to sync (will be used as its location on disk - folder name).
        Returns:
            Nothing, The branch will be synced on disk.
    """
    if os.path.isdir('%s/%s' % (TMPDIR, svnutils.get_branch_dir(branch_name))): # branch exists update it.
        svnutilsobj.update_local_workbranch(svnutils.get_branch_dir(branch_name))
    else:
        svnutilsobj.checkout(branch_url, svnutils.get_branch_dir(branch_name))
    return branch_name

def get_issue_id(issue_id_pattern, message):
    """When you have a branch which is merged this method will commit it.
        
        Args:
            revstart: The starting revision which was applied as a merge, used mainly for auditing. 
            revend: The ending revision which was applied as a merge, used mainly for auditing..
            current_branch_name: The branch which the merge was performed from, used mainly for auditing.
            next_branch_name: The branch which the merge was performed to, used mainly for auditing.
            message: Commit message.
            author: When committing code will add the author name to description so we can keep trac of who was original committer.
            merge_to_branch: The branch the merge was performed for, this is the actual directory name we do the commit to.
        Returns:
            Nothing, The local branch is being committed.
    """
    if message is not None:
        res = re.compile(r"%s" % (issue_id_pattern), re.MULTILINE).search(message)
        if res is not None and len(res.groups()) > 0:
            return res.groups()[0]
    return mergeconf.ISSUE_ID_DEFAULT_VALUE

def log_prefix_desc(merge_item):
    """
        When analyzing a commit log this prefix, useful when trying to debug
        mergeworker decisions.
        
        Args:
            REPO: The repository the commit was made upon. 
            rev: Revision that was comitted which mergeworker handles.
        Returns:
            The work unit processing log prefix a few lines to be printed
            to log before processing any work unit.
    """
    mergeconf.LOGGER.debug('-- Server Adding Merge Worker Unit --')
    mergeconf.LOGGER.debug('auto merger %s ' % (mergeconf.VERSION))
    mergeconf.LOGGER.debug('repository: ' + merge_item[KEY_REPO])
    mergeconf.LOGGER.debug('revision number: ' + merge_item[KEY_REV_START])


def get_author(rev, repo, message):
    """
        Extract the author from commit log or look command. 
        We do look only at some cases only on rev and not
        on all revisions which committed under the assumption its going to have
        (ofcourse) the same author.
        
        Args:
            rev: Revision that was comitted which mergeworker handles. 
            repo: rev, revision of commit to check the commit log message.
            message: Commit log message we might extract from there the original
                author as the auto merger merges with his own user and not
                the original committer.
            
        Returns:
            The name of the committer we we perform the merge for.
    """
    if (message and message.find(ORIG_AUTHOR) != -1):
        message = message.replace('\r', '')
        orig_authors = re.compile(r"^orig_author: (.*?)$", re.MULTILINE).search(message).groups()
        author = orig_authors[0] if orig_authors else None
        mergeconf.LOGGER.debug ('author is: %s ' % author)
    else:
        svnlook_getauthor_cmd = svnutils.LOOK_AUTH_TMPL % (rev, repo)
        mergeconf.LOGGER.debug ('get author version control command: %s ' % svnlook_getauthor_cmd)
        author = M_SHU.runshellcmd(svnlook_getauthor_cmd).rstrip()
    return author





def deduce_current_branch(merge_item):
    """
        Extract branch directory to do local temporal work form branch name.
        For example if we have multiple projects which have the same ending
        branch name projecta/1.0, projectb/1.0 then store the folders as
        projecta_1.0 and projectb_1.0 for temporal work folder for merging.
        
        Args:
            branch_name: The branch name to compute the branch working folder.
        Returns:
            Working branch dir on disk.
    """
    lookcmd = svnutils.LOOK_CHANGED_TMPL % (merge_item[KEY_REV_START], merge_item[KEY_REPO])
    lookresult = M_SHU.runshellcmd(lookcmd)
    mergeconf.LOGGER.debug('result: ' + lookresult)
    if merge_item.get(KEY_SOURCE_BRANCH_NAME, None) is None:
        current_branch = get_branch_by_look(lookresult, mergeconf.BRANCHES_MAP)
    else:
        current_branch = merge_item.get(mergeconf.KEY_SOURCE_BRANCH_NAME, None)
    return current_branch, lookresult


def is_relevant_branch(commitrev, branch_name):
    """
        Check if the branch is in our merger.conf at all.  If not then we 
        are not going to deal with it.
        Args:
            commitrev: The revision which commit was done,
                used for auditing.
            branch_name: The branch to check if relevant for auto merges or not.
        Returns:
            True if branch is relevant for merges, False if not.
    """
    is_relevant = True
    if not branch_name:
        audit_write(AUDIT_OP_MERGE, NA, branch_name, NA, commitrev, commitrev, NA, NA,
                    AUDIT_RES_BRANCH_NOT_INF_CONF)
        mergeconf.LOGGER.debug('Branch changed is not in list of branches to auto merge')
        is_relevant = False
    return is_relevant


def is_next_branch_relevant(commitrev, current_branch, next_branch):
    """
        Check if the branch to merge into is relevant, and we should merge into it.
        Args:
            commitrev: The revision which commit was done,
                used for auditing.
            current_branch: The current branch name (commit has been performed to this branch).
            next_branch: The branch we potentially will merge into.
        Returns:
            True if next branch is relevant for merges, False if not.
    """
    is_relevant = True
    if not next_branch:
        audit_write(AUDIT_OP_MERGE, NA, current_branch, NA, commitrev, commitrev, NA, NA, AUDIT_RES_NO_NEXT_BRANCH)
        mergeconf.LOGGER.debug('No next branch to: ' + current_branch + ' to merge into')
        is_relevant = False
    return is_relevant

def handle_merge_failed(revstart, revend, current_branch_name, next_branch_name, message, author, rev_as_str, commit_merge_result):
    mergeconf.LOGGER.debug('merge failed')
    try:
        mailutils.mail(mergeconf.get_dl(author, mergeconf.ENUM_MERGE), get_failed_mergecommit_subject(current_branch_name, next_branch_name, author, rev_as_str), get_failed_mergecommit_text(current_branch_name, next_branch_name, message, author, rev_as_str, commit_merge_result), mergeconf.MAIL_ENABLED)
    except:
        LOGGER.error("Please check mail configuration, failed sending email...")
    audit_write(AUDIT_OP_MERGE, author, current_branch_name, next_branch_name, revstart, revend, NA, NA, AUDIT_RES_FAILED_CONFLICT)
    add_row({mergeconf.TYPE_COL:SPREADSHEET_MERGE_FAILED, 'who':SPREADSHEET_AUTHOR_PREFIX + author, 'frombranch':current_branch_name, 'tobranch':next_branch_name, 'rfrom':revstart, 'rend':revend, 'rcommit':NA, 'bugid':mergeconf.ISSUE_ID_DEFAULT_VALUE, 'details':SPREADSHEET_CONFLICT_MSG}, mergeconf.SPREADSHEET_USERNAME, mergeconf.SPREADSHEET_PASSWORD, mergeconf.SPREADSHEET_KEY, mergeconf.SPREADSHEET_WORKSHEET_ID, mergeconf.APP_KEY)


def handle_success_merge(revstart, revend, current_branch_name, next_branch_name, message, author, rev_as_str, commit_message, commit_merge_result):
    audit_write(AUDIT_OP_MERGE, author, current_branch_name, next_branch_name, revstart, revend, NA, NA, CSV_STATUS_MERGE_SUCCESS)
    rcommit = get_commit_rev_by_resp(commit_merge_result)
    try:
        mailutils.mail(mergeconf.get_dl(author, mergeconf.ENUM_MERGE), get_merge_success_subject(current_branch_name, next_branch_name, author, rev_as_str), get_merge_success_text(current_branch_name, next_branch_name, message, author, rev_as_str, commit_merge_result), mergeconf.MAIL_ENABLED)
    except:
        LOGGER.error("Please check mail configuration, failed sending email...")
    add_row({mergeconf.TYPE_COL:SPREADSHEET_MERGE, 'who':SPREADSHEET_AUTHOR_PREFIX + author, 'frombranch':current_branch_name, 'tobranch':next_branch_name, 'rfrom':revstart, 'rend':revend, 'rcommit':rcommit, 'bugid':mergeconf.ISSUE_ID_DEFAULT_VALUE, 'details':commit_message}, mergeconf.SPREADSHEET_USERNAME, mergeconf.SPREADSHEET_PASSWORD, mergeconf.SPREADSHEET_KEY, mergeconf.SPREADSHEET_WORKSHEET_ID, mergeconf.APP_KEY)

class MergeWorker():
    """
        Decides if to do merge or not.
        If yes, main component that perform the actual merges with relevant helpers.
    """
    
    def __init__(self, svn_utils=SVNUTILS):
        """
            Construct a new MergeWorker.
            As mergeworker is going to use svn utils provide it with it.
            
            Args:
                svn_utils: SVN related utilities to use - helper .
        """
        self.svn_utils = svn_utils
    






    def commit_merged_code(self, revstart, revend, current_branch_name, next_branch_name, message, author,
                           merge_to_branch, rev_as_str):
        """When you have a branch which is merged this method will commit it.
            
            Args:
                revstart: The starting revision which was applied as a merge, used mainly for auditing. 
                revend: The ending revision which was applied as a merge, used mainly for auditing..
                current_branch_name: The branch which the merge was performed from, used mainly for auditing.
                next_branch_name: The branch which the merge was performed to, used mainly for auditing.
                message: Commit message.
                author: When committing code will add the author name to description so we can keep trac of who was original committer.
                merge_to_branch: The branch the merge was performed for, this is the actual directory name we do the commit to.
            Returns:
                Nothing, The local branch is being committed.
        """
        if revend is None:
            revend = revstart
        
        mergeconf.LOGGER.debug('Committing merged code...')
        commit_message = mergeconf.ISSUE_ID_NAME + ': ' + mergeconf.ISSUE_ID_DEFAULT_VALUE + '\n' + mergeconf.CODEREVIEW_NAME + \
            ': ' + NA + '\n' + ORIG_AUTHOR + ': ' + author + '\n' + ORIG_MESSAGE + ': ' + message
        commit_merge_result = self.svn_utils.commit(TMPDIR + '/' + svnutils.get_branch_dir(merge_to_branch), commit_message, revstart)
        mergeconf.LOGGER.debug('is aborting found? ' + str(commit_merge_result.find(MESSAGE_ABORT_COMMIT)))
        
        if (commit_merge_result.find(MESSAGE_SUCCESSFUL_COMMIT) == -1):
            handle_merge_failed(revstart, revend, current_branch_name, next_branch_name, message, author, rev_as_str, commit_merge_result)
        else:
            handle_success_merge(revstart, revend, current_branch_name, next_branch_name, message, author, rev_as_str, commit_message, commit_merge_result)
            return True








    def do_merge(self, merge_item):
        """
            This is the main handler for merges.
            This method recieves some details from the commit
            it checks if we need to do a merge, to which branch
            deduces the merge message, sends emails, and
            actually performs the merge.
            Args:
                REPO: Repository on which the original commit was perforemd.
                revstart: The revision that was originally committed from it the 
                    merge was performed.
                is_manual: Manual - A merge through a web interface,
                    Automatic means an auto merge.
                revend: In case of multiple revisions to perform commit to
                    (relevant in manual merge only).
                source_branch: The originating branch for this potential merge.
                svn_username: The username to use in order to perform the commit after merge.
                svn_password: The password to use while committing the merge.
            Returns:
                Result: performing the merge.
        """

        try:
            log_prefix_desc(merge_item)
            merge_item[KEY_CURRENT_BRANCH], merge_item[KEY_LOOK_RESULT] = deduce_current_branch(merge_item) 
            if not is_relevant_branch(merge_item[KEY_REV_START], merge_item[KEY_CURRENT_BRANCH]): 
                return

            mergeconf.LOGGER.debug('current_branch: ' + merge_item[KEY_CURRENT_BRANCH])
            merge_item[KEY_NEXT_BRANCH] = branchutils.get_next_branch(merge_item[KEY_LOOK_RESULT], mergeconf.BRANCHES_MAP)

            if not is_next_branch_relevant(merge_item[KEY_REV_START], merge_item[KEY_CURRENT_BRANCH], merge_item[KEY_NEXT_BRANCH]): 
                return

            merge_item[KEY_CURRENT_BRANCH_URL] = branchutils.get_branch_url(merge_item[KEY_CURRENT_BRANCH])
            merge_item[KEY_NEXT_BRANCH_URL] = branchutils.get_branch_url(merge_item[KEY_NEXT_BRANCH])
            mergeconf.LOGGER.debug ('result: %s' % merge_item[KEY_LOOK_RESULT])
            merge_item[KEY_MESSAGE] = svnutils.get_commit_log_message(merge_item[KEY_REPO], merge_item[KEY_REV_START])
            merge_item[KEY_AUTHOR] = get_author(merge_item[KEY_REV_START], merge_item[KEY_REPO], merge_item[KEY_MESSAGE])
            merge_item[KEY_FILES_TO_IGNORE] = mergeconf.FILES_TO_IGNORE
            merge_item[KEY_AUTHORS_TO_IGNORE] = mergeconf.AUTHORS_TO_IGNORE

            if not branchutils.handle_merge_conditions(merge_item):
                return
            merge_to_branch = checkout_target_branch(merge_item[KEY_NEXT_BRANCH], merge_item[KEY_NEXT_BRANCH_URL], self.svn_utils)
            rev_as_str = self.svn_utils.merge_to_branch(merge_item[mergeconf.KEY_REV_START], merge_item.get(mergeconf.KEY_REV_END, None), merge_item[KEY_CURRENT_BRANCH_URL], merge_to_branch)
            self.commit_merged_code(merge_item[mergeconf.KEY_REV_START], merge_item.get(mergeconf.KEY_REV_END, None), merge_item[KEY_CURRENT_BRANCH], merge_item[KEY_NEXT_BRANCH], merge_item[KEY_MESSAGE] + '\n' + merge_item[KEY_LOOK_RESULT], merge_item[KEY_AUTHOR],
                                    merge_to_branch, rev_as_str)
        except:
            mergeconf.LOGGER.exception("failed performing merge please see further details")
            audit_write(AUDIT_OP_MERGE, merge_item[KEY_AUTHOR], merge_item[KEY_CURRENT_BRANCH],
                        merge_item[KEY_NEXT_BRANCH], merge_item[mergeconf.KEY_REV_START], merge_item[mergeconf.KEY_REV_START],
                        NA, NA, AUDIT_EXPL_EXCEPTION)

