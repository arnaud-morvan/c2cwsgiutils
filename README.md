Camptocamp WSGI utilities
=========================

This is a python library providing common tools for Camptocamp WSGI
applications:

* Provide a small framework for gathering performance statistics about
  a web application (statsd protocol)
* Allow to use a master/slave PostgresQL configuration
* Logging handler for CEE/UDP logs
* Error handlers to send JSON messages to the client in case of error
* A cornice service drop in replacement for setting up CORS

Also provide tools for writing acceptance tests:

* A class that can be used from a py.test fixture to control a
  composition
* A class that can be used from a py.text fixture to test a REST API

As an example on how to use it in an application, you can look at the
test application in [acceptance_tests/app](acceptance_tests/app).
To see how to test such an application, look at
[acceptance_tests/tests](acceptance_tests/tests).


Build
-----

You will need `docker` (>=1.12.0), `docker-compose` (>=1.10.0) and
`make` installed on the machine to play with this project.
Check available versions of `docker-engine` with
`apt-get policy docker-engine` and eventually force install the
up-to-date version using a command similar to
`apt-get install docker-engine=1.12.3-0~xenial`.

To lint and test everything, run the following command:

```shell
make
```
