Auto-Merger
===========
.Auto merger combines the benefits of multiple branches and continuous integration.  Auto merger “propagates” all commits performed on a repository.  While propagating, it deduces by its configuration if a commit should be merged into further branches.  If yes, it propagates the commit immediately from one branch to the next.   During its operation it’s sending notifications to committers (and other predefined delivery list) to verify the correctness of merges performed on behalf of them.  In case of failures (in most cases conflicts which requires a human to resolve) it will ask committer to resolve, merge, and then to confirm.
.
Auto-merger provides various reports to check backwards the merge-completeness status of branches.  It’s filling up automatically an  online spreadsheet, an audit file, and a web based online report which tries to detect separately from it’s actual merge operation, which merges were not verified or not done.  All this, in order to assist querying the merge-health of branches.

What?
=====
![What does it do](https://sites.google.com/site/thedevtips/Home/linux/automerger-branches.png)

you configure which branches you have and over which rules you want automatic merges, auto merger will automatically perform it for you, commit into 1.0.0 your commit will be propagated into next branches automatically.

How?
====
![How does it work](https://sites.google.com/site/thedevtips/Home/linux/automerger-sequence.png)

Design?
=======
![How about its design?](https://sites.google.com/site/thedevtips/Home/linux/automerger-design.png)

Sounds great! how to install it?
================================
Just go ahead and clone it, run python ./main.py from src directory.
(you should have web.py, gdata, mock.py in your PYTHONPATH)
see that you have a properly configured merger.conf
(if you have any questions let me know)

Configuration?
==============
Have a look at conf/merger.conf it contains an example configuration.

you need to define the base url to your repository (currently automerger supports a single repository). so you define it under:
you need to have an `[svn-repo]` section and under this section place the base url to your svn repository example:

```
[svn-repo]
base-repository = http://mysvnserver/myrepo
```

note automerger will expect every item separated by `,` in section `[branches]` to be a postfix to this base  url.
so if you can access your project with `http://mysvnserver/myrepo/MyProjectA/trunk` then in next section in branches every branch will start from
trunk or your specific version name as you already specified the base url in `base-repository`

in `[branches]` section.  This section describes your projects.
Each "project" merging flow will have a "row" in that section.  So if you have 3 projects.  `MyProjectA`, `MyProjectB`, `MyProjectC` where `MyProjectA` has 3 branches `trunk`,`1.0`,`1.1`
 and you wish 1.0 to be merged into 1.1 and then 1.1 to be merged into trunk you will have the following line:

```
[branches]
some_signifying_name_for_project_choose_whatever_you_want=MyProjectA/1.0,MyProjectA/1.1,MyProjectA/trunk
```
you see, `MyProjectA/1.0` is the relative path to `MyProjectA/1.0` under `http://mysvnserver/myrepo`.

*Whenever do a commit, automerger will scan all projects under `[branches]` if there is a match meaning you have committed
to ANY project under `[branches]` it will then check if there is another branches specified after it with a `,` if yes it will
simply try to merge into it.  Then as it will commit the merge it will be triggered again to the next branch ofcourse.

## Automerver client / server notations explained.
Automerver listens to every commit made by an svn hook.  This means you will need to install an svn hook in your `post-commit` script.  `post-commit` hook will then call auto-merer server for each `commit` the server is now responsible for actually performing the merge (checkout target branch, merge, commit target branch).

An example `post-commit` hooks looks as following:
```bash
#!/bin/sh
cd  /opt/auto-merger/src/
echo commit-hook trigered  >> /var/log/automerger.log
/usr/bin/python /opt/auto-merger/src/postcommit.py $1 $2
```
all it does is call automerger's postcommit.py with the args ($1 $2) which the svn commit passes it (the repo home and the commit revision), `postcommit.py` which is poart of automerger is then responsible for calling automerger server for further merging.

Development?
====================
Same guidelines here can be utilized in order to start up automerger.
We recommend using virtualenv for development, this would easy dependency management and local dependency scoping.
Install pip (for more information http://www.pip-installer.org/en/latest/installing.html)
checkout Auto-Merger project and install virtualenv on its root (for more information http://http://docs.python-guide.org/en/latest/dev/virtualenvs/)

in following example we will clone automerger to `~/tmp folder`

```bash
~/tmp$ git clone https://github.com/liveperson/Auto-Merger.git
```

now lets change to automerger cloned dir

```bash
~/tmp$ cd Auto-Merger/
```

Create a virtualenv called venv (will appear as a folder inside Auto-Merger)

```bash
~/tmp/Auto-Merger$ virtualenv venv
```

Activate venv

```bash
source venv/bin/activate
```

Install gdata dependency (for more information see: http://pythonhosted.org/gdata/installation.html)

```bash
pip install gdata
```

Install web.py (http://webpy.org/install)

```bash
pip install web.py
```

Start up the server

```bash
cd src
python ./main.py
```

On success you will see:

<pre>
                _              __  __                            _    _ _____  _
     /\        | |            |  \/  |                          | |  | |  __ \| |
    /  \  _   _| |_ ___ ______| \  / | ___ _ __ __ _  ___ _ __  | |  | | |__) | |
   / /\ \| | | | __/ _ \______| |\/| |/ _ \ '__/ _` |/ _ \ '__| | |  | |  ___/| |
  / ____ \ |_| | || (_) |     | |  | |  __/ | | (_| |  __/ |    | |__| | |    |_|
 /_/    \_\__,_|\__\___/      |_|  |_|\___|_|  \__, |\___|_|     \____/|_|    (_)
                                                __/ |
                                               |___/
</pre>

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
**A:** Feel free to contact us with questions.

**Q:** I don't see `Run` context menu item when right clicking any test file, how can I run the tests from `intellij`?
**A:** From `intellij`: Project Settings --> Facets --> Add python facet to the project.  If did not work edit `.idea/github-automerger.iml` and set the following params (if already exist and point to wrong directory)
```xml
    <output url="file://$MODULE_DIR$/outputurl" />
    <output-test url="file://$MODULE_DIR$/outputtest" />
```