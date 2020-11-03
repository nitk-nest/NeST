# Contributing to NeST
`NeST` is a python3 package that handles testbed setup, testbed configuration,
collecting and visualizing data by providing a user friendly API, addressing
common issues involved in conducting networking experiments.
#### Table Of Contents
[What should I know before I get started?](#what-should-i-know-before-i-get-started)
[How Can I Contribute?](#how-can-i-contribute)
  * [Reporting Bugs](#reporting-bugs)
  * [Suggesting Enhancements](#suggesting-enhancements)
  * [Code Contribution](#code-contribution)

[Styleguides](#styleguides)
  * [Git Commit Messages](#git-commit-messages)
  * [Documentation Styleguide](#documentation-styleguide)
  * [Code Style](#code-style)


## What should I know before I get started?

`NeST` has it's own architecture. The architecture is given below.
(Add image here)
Each module provides a specific service. Engine provides a set of low level APIs for other modules. Topology module creates the topology by using virtual nodes and interfaces. Experiment module provides APIs to generate traffic and extract the statistics from nodes and interfaces.


## How Can I Contribute?

### Reporting Bugs

To report a bug in NeST, do the following

* Check if the bug is already an issue [here](https://gitlab.com/nitk-nest/nest/-/issues?scope=all&utf8=%E2%9C%93&state=opened&label_name[]=bug)
* Create a new issue [here](https://gitlab.com/nitk-nest/nest/-/issues/new?issue%5Bassignee_id%5D=&issue%5Bmilestone_id%5D=)
* Add the label 'bug'

### Suggesting Enhancements
To suggest an enhancement, you can do the following

* Check if the enhancement is already suggested [here](https://gitlab.com/nitk-nest/nest/-/issues?scope=all&utf8=%E2%9C%93&state=opened&label_name[]=enhancement)
* Create a new issue [here](https://gitlab.com/nitk-nest/nest/-/issues/new?issue%5Bassignee_id%5D=&issue%5Bmilestone_id%5D=)
* Add the label 'enhancement'

### Code Contribution
To contribute to NeST,

* Fork the repository
* Create a new branch with an appropriate name for the branch
* Make sure the code follows the  [Styleguides](#styleguides)
* Run all the unittests and add unittest if necessary
* Push the code to the relevant branch
* Make a merge request (add link)

## How Can I Contribute?

### Git Commit Messages
The commit messages usually follow the convention
`\<module-name> : Commit message`
`Deailed description of the commit`

### Documentation Styleguide
We follow the [Sphinx documentation](https://www.sphinx-doc.org/en/master/) style

### Code Style
We follow the [PEP-8 coding sytle](https://www.python.org/dev/peps/pep-0008/) and the code written must get a 10/10 on pylint. This can be verified by running
`pylint nest`
from the root folder of the repository. If the code fails to adhere to the PEP-8 coding style, then the pipeline fails and the code will not be accepted