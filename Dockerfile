FROM ubuntu:18.04
LABEL maintainer "info@camptocamp.org"

COPY requirements.txt docker-requirements.txt fake_python3 /opt/c2cwsgiutils/
RUN apt update && \
    DEV_PACKAGES="libpq-dev build-essential python3.7-dev equivs" && \
    DEBIAN_FRONTEND=noninteractive apt install --yes --no-install-recommends \
        libpq5 \
        python3.7 \
        curl \
        gnupg \
        $DEV_PACKAGES && \
    equivs-build /opt/c2cwsgiutils/fake_python3 && \
    dpkg -i python3_3.7.1-1~18.04_amd64.deb && \
    rm python3_3.7.1-1~18.04_amd64.deb && \
    ln -s pip3 /usr/bin/pip && \
    ln -s python3.7 /usr/bin/python && \
    ln -sf python3.7 /usr/bin/python3 && \
    DEBIAN_FRONTEND=noninteractive apt install --yes --no-install-recommends \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        python3-pkgconfig && \
    apt-get clean && \
    rm -r /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r /opt/c2cwsgiutils/requirements.txt -r /opt/c2cwsgiutils/docker-requirements.txt && \
    apt remove --purge --autoremove --yes $DEV_PACKAGES binutils

COPY . /opt/c2cwsgiutils/
RUN flake8 /opt/c2cwsgiutils && \
    echo "from pickle import *" > /usr/lib/python3.7/cPickle.py && \
    pip3 install --disable-pip-version-check --no-cache-dir -e /opt/c2cwsgiutils && \
    (cd /opt/c2cwsgiutils/ && pytest -vv --cov=c2cwsgiutils --color=yes tests && rm -r tests) && \
    python3 -m compileall -q && \
    python3 -m compileall -q /opt/c2cwsgiutils && \
    rm /opt/c2cwsgiutils/fake_python3

ENV TERM=linux \
    LANG=C.UTF-8 \
    LOG_TYPE=console \
    LOG_HOST=localhost \
    LOG_PORT=514 \
    SQL_LOG_LEVEL=WARN \
    GUNICORN_LOG_LEVEL=WARN \
    OTHER_LOG_LEVEL=WARN \
    DEVELOPMENT=0 \
    PKG_CONFIG_ALLOW_SYSTEM_LIBS=OHYESPLEASE

CMD ["c2cwsgiutils_run"]
