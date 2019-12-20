FROM python:3.7-alpine3.10
# set virtual env in project directory
ENV PIPENV_VENV_IN_PROJECT true

# install necessary software
# install pipenv for virtual environments
RUN apk add --no-cache \
        --virtual .build_deps \
            gcc \
            linux-headers \
            python3-dev \
    && apk add --no-cache \
        postgresql-dev \
        musl-dev \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --upgrade pipenv \
    && adduser -u 1000 -s /bin/false -D faucet \
    && mkdir -p /data/tmp \
    && chown -R faucet:faucet /data/tmp \
    && ls -l /data

WORKDIR /data

COPY --chown=faucet:faucet ./faucet /data
RUN chown faucet:faucet /data
COPY mime.types /etc/

ENV FAUCET_PORT 8000
EXPOSE $FAUCET_PORT
# collectstatic requires SECRET_KEY
ARG SECRET_KEY
ENV SECRET_KEY=$SECRET_KEY

RUN pipenv --three \
    && pipenv update

RUN apk del .build_deps \
    && rm -rf /var/cache/apk/*


# switch user
USER faucet

RUN pipenv run sh -c "python manage.py collectstatic --noinput -i rest_framework -i admin"

CMD pipenv run sh -c "python manage.py migrate && ./start_uwsgi_server.sh"
