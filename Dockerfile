FROM ubuntu:20.04

ENV SET_CONTAINER_TIMEZONE true
ENV CONTAINER_TIMEZONE UTC

RUN echo "deb http://ap-south-1.ec2.archive.ubuntu.com/ubuntu/ xenial main restricted" >> /etc/apt/sources.list
RUN echo "deb-src http://ap-south-1.ec2.archive.ubuntu.com/ubuntu/ xenial main restricted" >> /etc/apt/sources.list
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt-get update && apt-get install wget python3 supervisor libpq-dev -y
RUN apt-get update && apt-get -y install vim \
    python3-setuptools  \
     python3-dev python3-pip curl figlet rsync iptables \
    git net-tools sudo ipython3

RUN apt install -y python3-pip && \
    pip3 install --upgrade pip

RUN mkdir -p /usr/ecom-v1
COPY api_service /usr/ecom-v1/api_service
COPY scripts /usr/ecom-v1/scripts

RUN cd /usr/ecom-v1/scripts && \
    pip3 install -r requirements.txt 

ADD scripts/supervisord.conf /etc/supervisor/
ADD scripts/ecom.conf /etc/supervisor/conf.d/

# Postgres installation
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y wget gnupg \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && echo 'deb http://apt.postgresql.org/pub/repos/apt/ focal-pgdg main' >> /etc/apt/sources.list

ENV PG_VERSION=12

RUN apt-get update \
     && DEBIAN_FRONTEND=noninteractive apt-get install -y \
     postgresql-${PG_VERSION} postgresql-client-${PG_VERSION} postgresql-contrib-${PG_VERSION}

ENTRYPOINT ["bash","/usr/ecom-v1/scripts/init.sh"]