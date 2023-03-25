# ADO Pipeline helper 

Python package and commandline tool for helping with writing Azure Devops pipelines.

# Features
None of these are implemented mind you as of now

- validate pipeline (load .azure-pipeline, resolve templates, send to run endpoint with yamlOverride and preview=True)
- validate library groups (see if value exists)
- MAYBE: validate schedule cron
- Warning about templating syntax errors (like missing $ before {{ }} )

## Limitations

- Can't resolve `{{ }}` expressions, only simple `{{ parameter.<key>}}` ones.
I started working on a custom resovler but it was a lot of work. You can see it on the branch `expression resolver` under
`ado_pipeline_helper/src/ado_pipeline_helper/resolver/expression.py`

## Useful links

- [ADO Yaml Reference](https://learn.microsoft.com/en-us/azure/devops/pipelines/yaml-schema/?view=azure-pipelines)

