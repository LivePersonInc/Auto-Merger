Auto-Merger
===========
Auto merger combines the benefits of multiple branches and continuous integration which is opposed to having multiple branches in general.  Auto merger “propagates” to all commits performed on a repository.  While propagating, it deduces by its configuration if a commit should be merged into further branches.  If yes, it propagates the commit immediately from one branch to the next.   During its operation it’s sending notifications to committers (and other predefined delivery list) to verify the correctness of merges performed on behalf of them.  In case of failures (in most cases conflicts which requires a human to resolve) it will ask committer to resolve, merge, and then to confirm...

Auto-merger provides various reports to check backwards the merge-completeness status of branches.  It’s filling up automatically an  online spreadsheet, an audit file, and a web based online report which tries to detect separately from it’s actual merge operation, which merges were not verified or not done.  All this, in order to assist querying the merge-health of branches.

FAQ
---

**Q:** When i'm asked by auto merger to perform a manual merge, how do I do that?  
**A:** Use plain svn merge command, otherwise, use standard utilities (tortoise svn --> merge or intellij or whichever IDE you use). It's important to perform the merge on the target root folder in order to avoid seeing in future redundant files being committed upon merges (this is an internal svn issue).


**Q:** I see more files merged (/ to merge) than i originally committed, why is that?  
**A:** This is not an auto merger issue, svn requires a cleanup see: http://blog.syntevo.net/2011/03/16/1300268640000.html .


**Q:** The branch my commit was merged to is not the correct branch, what do i do?  
**A:** Check this out with configuration file, specifically check that configuration files are pointing to branches as you expect.  You can also have a look at any email you get from auto merger it specifies the current list of branches it handles, other branches are not merged.


**Q:** My merge failed but i don't see any reason for it to fail.  
**A:** This may be caused by a temporal problem with svn, do manual merge as if this was a conflict.


**Q:** We are about to release/code freeze a branch how do I know its merge-complete?  
**A:** Auto merger and svn itself both provides various reports, consult the various reports , see svn logs for your branch, see spreadsheet report, audit file, web report, if you don't plan to use the reports to review that a branch is merge complete, don't use auto merger.


**Q:** How can I trust that auto merging is semantically correct?  
**A:** You canno't (not because of auto merger but because of the inherent automatic svn merge command used which is a mechanical command not performed by a human), you are encouraged (and asked) to verify that its semantically correct as only a human can verify it (+ continuous integration tests), have a look at the merge which was performed for you (sources committed) see that its what you expect to be committed, note that auto merger asks you to verify semantic correctness of merges.


**Q:** What are the alternatives for using auto merger?  
**A:** 
Do not branch - so you do not need to merge.  
Modularization - so branching and merging are encapsulated and managed within teams.  
Contributors / Maintainers separation - so only a few maintainers can commit & merge..  
Heavy procedures - ton’s of procedures to verify all that is committed should be committed (and to all proper places), and whatever should not - is not.  
Do not merge - leave the code unmerged.  
Enforce to use latest - if a bug is found upgrade to latest.  
Automatic tools.  
Human mergers - which continuously perform merge.  
Every developer is responsible for his commits - so he is responsible to merge them to all future branches.  


**Q:** Doesn't git solves all merging problems?  
**A:** No, while git has a better merge algorithm it does not perform auto merging. (git has gerrit which is somewhat what auto-merger is to svn, so both required a tool problem to handle a similar but not the same problem).  

**Q:** Which modules is auto merger dependant on?  
**A:** web.py, gdata, mock.py

**Q:** I have other question which was not answered here.  
**A:** Feel free to contact us with questions
