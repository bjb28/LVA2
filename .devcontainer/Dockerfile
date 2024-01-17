#-----------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
#-----------------------------------------------------------------------------------------

FROM python:3

# Copy default endpoint specific user settings overrides into container to specify Python path
COPY .devcontainer/settings.vscode.json /root/.vscode-remote/data/Machine/settings.json

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED 1

RUN mkdir /workspace
WORKDIR /workspace

ENV SHELL /bin/bash

# Install git, process tools
RUN apt-get update && apt-get -y install git procps

# Install Python dependencies from requirements.txt if it exists
COPY ../requirements* /workspace/
RUN pip install -r requirements-dev.txt

# Clean up
RUN apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "../lva2.wsgi"]