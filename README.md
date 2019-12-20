# Monero faucet
The monero faucet can be used as `stagenet` faucet or as `testnet` faucet.
A faucet in general accepts a monero wallet address and returns a fraction of its own wallet's balance to the given wallet.

Running faucets based on this project can be found at
* [stagenet](https://community.xmr.to/faucet/stagenet)
* [testnet](https://community.xmr.to/faucet/testnet)

Visit us at https://community.xmr.to.

## Getting Started

These instructions will get you a copy of the faucet up and running on your local machine for development and testing purposes.

See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Before you even start to use docker-compose to run a faucet locally, you should make a copy of `docker-compose-template.yml`.

```bash
cp docker-compose-template.yml docker-compose.yml
```

In `docker-compose.yml` you will find some settings, you should be familiar with (**default** settings refer to `docker-compose.yml`, not `settings.py`):
* faucet specific
  - `FACTOR_BALANCE` (**default**: `10`)
    + The factor by which the wallet's balance is divided. Determines the amount to pay to the given address.
  - `WALLET_HOST` (**default**: `localhost`)
    + IP or URL to the `monero -wallet-rpc` (see `monero-rpc` service)
  - `WALLET_PORT` (**default**: `38083`)
    + RPC port of the `monero -wallet-rpc` (see `monero-rpc` service)
  - `DAEMON_HOST` (**default**: `node.xmr.to`)
    + IP or URL to `monerod`
  - `DAEMON_PORT` (**default**: `38081`)
    + RPC port of `monerod`
  - `DEFAULT_MIXIN` (**default**: `10`)
    + mixin to be used when making transactions (`ring size = mixin + 1`)
  - `FAUCET_PORT` (**default**: `8000`)
    + Published port of the faucet
    + If changed, also modify
      - exposed port in `docker-compose.yml`
      - `command` in `docker-compose.yml` to `runserver 0.0.0.0:<your_port>`
* service/project specific
  - `RATELIMIT_ENABLE` (**default**: `True`)
    + switches on/off rate limitation on the `transactions/` endpoint.
    + not working locally, since `django-ratelimit` is configured to read `header:x-real-ip` instead of `ip`.
      - if set to `ip`, `django-ratelimit` tries to read  `remote_addr`.
      - A [Middleware](https://django-ratelimit.readthedocs.io/en/v1.1.0/security.html) could be added to modify `remote_addr` and always use `ip` in the `django-ratelimit` configuration.
    + Makes use of [`django-ratelimit`](https://github.com/jsocol/django-ratelimit).
  - `ONCE_EVERY_N_MINUTE` (**default**: `5`)
    + configures the faucet's rate limitation on API endpoint `transactions/` to **once per `n` minutes** where `n=ONCE_EVERY_N_MINUTE`.
  - `MAXIMUM_PAYOUT` (**default**: `1`)
    + sets the maximum XMR to pay to the user to `1 XMR`
    + This was implemented due to the fact, that someone was draining the faucet with a script.
  - `DEBUG` (**default**: `True`)
    + Should be set to `False` in production
  - `SECRET_KEY` (**default**: `<some_secret_key>`)
    + This value should be changed to something sensible in production.
  - `MONERO_ENDPOINT` (**default**: `/`)
    + Is only changed when several faucets are served by one single proxy server (like nginx).
    + See deployment for further information.
  - `CACHE_URL` (**default**: `locmemcache://`)
    + URL to cache
      - `locmemcache://` uses the local Django cache
      - See 'Starting the faucet' for use with redis.
    + Makes use of [`django-environ`](https://github.com/joke2k/django-environ).
  - `DATABASE_URL` (**default**: `sqlite://`)
    + URL to database
      - `sqlite://` creates an in-memory sqlite database
      - `sqlite:////data/db.develop` creates a sqlite database file called `db.devlop`
      - See 'Starting the faucet' for use with postgres.
    + Makes use of [`django-environ`](https://github.com/joke2k/django-environ).

#### `monero-rpc` service
A `monero-wallet-rpc` docker image is hosted [here](https://hub.docker.com/r/xmrto/monero/). The source can be found [here](https://github.com/XMRto/monero).

The service `monero-rpc` does not publish its port (not listening on host's localhost). The port is just exposed, which makes it available in the `faucet` service, since they are hosted within the same `docker`/`docker-compose` network.

Modify `monero-rpc` service in `docker-compose.yml`.

* `USER_ID` (**default**: `1000`)
  - Can be set to whatever `uid` the wallet folder is owned by.
    + Within the docker container a user (with the given `uid=USER_ID`) is created.
  - Obviousy only works, if `uid` is available.
* `LOG_LEVEL`
  - verbosity level of `monero-wallet-rpc` log messages
* **stagenet**
  - `--stagenet`
  - `--wallet-file <stagenet_wallet>`
  - `--password-file <stagenet_wallet_password_file>`
  - Adapt the path to your monero **stagenet** wallet `<stagenet_wallet>`.
  - `DAEMON_PORT=38081` (or whatever port your daemon is listening to)
  - `wallet_port=38083` (or whatever port yout RPC should be listening on)
* **testnet**
  - `--testnet`
  - `--wallet-file <testnet_wallet>`
  - `--password-file <testnet_wallet_password_file>`
  - Adapt the path to your monero **testnet** wallet `<testnet_wallet>`.
  - `DAEMON_PORT=28081` (or whatever port your daemon is listening to)
  - `wallet_port=28083` (or whatever port yout RPC should be listening on)

#### Necessary tools
The faucet project makes use of `docker` and `docker-compose`.

The following tools should be installed to make it work locally:
* `docker`
  - [Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/)
  - [Mac](https://docs.docker.com/docker-for-mac/install/)
* [`docker-compose`](https://docs.docker.com/compose/install/#install-compose)

### Starting the faucet

The faucet can be started like this
```bash
docker-compose up -d --build
```

The above command starts the `faucet` service as well as a `monero-wallet-rpc` server (as defined within `docker-compose.yml`).

It also makes sure, the service's image is built from scratch (`--build`) and the services (docker containers) are started in the background (`-d`, daemonized).

The local development environment's (`Dockerfile`) docker base image (`faucet` service) is based on `python:3.6` (`docker-compose-template.yml`).
For production (`prod.Dockerfile`) docker base image(`faucet` service) should be based on `python:3.6-alpine` (`docker-compose-prod.yml`). Please see deployment for more information.

Have a look at the logs:
* `docker-compose log -f`
* `docker-compose log -f faucet` (only `faucet` service)

Stop services:
* `docker-compose rm -s -f`
* `docker-compose rm -s -f faucet` (only `faucet` service)

#### Switching databases
The default database (`docker-compose-template.yml`) is `sqlite`.

Using the setting `DATABASE_URL` the database can be easily changed.
* `DATABASE_URL=postgresql://postgres:postgres@postgres:5432/transactions`
* `DATABASE_URL=sqlite:////data/db.develop`

* `sqlite`
  - uncomment `sqlite` in `depends_on` (in `docker-compose.yml`)
  - uncomment `sqlite` `DATABASE_URL`
  - comment `postgres` `DATABASE_URL`
  - comment `postgres` in `depends_on` (in `docker-compose.yml`)
  - comment the `postgres` service (in `docker-compose.yml`)
  - comment the `volumes` (in `docker-compose.yml`)
* `postgres`
  - comment `sqlite` in `depends_on` (in `docker-compose.yml`)
  - comment `sqlite` `DATABASE_URL`
  - uncomment `postgres` `DATABASE_URL`
  - uncomment `postgres` in `depends_on` (in `docker-compose.yml`)
  - uncomment the `postgres` service (in `docker-compose.yml`)
  - uncomment the `volumes` (in `docker-compose.yml`)

#### Switching caches
In the same manner the cache can be configured.
* `CACHE_URL=rediscache://redis:6379/1?CLIENT_CLASS=django_redis.client.DefaultClient`

## Accessing the faucet

With its default configuration the faucet listens on port `8000`.



## Running the tests

Tests can be run using the script
```
start_local_tests.sh
```

This script spins up a docker container and runs the tests within this specific environment.
Have a look at `docker-compose-testing.yml` for further details.

Of course, it is also possible to run the `faucet` service and enter the container using `docker-compose exec faucet bash`.
Then you should be able to activate and enter the virtual environment with `pipenv shell`.
From here on, it is possible to run Django commands like `python manage.py ...`.

### And coding style tests

The source code is formatted using `black --line-length 79`.

## Deployment

For the deployment we recommend using `alpine` as docker base image.
`prod.Dockerfile` makes use of this - Locally such an environment can be started with `docker-compose-prod.yml` as docker-compose configuration file.

```bash
docker-compose -f docker-compose-prod.yml up -d --build
```

### Serve using uWSGI
In this case `DEBUG` should be set to `False`'

Another `command` line within `docker-compose.yml` can be used to let the faucet be served by `uWSGI`.
In this case, comment the `command` containing `runserver 0.0.0.0...`.

The `uWSGI` server listens on port `FAUCET_PORT`.

`STATIC_ROOT = "/data/static/"` and `uWSGI` is configured to serve statc content like this `--static-map /static/=/data/static/`.


### Running serveral faucets behind a proxy server
There might be the need to run `stagenet` and `testnet` faucets behind the same nginx proxy.

In this case it is recommended to let the faucet be served by `uWSGI`.

This requires to differentiate
* API calls
* static content requests
between the two faucets.

Therefore `MONERO_ENDPOINT` was introduced. This setting defines a URL prefix, that is used when the client talks to the backend.

`MONERO_ENDPOINT` modifies the following settings:
* URL to static content in `index.html`
* URL to `transactions/` API endpoint in `index.html`
by modifiying `STATIC_URL` in `settings.py`.

`MONERO_ENDPOINT` should be the same as the appropriate location block in the nginx configuration.
Within the nginx location block the prefixed URL should be stripped of `MONERO_ENDPOINT` again, since `uWSGI` is configured to just serve static contents

#### Example
* With `MONERO_ENDPOINT=/` `STATIC_URL` becomes `/static/`
  - `index.html`
    + `/transactions/`
    + `/static/fonts/fonts.css`
* With `MONERO_ENDPOINT=/faucet/stagenet/` `STATIC_URL` becomes `/faucet/stagenet/static/`
  - `index.html`
    + `/faucet/stagenet/transactions/`
    + `/faucet/stagenet/static/fonts/fonts.css`
    + `...`
* With `MONERO_ENDPOINT=/faucet/testnet/` `STATIC_URL` becomes `/faucet/testnet/static/`
  - `index.html`
    + `/faucet/testnet/transactions/`
    + `/faucet/testnet/static/fonts/fonts.css`
    + `...`

nginx could be configured like this:
```nginx.conf

set $upstream_faucet_testnet some_ip_url_dns_to_the_testnet_faucet:8000;

location ~ ^/faucet/testnet/ {
    if ($request_method !~ ^(GET|POST|HEAD|OPTIONS)$) {
        return 405;
    }

    # forwarding
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $http_x_real_ip;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_cache_bypass $http_upgrade;

    # use the complete $request_uri for rewriting
    rewrite ^ $request_uri;
    # remove /faucet/testnet/
    # take the remaining content and put it into $uri
    rewrite ^/faucet/testnet/(.*) /$1 break;  # add / before $1 to avoid zero length $uri
    return 400; #if the second rewrite does not match

    proxy_pass http://$upstream_faucet_testnet$uri;
}
```

Eventually, this setup requests the backend with `/transactions/` instead of `/faucet/testnet/transactions/`, which is the configured URL.
Also static content will be requested from `/static/fonts/fonts.css` instead of `/faucet/testnet/fonts/fonts.css`, like the `uWSGI` configuration defines.

## Built With

The services are run within docker containers.

The `faucet` service is backed by `python3.6`.

The virtual environment for python is created and maintained with `pipenv`.
Specific versions are defined within `Pipfile`.
* [`django-environ`](https://github.com/joke2k/django-environ) is used to to extract database URLs as well as cache URLs.
* [`django-ratelimit`](https://github.com/jsocol/django-ratelimit) is used to rate throttle API endpoints.
* [`djangorestframework`](https://www.django-rest-framework.org/) is used to create a REST API.

<!-- ## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us. -->

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/xmrto/faucet/tags).

## Authors

* **Norman Moeschter-Schenck** - *Initial work* - [normoes](https://github.com/normoes)

See also the list of [contributors](contributors.md) who participated in this project.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* [Monero project](https://github.com/monero-project/monero)
* [XMR.to](https://xmr.to)


## Troubleshooting

`makemigrations` could, in some cases, be interactive (e.g. renaming a model field).
Then, the `faucet` container will not start successfully.
* Leave the `faucet` service in its unsuccessful state
```bash
    # enter the running faucet service container
    docker-compose exec faucet bash
    # enter the virtual environment
    pipenv shell
    # run makemigrations manually
    python manage.py makemigrations  # interactive
```
