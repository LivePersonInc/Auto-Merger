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

from merger.conf.mergeconf import APP_TITLE
from merger.conf import mergeconf

def get_failed_mergecommit_subject(current_branch_name, next_branch_name, author, rev_as_str):
    return APP_TITLE + ' Failed %s -> %s (rev %s author %s) merge' % (current_branch_name, next_branch_name, rev_as_str, author)


def get_failed_mergecommit_text(current_branch_name, next_branch_name, message, author, rev_as_str, commit_merge_result):
    return 'Hello, This is an automatic message from %s\n\nWhile I performed an automatic merge\nfrom branch: %s\nto branch: %s\nrevision: %s\nauthor: %s\non your commit, I failed due to conflict - please do manual merge\norig_message%s\n\nAfter you merge it please reply this mail that you merged' % (APP_TITLE, current_branch_name, next_branch_name, rev_as_str, author, message + '\n' + commit_merge_result)


def get_merge_success_subject(current_branch_name, next_branch_name, author, rev_as_str):
    return APP_TITLE + ' SUCCESS -> %s -> %s (rev %s author %s) merge' % (current_branch_name, next_branch_name, rev_as_str, author)


def get_merge_success_text(current_branch_name, next_branch_name, message, author, rev_as_str, commit_merge_result):
    return 'Hello, This is an automatic message from %s\r\n\nSuccessfully merged:\r\nfrom branch: %s\r\nto branch: %s\r\nrevision: %s\r\nauthor: %s\r\norig_message: %s\r\n\nPlease verify your merge done correctly at url: %s?key=%s  (go to last lines in this document and mark yes in confirmed column)' % (APP_TITLE, current_branch_name, next_branch_name, rev_as_str, author, message + '\n' + commit_merge_result, mergeconf.SPREADSHEET_BASEURL, mergeconf.SPREADSHEET_KEY)

def get_nextbranch_codefreeze_subject(next_branch):
    return 'Next branch in code freeze not merging: ' + next_branch + ' is below code freeze branch'


def get_nextbranch_codefreeze_text(revstart, current_branch, lookresult, next_branch, message, author):
    return 'Not meging to code freeze branch ' + next_branch + ' from branch: ' + current_branch + '\r\n' + 'By: ' + author + '\r\n' + 'Revision: ' + revstart + '\r\n' + 'Message: ' + message + '\r\n' + lookresult

def get_subject_excluded(current_branch):
    return 'Commit made to branch ' + current_branch + ' which is in exclusion for merges'


def get_text_excluded(revstart, current_branch, lookresult, message, author):
    return 'Commit made to branch ' + current_branch + ' which is in exlusion for merges\r\n' + 'By: ' + author + '\r\n' + 'Revision: ' + revstart + '\r\n' + 'Message: ' + message + '\r\n' + lookresult

def get_next_excluded_subject(next_branch):
    return 'Merge will not be done to branch ' + next_branch + ' which is in exclusion for merges'


def get_next_excluded_text(revstart, lookresult, next_branch, message, author):
    return 'Commit made to branch ' + next_branch + ' which is in exlusion for merges\r\n' + 'By: ' + author + '\r\n' + 'Revision: ' + revstart + '\r\n' + 'Message: ' + message + '\r\n' + lookresult

def get_auto_not_allowed_subject(next_branch):
    return 'Merge will not be done to branch ' + next_branch + ' automatic merges are not allowed'


def get_auto_not_allowed_text(revstart, current_branch, lookresult, message, author):
    return 'Commit made to branch ' + current_branch + '\n' + 'By: ' + author + '\n' + 'Revision: ' + revstart + '\n' + 'Message: ' + message + '\n' + lookresult

def say_up():
    print("""
                _              __  __                            _    _ _____  _
     /\        | |            |  \/  |                          | |  | |  __ \| |
    /  \  _   _| |_ ___ ______| \  / | ___ _ __ __ _  ___ _ __  | |  | | |__) | |
   / /\ \| | | | __/ _ \______| |\/| |/ _ \ '__/ _` |/ _ \ '__| | |  | |  ___/| |
  / ____ \ |_| | || (_) |     | |  | |  __/ | | (_| |  __/ |    | |__| | |    |_|
 /_/    \_\__,_|\__\___/      |_|  |_|\___|_|  \__, |\___|_|     \____/|_|    (_)
                                                __/ |
                                               |___/                             
					       
hey, don't forget to add the post commit hook example:
@echo off
d:
cd d:\vcs\Auto-Merger\src
python.exe main.py client %*
					       """)

