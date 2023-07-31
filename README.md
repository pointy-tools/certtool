# CertTool

Cedar private PKI management tool

## Python package setup

In the root of the project, follow these steps:

Build and run the new image

```shell
dc build
dc run certtool bash
```

Within the container, initialize the `poetry.lock` file, export dependencies for both dev and prod images, and exit the container.

```shell
poetry lock
poetry export --dev -f requirements.txt --output dev-requirements.txt
poetry export -f requirements.txt --output requirements.txt
exit
```

Build the image again, which will install the dependencies listed in `dev-requirements.txt` for the dev image and `requirements.txt` for the prod image. Make sure to not export dev dependencies to the `requirements.txt`.
```shell
dc build
```

## DB setup

This project has its own DB. The init foo can be found 

- Confirm the DB environment variables in `certtool/certtool/settings/base.py`
- Run the Docker image `dc run certtool bash`
- From the shell, run `./manage.py migrate`

## Data Access Layer

Along with database set up, the project lays out the patterns that make up the new [Data Access Layer](https://docs.google.com/document/d/142exltFjqfUdsvEqcYOw87yMw6eyiBqcITvDHbyon9c/edit?usp=sharing). This layer, when adhered to, keeps business and persistence logic separate. Use [The DAL Standards](https://careportal.atlassian.net/wiki/spaces/EN/pages/5280530611/The+DAL+Standards) document to help ensure compliance. Decisions to break through the DAL should not be made lightly and need to come with strong, supported justifications documented with the code.

## Sentry setup

- See the `SENTRY_` environment variables in `certtool/certtool/settings/base.py` - these will be referenced in non-dev environments to send errors to Sentry. These variable values can be provided via secretsmanager. Services are encouraged to use an independent Sentry project for their errors. Please reach contact the Platform team if you need to add a new Sentry project.

## Adding or Updating a Python dependency

We use poetry to manage dependencies. We export production dependencies to requirements.txt and dev dependencies to dev-requirements.txt, both of which are used for pip installs. Be sure to add dependencies only used for dev as dev dependencies to keep production installs clean.

To update dependencies (dev or prod), first exec into the docker container:

`docker-compose exec -it certtool bash`

To add a new package for dev:

```shell
poetry add --dev --lock {library==version} 
poetry export --dev -f requirements.txt --output dev-requirements.txt
```

To add a new package for production:

```shell
poetry add --lock {library==version}
poetry export -f requirements.txt --output requirements.txt
```

To update a package, edit the version in `pyproject.toml` and then:

```shell
poetry update --lock {library}
```
Then run the appropriate export described above depending on if it's a dev or prod dependency.

## Django setup

The Django files in this project were initialized by running:

```shell
django-admin startproject CertTool .
python manage.py startapp your_cookie_cutter_api
```

Please rename `your_cookie_cutter_api` to you desired app name.

Your first endpoint:

- Test your endpoint by running `curl localhost:4443/status/` from the Terminal

## Type checks

We use mypy for type checking. When the service tests are run in CI, we run mypy on the whole directory. To run mypy locally, run the following from your service container:

```shell script
mypy . --config ./mypy.ini
```

## Nginx

We recommend deploying an Nginx sidecar alongside your service. Please consult the Platform team to see if you can use a pre-configured Nginx image.

## Test pipelines

To run tests in Jenkins, add a stage to `all_required_tests.jenkinsfile` and adapt as needed. Note: you need a GitHub admin to make these tests required!

A pre-generated `certtool/file_requirements.txt` can be used to identify whether files have changed in folders relevant to the application. This guards against changes to python_packages that may break the app. As you add/remove python_packages in the Dockerfile, be sure to update this script.

In `all_required_tests.jenkinsfile`, see `Interactor Service Tests` for an example of how to use `file_requirements.txt` with `.jenkins/bash/utils/should_run_tests.sh` to target tests.

See `Xifin Gateway Tests` for an example of how to use our generic service test script `.jenkins/bash/services/test.sh`.

## Build pipelines

To build and publish your service's Docker image to Elastic Container Registry (ECR), add your service to `.jenkins/build-image-services.jenkinsfile`. This is a generic Jenkins pipeline to build service images. Add your service to `ServiceMap` and to the `SERVICE` parameter choices list.

The ECR repository needs to be created by Platform before you can run this Jenkins pipeline for your service.

Note: The `build-image-services` Jenkins pipeline is run manually. If you need your service image built at a certain cadence, please consult the Platform team.

We also have the `build-images-dev` Jenkins pipeline that publishes a Docker image to ECR with cache layer metadata - this dev image can be used as a build cache so that build and test pipelines can build from cache instead of building from scratch. This pipeline is defined in `.jenkins/build-images-dev.jenkinsfile` and runs daily. This is an optional step for services to speed up their Docker builds.
