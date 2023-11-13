# ADO Pipeline helper 

**ARCHIVED**: I fortunantly do not have to work with Azure Devops Pipelines anymore (hopefully ever), so I won't do any work on this. Putting it out there for inspiration for others.


Python package and command line tool for helping with writing Azure Devops pipelines.

Primary functionality right now is that you can preview local changes to pipelines without pushing them.

## Installation

It a standard python package and can be installed as such. 
Since the required Python version is pretty new (3.10) I would however advice to install with `pipx`.

```bash
pipx install ado-pipeline-helper
```

**Requirements**:

- Python3.10

## Usage

```bash
ado-pipeline-helper validate azure-pipeline.yml
```

## Limitations

- Can't resolve `{{ }}` expressions, only simple `{{ parameter.<key>}}` ones.
I started working on a custom resolver but it was a lot of work. You can see it on the branch `expression resolver` under
`ado_pipeline_helper/src/ado_pipeline_helper/resolver/expression.py`.
Please create an issue if this is something you really need and especially if you would like to contribute.

## Project vision and design

The main goal is to make it easier to work with azure pipeline defined in yaml.
The current implementation tries to solve this by providing a CLI tool.

Since it is designed primarily as a CLI tool that is installed into a separate environment with something like [`pipx`](https://pypa.github.io/pipx/),
I am not that strict with adding dependencies even if they are maybe not strictly necessary.
This project is a learning experience for me and a way to try out new things (like the `match` statement which is the 
primary reason for the Python 3.10 requirement).

It does not have that many features in the current state, but the idea is to grow it into a collection of many different
functionalities. In time this might be structured into a main app with plugins but for now it will one big package.

## Roadmap

Not ordered, no guarantees that any of this is feasible or will ever be implemented.

- [x] validate local pipelines.
- [ ] Warnings about templating syntax errors (like missing $ before {{ }} )
- [ ] resolve arbitrary expression.
- [ ] validate library groups - Check if a referenced value is defined.
- [ ] validate schedule cron - Check if a schedule cron is valid and/or makes sense.
**Far future**:
- [ ] LSP - Get error messages directly in editor


## Useful links

- [ADO Yaml Reference](https://learn.microsoft.com/en-us/azure/devops/pipelines/yaml-schema/?view=azure-pipelines)

