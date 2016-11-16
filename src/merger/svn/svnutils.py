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
General svn utilities, used heavily as auto merger works with svn.
"""

from merger.conf import mergeconf
from merger.conf.mergeconf import M_SHU, TMPL_COMMIT_LOG_MSG, TMPDIR, NA
from merger.utils.shellutils import ShellUtils
import logging
import os
import re


COMMIT_TMPL                 = 'svn commit %s -F %s --username %s --password %s'
CLEANUP_TMPL                = 'svn cleanup %s/%s --username %s --password %s'
REVERT_TMPL                 = 'svn revert -R %s/%s --username %s --password %s'
UPDATE_TMPL                 = 'svn update --force %s/%s --username %s --password %s'
CO_TMPL                     = 'svn co %s %s/%s --force --username %s --password %s'
MERGE_TMPL                  = '''svn merge --non-interactive -r %s:%s %s %s/%s 
                                + '--username %s --password %s'''
LOG_TMPL                    = 'svn log %s -r %s:%s'
LOG_URL_TMP                 = 'svn log -v %s -r %s:%s --username %s --password %s %s %s'
LOOK_CHANGED_TMPL           = 'svnlook changed --revision %s %s'
LOOK_AUTH_TMPL              = 'svnlook author --revision %s %s'
LOOK_LOG_TMPL               = 'svnlook log --revision %s %s'

MESSAGE_ABORT_COMMIT        = 'Aborting commit'
MESSAGE_SUCCESSFUL_COMMIT   = 'Committed revision'


def get_commit_log_message(repo, rev):
    """
        Here we compute the commit log message after merge.
        In this commit log message we will include details about
        the merge that was performed, who was original committer etc.
        Args:
            repo: Repository on which the original commit was perforemd.
            rev: The revision that was originally committed from it the 
                merge was performed.
        Returns:
            The message which will be provided to the commit.
    """
    svnlook_log_cmd = LOOK_LOG_TMPL % (rev, repo)
    mergeconf.LOGGER.debug('svn look log command: %s ' % svnlook_log_cmd)
    message = M_SHU.runshellcmd(svnlook_log_cmd)
    mergeconf.LOGGER.debug('log result: %s ' % message)
    return message

def get_files_by_log(log):
    """
    Return the list of files from svn log -v
    Arguments:
        url: The log produced by svn log -v
    Returns: 
        A list of file paths which were updated by the svn log verbose message.
    """
    fileslines = []
    for line in log.splitlines():
        if (line.strip().startswith('A ') or line.strip().startswith('D ') 
            or line.strip().startswith('M ') or line.strip().startswith('R ')):
            fileslines.append(line)
    return fileslines


class SVNCmdParams:
    """
    Parameters for running various svn command.
    """
    def __init__(self, **kwargs):
        prop_defaults = {
            "username": None, 
            "password": None,
            "tmpdir": None,
            "logger": None,
            "url": None,
            "startdate": None,
            "enddate": None,
            "isxml": False,
            "stoponcopy": False
        }
        self.__dict__.update(prop_defaults) 
        self.__dict__.update(kwargs)   
        self.username = self.__dict__["username"]
        self.password = self.__dict__["password"]
        self.tmpdir = self.__dict__["tmpdir"]
        self.logger = self.__dict__["logger"]
        self.url = self.__dict__["url"]
        self.startdate = self.__dict__["startdate"]
        self.enddate = self.__dict__["enddate"]
        self.isxml = self.__dict__["isxml"]
        self.stoponcopy = self.__dict__["stoponcopy"]

class SVNUtils:
    """
    General svn utilities, used heavily as auto merger works with svn.
    """
    def __init__(self, svn_cmd_params):
        self.logger = svn_cmd_params.logger
        self.tmpdir = svn_cmd_params.tmpdir
        self.username = svn_cmd_params.username
        self.password = svn_cmd_params.password
        self.shellutils = ShellUtils(svn_cmd_params.logger)

    def log(self, url, startdate, enddate, isxml=False, stoponcopy=False):
        """
        Run svn log commmand.
        """
        logcommand = LOG_URL_TMP % (url, '{' + startdate + '}', '{' + enddate + '}', self.username, self.password, 
                                    ' --xml' if isxml else '', ' --stop-on-copy' if stoponcopy else '')
        logging.info(logcommand)
        return M_SHU.runshellcmd(logcommand)

    def get_log_message(self, url, rev):
        """
        Get commit log message by url and revision
        Arguments:
            url: Url to get commit log message for.
            rev: Revision to get the commit log message for the url above.
        Returns: 
            The message which was committed on revision rev on url specified.
        """
        mergeconf.LOGGER.debug("Commit log message for url [%s] with rev [%s]" % (url, rev))
        log_cmd = (LOG_URL_TMP % (url, rev, rev, self.username, self.password))
        return M_SHU.runshellcmd(log_cmd)

        
    def commit(self, fileordir_to_commit, message, rev):
        """
        Commit files into svn repository with message specified.
        Arguments:
            fileordir_to_commit: The working directory (or file) to commit to svn - path to them.
            message: The message to commit with (-m)
            rev: We are going to write an internal temporary file with the message 
                we will use this rev for its naming convention.
        Returns: The message response from svn server.
        """
        mergeconf.LOGGER.debug("Committing file/dir %s with message %s" % 
                               (fileordir_to_commit, message))
        message_file_name = TMPL_COMMIT_LOG_MSG % (self.tmpdir, rev)
        message_file_name_org = message_file_name + '.org'
        mergeconf.LOGGER.debug("Creating message file: %s" % 
                               (message_file_name_org))
        message_file = open(message_file_name_org, 'w')
        try:
            message_file.write(message)
            message_file.close()
            svn_commit_merged_cmd = (COMMIT_TMPL % 
                                     (fileordir_to_commit, message_file_name, 
                                      self.username, self.password))
            initial_msg_file = open(message_file_name_org, 'rb')
            msg_file = open(message_file_name, 'wb')
            for line in initial_msg_file:
                line = line.replace('\r', '')
                line = line.replace('\n', '')
                if line != '':
                    msg_file.write(line + '\n')
            initial_msg_file.close()
            msg_file.close()
            result = self.shellutils.runshellcmd(svn_commit_merged_cmd)
            mergeconf.LOGGER.debug(svn_commit_merged_cmd)
        finally:
            os.remove(message_file_name)
        mergeconf.LOGGER.debug('returning result: ' + result)
        return result


    def update_local_workbranch(self, branch_dir):
        """Does everything it can to verify the current 
            working branch which is being used for merges is updated 
            and synced with svn so we can perform the merge 
            on this local branch.
            
            Args:
                merge_to_branch: The branch name we want to merge a commit into.
                user: Auto merging will use this svn username to perform the merge.
                pass: Auto merging will use this svn password to perform the merge.
            Returns:
                Nothing, local working branch will be updated in order to perform the auto merge.
        """
        M_SHU.runshellcmd(CLEANUP_TMPL % (TMPDIR, branch_dir, self.username, self.password))
        M_SHU.runshellcmd(REVERT_TMPL % (TMPDIR, branch_dir, self.username, self.password))
        M_SHU.runshellcmd(UPDATE_TMPL % (TMPDIR, branch_dir, self.username, self.password))

    def checkout(self, url, tolocation):
        """Given a branch url check it out to the local disk.
            
            Args:
                url: The branch to check out.
                tolocation: Location on disk to check out to.
                svn_username: Auto merging will use this svn username to perform the checkout.
                svn_password: Auto merging will use this svn password to perform the checkout.
            Returns:
                Nothing, the branch specified in url will be checked out to local disk.
        """
        checkout_cmd = CO_TMPL % (url, TMPDIR, tolocation + '/', self.username, self.password)
        M_SHU.runshellcmd(checkout_cmd) # branch to merge to does not exist in disk, check it out from svn.

    def merge_to_branch(self, revstart, revend=None, merge_from_url=None,
                        merge_to_branch=None):
        """Given a branch url merge it into a local branch.
            
            Args:
                merge_from_url: The url to merge from.
                merge_to_branch: The branch to merge to.
                revstart: Rev to merge from.
                revend: If not specified only revstart is merged otherwise merging a range of revisions.
                svn_username: Auto merging will use this svn username to perform the merge.
                svn_password: Auto merging will use this svn password to perform the merge.
            Returns:
                Nothing, The branch will be synced on disk.
        """
        mergeconf.LOGGER.debug('\nMerging...')
        prev_rev = int(revstart) - 1 # In svn when merging single revision then merging from merge_rev - 1 to merge_rev
        prev_rev_as_str = str(prev_rev)
        if revend is None:
            rev_as_str = str(revstart)
        else:
            rev_as_str = str(revend)
        svn_merge_cmd = MERGE_TMPL % (prev_rev_as_str, rev_as_str, merge_from_url, TMPDIR, get_branch_dir
                (merge_to_branch), self.username, self.password)
        mergeconf.LOGGER.debug('merge cmd: : ' + svn_merge_cmd)
        merge_result = M_SHU.runshellcmd(svn_merge_cmd)
        mergeconf.LOGGER.debug('merge result:' + merge_result)
        mergeconf.LOGGER.debug('merge cmd: : ' + svn_merge_cmd)
        return rev_as_str

def get_branch_dir(branch_name):
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
    return branch_name.replace('/', '_')



def get_branch_col(svn_look_line, branches_map):
    """
        For each project we have a list of branches which should be merged for it.
        this method will take the svn_look_line returned by svn look command
        and return the relevant branches map for it.
        
        Args:
            svn_look_line: Will deduce the relevant branches and project for this svn look line.
            BRANCHES_MAP: All projects with all their assigned branches.
        Returns:
            The relevant branches for the provided svn look line.
    """
    for branches_col in branches_map:
        for branch in branches_map[branches_col]:
            if svn_look_line.find(branch) != -1:
                return branches_map[branches_col]

def get_branch_by_look(svn_look_line, BRANCHES_MAP):
    """
        Example: for Branches/myapp/ver1/src/main/java/myfile.java will return Branches/myapp/ver1

        Args:
            svn_look_line: Will deduce the relevant branches and project for this svn look line.
            BRANCHES_MAP: All projects with all their assigned branches.
        Returns:
            The branch path for the provided svn look line.
    """
    mergeconf.LOGGER.debug('get_branch_by_look: svn_look_line: ' + svn_look_line + ', BRANCHES_MAP: ' + str(BRANCHES_MAP))
    for branches_col in BRANCHES_MAP:
        for branch in BRANCHES_MAP[branches_col]:
            mergeconf.LOGGER.debug('get_branch_by_look: svn_look_line: ' + svn_look_line + ', branch: ' + branch)
            if svn_look_line.find(branch) != -1:
                return branch

def get_branch_url(name):
    """
        Based on a branch name give its full url into svn.

        Args:
            name: The branch name (as provided in configuration branches).
        Returns:
            The branch full svn url.
    """
    return mergeconf.BASE_REPOSITORY_PATH + '/' + name 

def get_next_branch(svn_look_line, branches_map):
    """
        Get the actual branch that comes next to committed one - the branch to merge to.

        Args:
            svn_look_line: svn look line for a commit.
            BRANCHES_MAP: A map containing sequence of branches per project.
        Returns:
            The next branch name to do the auto merge into.
    """
    branches_col = get_branch_col(svn_look_line, branches_map)
    for index, branch in enumerate(branches_col):
        if (svn_look_line.find(branch) != -1):
            if len(branches_col) > (index + 1):
                return branches_col[index + 1]
    return None

def get_commit_rev_by_resp(commit_resp):
    """After performing a commit svn returns to stdout its committed version,
        parse it in order to get the new committed version number.
        
        Args:
            commit_resp: The stdout response out of commit command to svn
                in case failed to find commit revision returns NA
        Returns:
            The committed revision id.
    """
    rev = NA
    if commit_resp is not None:
        searchresult = re.compile(r"Committed revision (.*?)\.",
            re.DOTALL | re.MULTILINE).search(commit_resp)
        if searchresult is not None:
            results = searchresult.groups()
            if len(results) > 0: 
                rev = results[0]
    return rev


svnparams = SVNCmdParams(username=mergeconf.SVN_USERNAME, password=mergeconf.SVN_PASSWORD, tmpdir=TMPDIR, logger=mergeconf.LOGGER)
SVNUTILS = SVNUtils(svnparams)
