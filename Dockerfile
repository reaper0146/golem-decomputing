# Dockerfile used to build the VM image which will be downloaded by providers.
# The file must specify a workdir and at least one volume.
FROM python:3.8.7-slim

RUN pip install --upgrade pip
RUN pip instal --upgrade pip wheel
RUN pip install matplotlib
RUN pip install numpy
RUN pip install pandas
RUN pip install influxdb
RUN pip install sklearn

VOLUME /golem/input /golem/output
COPY worker.py /golem/entrypoint/
WORKDIR /golem/entrypoint

