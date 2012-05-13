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
A nice place to access all configuration from.
"""

from merger.conf.mergeconfhelper import get_config, load_conf, get_branches_map
from merger.utils.loggerutils import initlogger
from merger.utils.shellutils import ShellUtils
import base64


##############################################
###         Configuraiton file 
##############################################
CONF_FILE_RELATIVE              = '/../../../conf/merger.conf'
ETC_CONF_FILEPATH               = '/etc/merger.conf'
CONFIGREADER                    = load_conf(CONF_FILE_RELATIVE, ETC_CONF_FILEPATH)

##############################################
# Core branching merging related configuration
##############################################
BRANCHES_TO_EXCLUDE             = [ item[1] for item in sorted(CONFIGREADER.items('branches'), key=lambda branch: branch[1]) if item[0].startswith("branch-exclude")]
BRANCHES_IN_CODE_FREEZE         = get_config(CONFIGREADER, 'branches', 'codefreeze-branches', default='').split(',')
BRANCHES                        = [ item[1] for item in sorted(CONFIGREADER.items('branches'), key=lambda branch: branch[1]) if item[0].startswith("branch")]
BASE_REPOSITORY_PATH            = get_config(CONFIGREADER, 'svn-repo', 'base-repository')
TMPDIR                          = get_config(CONFIGREADER, 'general', 'drive', default="") + get_config(CONFIGREADER,'general', 'tmpdir', default='/var/tmp')
SVN_USERNAME                    = get_config(CONFIGREADER, 'svn-repo', 'username')
SVN_PASSWORD                    = base64.decodestring(get_config(CONFIGREADER, 'svn-repo', 'pass'))
REPO                            = get_config(CONFIGREADER, 'svn-repo', 'REPO')

##############################################
#     CSV / Audit related configuration
##############################################
NA                              = 'N/A'
MERGE_PRODUCER_CSV              = TMPDIR + '/' + get_config(CONFIGREADER, 'general', 'producer-audit-file', default='merge_producer.csv')
CSV_STATUS_MERGE_IGNORED        = 'IGNORED'
CSV_STATUS_MERGE_FAILED         = 'FAILED'
CSV_STATUS_MERGE_PRODUCED       = 'PRODUCED'
CSV_STATUS_MERGE_SUCCESS        = 'SUCCESS'
CSV_FILE_OPEN_TYPE              = 'ab'
AUDIT_OP_MERGE                  = 'MERGE'
AUDIT_RES_FAILED_CONFLICT       = 'FAILED-POSSIBLE-CONFLICT'
AUDIT_RES_BRANCH_NOT_INF_CONF   = 'BRANCH_NOT_IN_CONF'
AUDIT_RES_NO_NEXT_BRANCH        = 'NO_NEXT_BRANCH'
AUDIT_EXPL_CODE_FREEZE          = 'CODE_FREEZE'
AUDIT_EXPL_EXCLUDED             = 'EXCLUDED'
AUDIT_EXPL_AUTO_NOT_ALLOWED     = 'AUTOMATIC_NOT_ALLOWED'
AUDIT_EXPL_EXCEPTION            = 'EXCEPTION'
TYPE_COL                        = 'type'



##############################################
# Auto-Merger server related configuration 
##############################################
MERGE_INTERVAL                  = int(get_config(CONFIGREADER, 'general', 'merge-interval', default=30))
IS_AUTOMATIC                    = True


##############################################
#      Messages related configuration
##############################################
APP_TITLE                       = get_config(CONFIGREADER, 'general', 'app-title', default='[Auto-Merger]')
APP_KEY                         = 'automerger'

##############################################
#       Commit log related configuration
##############################################
ISSUE_ID_PATTERN                = get_config(CONFIGREADER, 'general', 'issue-id-pattern', default='^issueid:\w(.*?)$')
ISSUE_ID_NAME                   = get_config(CONFIGREADER, 'general', 'issue-id-name', default='issueid')
ISSUE_ID_DEFAULT_VALUE          = get_config(CONFIGREADER, 'general', 'issue-default-value', default='0000')
CODEREVIEW_NAME                 = get_config(CONFIGREADER, 'general', 'codereview-name', default='corereview')
NOMERGE_KEY                     = 'NOMERGE'
ORIG_AUTHOR                     = 'orig_author'
ORIG_MESSAGE                    = 'orig_message'
TMPL_COMMIT_LOG_MSG             = '%s/' + 'svn.commit.log.message.rev.%s.txt' # (tmpdir,rev)





LOG_FILE_PATH                   = TMPDIR + '/' + get_config(CONFIGREADER, 'general', 'log-file', default='automerger.log')
VERSION_PREFIX                  = get_config(CONFIGREADER, 'general', 'version-prefix')
VERSION_PREFIX_FILTER           = get_config(CONFIGREADER, 'general', 'version-prefix-filter')
VERSIONS_REPOSITORY             = get_config(CONFIGREADER, 'general', 'versions-repository')

LOGGER                          = initlogger(APP_KEY, LOG_FILE_PATH, SVN_PASSWORD)
M_SHU                           = ShellUtils(LOGGER)
MERGE_SERVER_URL                = 'http://' + get_config(CONFIGREADER, 'general', 'host', default='localhost') + ':' + get_config(CONFIGREADER, 'general', 'port', default='8080') + '/?%s'

FILES_TO_IGNORE_STR             = get_config(CONFIGREADER, 'general', 'files-to-ignore')
FILES_TO_IGNORE                 = FILES_TO_IGNORE_STR.split(',') if FILES_TO_IGNORE_STR else None
AUTHORS_TO_IGNORE_STR           = get_config(CONFIGREADER, 'general', 'authors-to-ignore')
AUTHORS_TO_IGNORE               = AUTHORS_TO_IGNORE_STR.split(',') if AUTHORS_TO_IGNORE_STR else None


ENUM_CODE_FREEZE                = 0
ENUM_EXCLUDED                   = 1
ENUM_MERGE                      = 2


def get_dl(recipient, state):
    """Get delivery list for email sending, can be different
    for code freeze branches, excluded branches, or merge branches.
    
    Args:
      recipient: The main receipient, ie the original committer.
      state: Merge success / fail / excluded / code freeze.
    """
    recipient = recipient + "@" + EMAIL_DOMAIN
    if state == ENUM_CODE_FREEZE:
        return [recipient] + DL_FREEZE
    if state == ENUM_MERGE:
        return [recipient] + DL_MERGE
    if state == ENUM_EXCLUDED:
        return [recipient] + DL_EXCLUDED


############################################## 
#          Mail configurations
##############################################
MAIL_USERNAME                   = get_config(CONFIGREADER, 'mail', 'username')
MAIL_PASSWORD                   = base64.decodestring(get_config(CONFIGREADER, 'mail', 'pass'))
MAIL_CODE_FREEZE_DIST_LIST      = MAIL_USERNAME
MAIL_DEFAULT_DISTRIBUTION_LIST  = MAIL_USERNAME 
MAIL_FROM_NAME                  = get_config(CONFIGREADER, 'mail', 'from')
MAIL_ENABLED                    = CONFIGREADER.getboolean('mail', 'mail-enabled')
DL_MERGE                        = get_config(CONFIGREADER, 'mail', 'dl-merge').split(',')
DL_FREEZE                       = get_config(CONFIGREADER, 'mail', 'dl-freeze').split(',')
DL_EXCLUDED                     = get_config(CONFIGREADER, 'mail', 'dl-excluded').split(',')
SMTP_HOST                       = get_config(CONFIGREADER, 'mail', 'smtp-host', default='smtp.gmail.com')
SMTP_PORT                       = int(get_config(CONFIGREADER, 'mail', 'smtp-port', default=587))
EMAIL_DOMAIN                    = get_config(CONFIGREADER, 'mail', 'email-domain', default=None)

KEY_REPO                        = 'repo'
KEY_REV_START                   = 'rev_start'
KEY_REV_END                     = 'rev_end'
KEY_SOURCE_BRANCH_NAME          = 'source_branch_name'
KEY_TARGET_BRANCH_NAME          = 'target_branch_name'
KEY_SVN_USERNAME                = 'SVN_USERNAME'
KEY_SVN_PASSWORD                = 'SVN_PASSWORD'
KEY_IS_MANUAL                   = 'is_manual'
KEY_CURRENT_BRANCH              = 'current_branch'
KEY_LOOK_RESULT                 = 'look_result'
KEY_NEXT_BRANCH                 = 'next_branch'
KEY_NEXT_BRANCH_URL             = 'next_branch_url'
KEY_CURRENT_BRANCH_URL          = 'current_branch_url'
KEY_MESSAGE                     = 'message_key'
KEY_AUTHOR                      = 'author_key'
KEY_FILES_TO_IGNORE             = 'file_to_ignore'
KEY_AUTHORS_TO_IGNORE           = 'authors_to_ignore'


##############################################
#        Spreadsheet configurations
##############################################
SPREADSHEET_ENABLED_STR         = get_config(CONFIGREADER, 'spreadsheet', 'is-enabled', default='False')
SPREADSHEET_ENABLED             = SPREADSHEET_ENABLED_STR == 'True' 
SPREADSHEET_KEY                 = get_config(CONFIGREADER, 'spreadsheet', 'key')
SPREADSHEET_BASEURL             = get_config(CONFIGREADER, 'spreadsheet', 'baseurl')
SPREADSHEET_WORKSHEET_ID        = get_config(CONFIGREADER, 'spreadsheet', 'worksheet-id', default='0d6')
SPREADSHEET_MERGE_FAILED        = get_config(CONFIGREADER, 'spreadsheet', 'merge-failed', default='merge-failed')
SPREADSHEET_MERGE               = 'merge'
SPREADSHEET_AUTHOR_PREFIX       = 'auto-'
SPREADSHEET_CONFLICT_MSG        = 'CONFLICT'
SPREADSHEET_USERNAME            = get_config(CONFIGREADER, 'spreadsheet', 'username')
SPREADSHEET_PASSWORD_RAW        = get_config(CONFIGREADER, 'spreadsheet', 'password')
SPREADSHEET_PASSWORD            = base64.decodestring(SPREADSHEET_PASSWORD_RAW) if SPREADSHEET_PASSWORD_RAW else None

##############################################
#          General configuration
##############################################
VERSION                         = '2.5'
BRANCHES_MAP                    = get_branches_map(CONFIGREADER.items('branches'))
