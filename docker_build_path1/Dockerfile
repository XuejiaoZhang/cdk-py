FROM 320185343352.dkr.ecr.us-west-2.amazonaws.com/ubuntu:18.04
WORKDIR /home/mts
ENV DEBIAN_FRONTEND noninteractive
ENV DISPLAY=:0
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        apt-transport-https


RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates

    
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        cabextract

    
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gosu

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gpg-agent
