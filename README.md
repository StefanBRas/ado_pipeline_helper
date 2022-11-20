# ADO Pipeline helper 

Python package and commandline tool for helping with writing Azure Devops pipelines

# Features
None of these are implemented mind you as of now

- validate pipeline (load .azure-pipeline, resolve templates, send to run endpoint with yamlOverride and preview=True)
- validate library groups (see if value exists)
- MAYBE: validate schedule cron
- Warning about templating syntax errors (like missing $ before {{ }} )
