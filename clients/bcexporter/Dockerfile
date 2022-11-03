# syntax=docker/dockerfile:1

# set first stage base image (host OS)
FROM python:3.10.7 as builder

# copy the dependencies file to the builder container
COPY requirements.txt .

# Update pip
RUN python3 -m pip install --upgrade pip

# install depdencies to the local user directory
RUN pip3 install --no-cache --user -r requirements.txt

# set second stage final image
FROM python:3.10.7-slim as prod

# update binaries
RUN apt-get update

# copy only dependencies installed from builder image
COPY --from=builder /root/.local /root/.local

# copy contents of local src directory to the production src directory
COPY . /usr/app/bc_node_exporter

# set working directory
WORKDIR /usr/app/bc_node_exporter

# update PATH environment variable
ENV PATH=/root/.local:$PATH

# command to run on container start
ENTRYPOINT ["python3", "main.py"]

# docker build --tag nodies/blockchain_exporter:latest .