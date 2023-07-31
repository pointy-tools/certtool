FROM public.ecr.aws/docker/library/python:3.11.1-slim-bullseye as base
LABEL maintainer="platform@cedar.com"

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
# Disable writing of bytecode (i.e., .pyc) files during build.
# These are generated on the fly the first time the code is imported, so no need to
# bake them into the image. Although we pass --no-compile to pip to prevent bytecode
# generation at install time, we also want to suppress bytecode generation that
# would happen when executing pip.
ARG PYTHONDONTWRITEBYTECODE=1
ENV AWS_DEFAULT_REGION=us-east-1
ENV PYTHONPATH "${PYTHONPATH}:/home/app/python_packages"

# hadolint ignore=DL3008,SC1083
RUN apt-get update && apt-get -y install --no-install-recommends \
    # needed for python and uwsgi
    gcc \
    g++ \
    # needed for postgres
    libpq-dev \
    # add for pg_isready, psql
    # postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /home/app/certtool \
    && mkdir -p /home/app/python_packages

WORKDIR /home/app/

###############
# certtool DEV IMAGE
###############
FROM base as certtool-dev

COPY services/platform/certtool/dev-requirements.txt .

RUN pip install --upgrade --no-cache-dir pip==22.1.2 \
    && pip install --no-cache-dir -r ./dev-requirements.txt

# Install curl and vim for local development
# hadolint ignore=DL3008,DL4006
RUN apt-get update  \
    && apt-get install -y --no-install-recommends curl vim \
    && curl -sSL https://install.python-poetry.org \
    | python3 - --version 1.1.14 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PATH "/root/.local/bin:${PATH}"

################
# certtool PROD IMAGE
################
FROM base as certtool-prod

ARG VERSION

# Hey! If you add a python_package here, remember to also add it
# to your file_requirements.txt file!
COPY python_packages/configurator python_packages/configurator

COPY services/platform/certtool .

RUN pip install --upgrade --no-cache-dir pip==22.1.2 \
    && pip install --no-cache-dir -r ./requirements.txt

RUN ./manage.py addconfig --all-environments --key VERSION --val "$VERSION"

CMD ["/usr/local/bin/uwsgi", "--ini", "/home/app/conf/uwsgi.ini"]

################
# certtool CLI PROD IMAGE
################
FROM certtool-prod as certtool-cli-prod

# hadolint ignore=DL3008
RUN apt-get update  \
    && apt-get install -y --no-install-recommends wget vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# TODO: install teleport
