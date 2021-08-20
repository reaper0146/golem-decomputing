# Dockerfile used to build the VM image which will be downloaded by providers.
# The file must specify a workdir and at least one volume.
FROM python:3.8.7-slim
VOLUME /golem/input /golem/output
COPY worker.py /golem/entrypoint/
WORKDIR /golem/entrypoint

RUN pip3 install matplotlib
RUN pip3 install numpy
RUN pip3 install pandas
RUN pip3 install influxdb
RUN pip3 install sklearn
