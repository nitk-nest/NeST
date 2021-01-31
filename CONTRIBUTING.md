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

To suggest an enhancement, you can do the following

* Check if the enhancement is already suggested
[here](https://gitlab.com/nitk-nest/nest/-/issues?scope=all&utf8=%E2%9C%93&state=opened&label_name[]=enhancement)
* Create a new issue [here](https://gitlab.com/nitk-nest/nest/-/issues/new?issue%5Bassignee_id%5D=&issue%5Bmilestone_id%5D=)
* Add the label 'enhancement'

### Code Contribution
To contribute to NeST,

* [Fork](https://docs.gitlab.com/ee/gitlab-basics/fork-project.html) the repository
* Create a new branch with an appropriate name for the branch
* Make sure the code follows the  [Styleguides](#styleguides)
* Run all the [tests](./README.md#unit-tests) and add unit tests if necessary
* Push the commits to the relevant branch
* Ensure that the code passes the pipeline
* Make a [merge request](https://gitlab.com/nitk-nest/nest/-/merge_requests/new)

#### NOTE on Merge Request Pipelines

For new contributors, most likely the Pipelines won't get succesfully triggered.
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

## Styleguides

### Git Commit Messages
The commit messages usually follow the convention

```
<directory>: Commit message
Detailed description of the commit

Signed-off-by: name <email>
```

The "\<directory\>" indicates the location of major changes done in the commit.
Often, this path is shortened for brewity. An example commit message for fixing
a typo in `nest/experiment/plotter/ss.py` would be:

```git
plotter: Fix typo in ss.py

<Description>

Signed-off-by: name <email>
```

The "Signed-off-by" is added by `git commit --signoff` or `git commit -s`.

### Documentation Style

We follow the [NumPy Style](https://www.sphinx-doc.org/en/master/usage/extensions/example_numpy.html)
for Python docstring.

We use [Sphinx](https://www.sphinx-doc.org/en/master/) for auto-generating
documentation from docstrings in code. Refer [`docs`](./docs) folder for more details.

### Code Style

We follow the [PEP-8 coding sytle](https://www.python.org/dev/peps/pep-0008/)
(with some exceptions). The exceptions are commented inline in code as:

```python
#pylint: disable=missing-docstring
```

You may check [`.pylintrc`](.pylintrc) for inspecting pylint default configuration.

The code is expected to get 10/10 when running pylint as shown below:

```bash
pylint nest
```

The pipeline will fail if the code doesn't get a score of 10/10 in pylint.