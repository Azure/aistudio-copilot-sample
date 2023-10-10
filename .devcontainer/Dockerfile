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

RUN wget https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && \
   dpkg -i packages-microsoft-prod.deb && \
   apt update && apt install -y dotnet-sdk-7.0 nuget  # Change the version as needed

# Install azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Adding this install under root's path for the custom AI Studio container solution
ENV PATH="/home/vscode/.dotnet/tools:${PATH}"

# The instructions run after this for AI CLI are required to be run by the vscode user
WORKDIR /home/vscode
USER vscode

# Install Azure AI CLI
RUN wget https://csspeechstorage.blob.core.windows.net/drop/private/ai/Azure.AI.CLI.1.0.0-alpha1010.1.nupkg && \
   dotnet tool install --global --add-source . Azure.AI.CLI --version 1.0.0-alpha1010.1 && \
   rm Azure.AI.CLI.1.0.0-alpha1010.1.nupkg
