# Contributing to NeST
#### Table Of Contents
[How Can I Contribute?](#how-can-i-contribute)
  * [Reporting Bugs](#reporting-bugs)
  * [Suggesting Enhancements](#suggesting-enhancements)
  * [Code Contribution](#code-contribution)

[Styleguides](#styleguides)
  * [Git Commit Messages](#git-commit-messages)
  * [Documentation Styleguide](#documentation-styleguide)
  * [Code Style](#code-style)

## How Can I Contribute?

Refer [this](https://blog.apnic.net/2020/09/18/nest-a-simpleefficient-tool-to-study-congestion-control/) blog to get a brief overview of NeST.
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
* Run all the [tests](./README.md#unit-tests) and add unit test if necessary
* Push the code to the relevant branch
* Ensure that the code passes the pipeline
* Make a [merge request](https://gitlab.com/nitk-nest/nest/-/merge_requests/new)

## Styleguides

### Git Commit Messages
The commit messages usually follow the convention
`<module-name> : Commit message`
`Detailed description of the commit`

### Documentation Styleguide
We follow the [Sphinx documentation](https://www.sphinx-doc.org/en/master/) style and refer [docs/README.md](./docs/README.md) to generate documentation.

### Code Style
We follow the [PEP-8 coding sytle](https://www.python.org/dev/peps/pep-0008/) (with some exceptions) and the code written must get a 10/10 on pylint. This can be verified by running
`pylint nest`
from the root folder of the repository. If the code fails to adhere to the PEP-8 coding style, then the pipeline fails and the code will not be accepted