# Deployment Bug Bash 11/07/2023 Instructions

Welcome to the Deployment Bug Bash scheduled for 11/07/2023. Before you can start bashing, please make sure you follow these instructions to make sure you have the correct
local environment and AI Project.

## Setting Up Local Environment

In a new shell, run the following to create a virtual environment:

```
python -m venv deployment-bug-bash-env
```

To activate the enviornment on Windows, run:

```
./deployment-bug-bash-env/scripts/Activate
```

On Linux, run:

```
source ./deployment-bug-bash-env/scripts/Activate
```

After the environment is active, run:

```
pip install -r requirements.txt
```

Your local environment is now fully ready to use the deployment code!

## Creating an AI Project

An AI Resource has **already** been provisioned for your use, and connections to AOAI and AISearch have also been created. The AISearch resource already contains a vector index that
will be consumed by some of the deployment examples. Create a project that's connected to this resource by running:

```
python ./scripts/create_project.py --project-name <name of your project>
```

If you run into permission issues, ping in the chat and you will be given access to the test subscription.