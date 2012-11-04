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
postcommit hook will post here a request to merger, 
(you can also send requests if you like its plain http)
"""

from Queue import Queue
from merger.conf import mergeconf
from merger.conf.mergeconf import MERGE_INTERVAL
from merger.logic.mergeworker import MergeWorker
from merger.utils.merge_messages import say_up
from web import form
import logging
import os
import threading
import time
import urllib
import web


class ConsumeFromQueue(threading.Thread):
    """Take a merge work unit from queue and process it."""
    
    def __init__(self, threadname, queue):
        """Initialize the thread to consume from queue.
    
        Args:
          threadname: This consumer thread name.
        """
        threading.Thread.__init__(self, name=threadname)
        self.mergequeue = queue

    def run(self):
        """Process the work unit (merge) from queue."""
        while True: # Check pending merges.
            time.sleep(MERGE_INTERVAL) # check out the queue, if new merges to be done, perform.
            merge_item = self.mergequeue.get() # get next merge to perform (usually pushed by client - post commit hook).
            logging.info("%s read %s" % (self.getName(), merge_item))
            worker = MergeWorker()
            logging.info("merge consumer merging repo: %s , [is_manual: %s], revstart %s source branch: %s target branch: %s svn_username: %s" % (
                 merge_item[mergeconf.KEY_REPO], merge_item.get(mergeconf.KEY_IS_MANUAL, None), 
                 merge_item[mergeconf.KEY_REV_START], merge_item.get(mergeconf.KEY_SOURCE_BRANCH_NAME, None), 
                 merge_item.get(mergeconf.KEY_TARGET_BRANCH_NAME, None), 
                 merge_item.get(mergeconf.KEY_SVN_USERNAME, None)))
            logging.info("branches in conf: " + str(mergeconf.BRANCHES))
            worker.do_merge(merge_item)
  



class MergeServer():
    """
    client(producer) and server(consumer).
    The client is the postcommit hook placed in svn hooks folder it is the postcommit.py .
    The client then calls a url in the server and passes it the minimal required parameters
    in order to perform the merger.
    The server accepts these parameters and starts the actual process of merging.
    """
    def __init__(self, alogger, mergesconsumer):
        """Server startup, check if new commits are pending in queue, pass it to the consumer thread.
           
           Args:
            LOGGER: Logging facade to be used.
            mergeconsumer: The worker thread to process the merge.
           
           Returns:
             Nothing, though server is initialized and waits for queue to be filled by commit work units.
        """
        self.logger = alogger
        self.mergesconsumer = mergesconsumer
        self.mergequeue = myqueue
        

def filter_version(version):
    """
       When preseting the web version for user to choose for to merge from and to filter them:
       ie. if you have a folder deliveries with these subfolders
           deliveries/v1.0
           deliveries/v1.0_snapshot
           deliveries/v1.1
           
        then you might want to filter the snapshot, you can do that via configuration via this method.
       
       Returns:
         Nothing, though server is initialized and waits for queue to be filled by commit work units.
    """
    return version.find(mergeconf.VERSION_PREFIX_FILTER) == 0

def get_versions():
    """In manual merges: This enables the web based UI which presents all the versions of the software
        so that user can choose the VERSION to merge from and too (manually).

    Returns:
      Map of all versions available for manual merges.
    """
    logging.info('getting releases list.')
    versions = os.listdir(mergeconf.VERSIONS_REPOSITORY)
    versions.reverse()
    logging.info('versions before filter: ' + str(versions))
    versions = [VERSION for VERSION in versions if filter_version(VERSION)]
    versions = map(lambda name:name.replace(mergeconf.VERSION_PREFIX, ''), versions)
    logging.info('versions after filter: ' + str(versions))
    return versions

def mergeform():
    """In manual merges: create a web based UI for the merge html form.
        This will create the various selection boxes and input texts
        to allow the user to manually merge branches.

    Returns:
      A web.py form representation of the input fields in the manual merge page.
    """
    aform = form.Form(
        form.Dropdown('merge_from', get_versions()),
        form.Dropdown('merge_to', get_versions()),
        form.Textbox('start_rev', form.notnull, post="Start revision to merge"),
        form.Textbox('end_rev', form.notnull, post="End revision to merge"),
        form.Textbox('svn_username', form.notnull, post="Your SVN username (we will commit with this)"),
        form.Password('svn_password', form.notnull, post="your SVN password"))
    return aform

def validateform():
    """In manual merges: create a web based UI for the merge html form.
        This will create the various selection boxes and input texts
        to allow the user to manually merge branches.

    Returns:
      A web.py form representation of the input fields in the manual merge page.
    """
    aform = form.Form(
        form.Dropdown('Branch to validate', get_versions()),
        form.Textbox('SVN username', form.notnull),
        form.Password('SVN password', form.notnull))
    return aform


class index:
    """web.py index page which is used in manual merges.
        This screen presents the 

    Returns:
      A web.py form representation of the input fields in the manual merge page.
    """
    def GET(self):
        """web.py server was called with GET method, check if a merging request was made 
        """
        global mergeserver
        i = web.input(rev_end=None, source_branch_name=None, target_branch_name=None,
                      svn_username=None, svn_password=None, is_manual=False)
        message = 'Merging r%s repo: %s' % (str(i.rev_start), i.repo)
        mergeconf.LOGGER.debug(message)
        pending_merge_items = {}
        pending_merge_items[mergeconf.KEY_REPO] = i.repo
        pending_merge_items[mergeconf.KEY_REV_START] = i.rev_start
        pending_merge_items[mergeconf.KEY_REV_END] = i.rev_end
        pending_merge_items[mergeconf.KEY_SOURCE_BRANCH_NAME] = i.source_branch_name
        pending_merge_items[mergeconf.KEY_TARGET_BRANCH_NAME] = i.target_branch_name
        pending_merge_items[mergeconf.KEY_SVN_USERNAME] = i.svn_username
        pending_merge_items[mergeconf.KEY_SVN_PASSWORD] = i.svn_password
        pending_merge_items[mergeconf.KEY_IS_MANUAL] = i.is_manual
        mergeconf.LOGGER.info("adding merge item: " + str(pending_merge_items))
        myqueue.put_nowait(pending_merge_items)
        return message

class merge:
    def POST(self): 
        """web.py /merge POST request as a result of user submitting a manual requst for merge.
        """
        logging.info('got to post')
        i = web.input()
        params = urllib.urlencode({mergeconf.KEY_REPO: mergeconf.REPO, mergeconf.KEY_SOURCE_BRANCH_NAME: i.merge_from,
                                   mergeconf.KEY_TARGET_BRANCH_NAME: i.merge_to, mergeconf.KEY_REV_START: i.start_rev,
                                   mergeconf.KEY_REV_END: i.end_rev,
                                   mergeconf.KEY_SVN_USERNAME: i.svn_username,
                                   mergeconf.KEY_SVN_PASSWORD: i.svn_password,
                                   mergeconf.KEY_IS_MANUAL: True})
        try:
            urltocall = mergeconf.MERGE_SERVER_URL % params
            logging.info(urltocall)
            urllib.urlopen(mergeconf.MERGE_SERVER_URL % params)
            return '<html><body>Starting merge check result at: \var\tmp\automerger.log</body></html>'
        except:
            mergeconf.LOGGER.exception("exception occured")

def start_webpy():
    web.config.debug = False
    urls = ('/', 'index', '/merge', 'merge')
    app = web.application(urls, globals())
    consumer = ConsumeFromQueue("Consumer", myqueue)
    consumer.start()
    web.internalerror = web.debugerror
    say_up()
    app.run()

myqueue = Queue()

if __name__ == "__main__":
    start_webpy()
