FROM mcr.microsoft.com/devcontainers/python:3.10

WORKDIR /

ENV CONDA_PREFIX=/azureml-envs/ai-development-env
ENV CONDA_DEFAULT_ENV=$CONDA_PREFIX
ENV PATH=$CONDA_PREFIX/bin:$PATH
ENV LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH

# needed for build_mlindex
RUN apt update && apt install -y fuse

# Install Python SDK
COPY requirements.txt .
RUN pip install -r requirements.txt 

# Adding this install under root's path for the custom AI Studio container solution
ENV PATH="/home/vscode/.dotnet/tools:${PATH}"

# The instructions run after this for AI CLI are required to be run by the vscode user
WORKDIR /home/vscode
USER vscode

# Install Azure AI CLI (which installs `az` CLI and `ai` CLI + dependencies)
RUN curl -sL https://csspeechstorage.blob.core.windows.net/drop/private/ai/InstallAzureAICLIDeb-1.0.0-alpha1021.1.sh | bash

