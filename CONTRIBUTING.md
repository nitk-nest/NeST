# Contributing to NeST

#### Table Of Contents
[How Can I Contribute?](#how-can-i-contribute)
  * [Reporting Bugs](#reporting-bugs)
  * [Suggesting Enhancements](#suggesting-enhancements)
  * [Code Contribution](#code-contribution)
  * [MR conflicts resolution](#mr-conflicts-resolution)

[Styleguides](#styleguides)
  * [Git Commit Messages](#git-commit-messages)
  * [Documentation Style](#documentation-style)
  * [Code Style](#code-style)

## How Can I Contribute?

### Quick Introduction to NeST

For Contributing, you will need some basic understanding of the main features
of NeST. We recommend going over [this](https://blog.apnic.net/2020/09/18/nest-a-simpleefficient-tool-to-study-congestion-control/)
to get a brief overview of NeST.

### Reporting Bugs

To report a bug in NeST, do the following

* Check if the bug is already an issue [here](https://gitlab.com/nitk-nest/nest/-/issues?scope=all&utf8=%E2%9C%93&state=opened&label_name[]=bug)
* Create a new issue [here](https://gitlab.com/nitk-nest/nest/-/issues/new?issue%5Bassignee_id%5D=&issue%5Bmilestone_id%5D=)
* Add the label 'bug'

### Suggesting Enhancements

To suggest an enhancement (i.e., new feature), you can do the following

* Check if the enhancement is already suggested
[here](https://gitlab.com/nitk-nest/nest/-/issues?scope=all&utf8=%E2%9C%93&state=opened&label_name[]=enhancement)
* Create a new issue [here](https://gitlab.com/nitk-nest/nest/-/issues/new?issue%5Bassignee_id%5D=&issue%5Bmilestone_id%5D=)
* Add the label 'enhancement'

### Code Contribution

Code contributions can be in the form of resolving bugs or implementing new
features.

Before contributing code, go over the [issues](https://gitlab.com/nitk-nest/nest/-/issues)
on GitLab. If there is already an open issue that is similar to your idea, then
you can leave a comment in the issue mentioning your interest in resolving it.
One of the Developers will reply back to you in the issue, informing you
of all the necessary details. Feel free to ask any specific doubts you might have
in the issue.

If no issue is present on GitLab for your idea, then we recommend you to create
an issue for the same and then mention that you would like to work on resolving
it. This is to ensure that no one else works on the same issue, leading to
unnecessary conflicts. A less favored approach would be to directly create an MR
with your code changes. This is fine only if your code changes are very minor (for eg.,
fixing a typo, changing couple of lines in a file, etc).

We recommend new contributors to go over issues with label "good first issue"
([link](https://gitlab.com/nitk-nest/nest/-/issues?label_name%5B%5D=good+first+issue)).
These are relatively easy issues that can help a new contributor to get started with
contributing to NeST.

To contribute to NeST,

* [Fork](https://docs.gitlab.com/ee/gitlab-basics/fork-project.html) the repository
* Create a new branch with an appropriate name for the branch
* Make sure the code follows the  [Styleguides](#styleguides)
* Run all the [tests](./README.md#unit-tests) and add unit tests if necessary
* Push the commits to the relevant branch
* Make a [merge request](https://gitlab.com/nitk-nest/nest/-/merge_requests/new)
* Ensure that the code passes the pipeline (See note below)

#### NOTE on Merge Request Pipelines

For new contributors, most likely the Pipelines won't get successfully triggered.
You will observe that the pipeline is "stuck" and it won't run any checks on your MR.

This is intentional. The pipelines run on private VMs owned by us, and we
want to ensure that no malicious code is run on the VM. Hence, after a
Developer reviews your MR and is confident that the changes are safe,
they will trigger the pipeline manually for the MR (on your behalf).

### MR conflicts resolution

There may be MR conflicts if the master gets updated before your MR
gets accepted. If this happens, then **rebase** your branch on top of the updated
master to get the latest changes. **Do not create a merge commit**.

An exception to the above *rule* is if you intend to squash your commits
when merging the MR.

### Pushing changes to a Merge Request

During the review of an MR by a developer, you may be required to make some changes
to it. Please ensure that you add the requested changes to the same MR and **do not**
create a new MR. The requested changes may or may not need a new commit. Incase the
requested changes don't require a separate commit, please make the changes to one of the
existing commits(using `git rebase`) and force push to the same MR.

## Styleguides

We highly recommend installing the following tools and setting up git
hooks as shown below (the below commands should be run inside NeST repo):

```sh
$ python3 -m pip install pre-commit gitlint
$ pre-commit install
$ gitlint install-hook
```

This will help in catching simple violations in code standards early and
lead to smoother code reviews. These violations (if any) will be shown
when you are making a git commit.

Note that after installing the above git hooks, the first git commit
will take some time to install all the required dependencies (for eg.,
pylint, black, etc).

Below, we specify in detail about certain standards we maintain in the repo:

### Code Style

To maintain uniformity across the codebase and avoid having arguments over
trivial formatting issues, we use the [black](https://github.com/psf/black)
formatter. In some rare occasions when we are not satisfied with black formatting
in some specific parts of code, we disable black for that specific part
using the ```# fmt: on\off``` (as mentioned in black's documentation) comment inline.

In addition, we use [pylint](https://www.pylint.org/) for
checking for some trivial syntax errors, common mistakes and compliance with
[PEP-8 coding style](https://www.python.org/dev/peps/pep-0008/) (with some exceptions).
The exceptions are commented inline in code as:

```python
# pylint: disable=missing-docstring
```

You may check [`.pylintrc`](.pylintrc) for inspecting pylint default configuration.

The code is expected to get 10/10 when running pylint as shown below:

```bash
pylint nest
```

The CI pipeline will fail if the code doesn't confirm to black formatting
or get a score of 10/10 in pylint.

**NOTE**: If you have installed the pre-commit hook, then there is no need to
run black and pylint separately. It will automatically be run just before you commit
your changes.

### Documentation Style

We follow the [NumPy Style](https://www.sphinx-doc.org/en/master/usage/extensions/example_numpy.html)
for Python docstring. When a new class/function is added in NeST, along with code, the
docstring is also added (complying the the NumPy style).

We use [Sphinx](https://www.sphinx-doc.org/en/master/) for auto-generating
documentation from docstrings in code. Refer [`docs`](./docs) folder for more details.

### Git Commit Messages

The commit messages typically follow the convention

```
<directory>: Commit message

Detailed description of the commit

Signed-off-by: name <email>
```

The "\<directory\>" indicates the location of major changes done in the commit.
The "Commit message" is written in present-tense, imperative-style
just as [git](https://git-scm.com/docs/SubmittingPatches#describe-changes) follows.
The commit title (1st line) is maintained to lesser than 50 characters
long and the commit body (rest of it) can be upto 72 characters long per line
with a newline between the commit title and body.
Often, this path is shortened for brevity. An example commit message for fixing
a typo in `nest/experiment/plotter/ss.py` would be:

```git
plotter: Fix typo in ss.py

<Description>

Signed-off-by: Random J Developer <random@developer.example.org>
```

The "Signed-off-by" line is added automatically by using the sign-off flag while committing:
`git commit --signoff` or `git commit -s`. Note that a real name is used in the above
Signed-off-by line. We request you to do the same.

**NOTE**: To setup your name and email in git, run:
```
$ git config --global user.name <your-name>
$ git config --global user.email <your-email>
```
The above given name and email will be used in the signoff line.
