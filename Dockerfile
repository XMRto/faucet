FROM python:3.7-alpine3.10

# se a shell for 'pipenv shell'
ENV SHELL /bin/bash
# set virtual env in project directory
ENV PIPENV_VENV_IN_PROJECT true

WORKDIR /data
VOLUME ["/data"]

# install necessary software
# install pipenv for virtual environments
RUN apk add --no-cache \
        --virtual .build_deps \
            gcc \
            linux-headers \
            python3-dev \
    && apk add --no-cache \
        vim \
        bash \
        # python3-pip \
        python3-dev \
        postgresql-dev \
        musl-dev \
    && rm -rf /var/cache/apk/* \
    && pip install --upgrade pip \
    && pip install --upgrade pipenv \
    && adduser -u 1000 -s /bin/false -D faucet
    # && useradd -u 1000 -U -ms /bin/bash -p '*' -d /data faucet

# switch user
USER faucet

ENV FAUCET_PORT 8000
EXPOSE 8000

CMD []
