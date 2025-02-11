import json


def _remove_timings(response):
    for status in ('successes', 'failures'):
        assert status in response
        for key, value in response[status].items():
            assert 'timing' in value
            del value['timing']
    return response


def test_ok(app_connection):
    response = app_connection.get_json("c2c/health_check")
    print('response=' + json.dumps(response))
    assert _remove_timings(response) == {
        'successes': {
            'db_engine_sqlalchemy': {
                'level': 1
            },
            'db_engine_sqlalchemy_slave': {
                'level': 1
            },
            'http://localhost:8080/api/hello': {
                'level': 1
            },
            'fun_url': {
                'level': 1
            },
            'alembic_app_alembic.ini_alembic': {
                'result': '4a8c1bb4e775',
                'level': 1
            }
        },
        'failures': {},
    }


def test_filter(app_connection):
    response = app_connection.get_json("c2c/health_check", params={'checks': 'db_engine_sqlalchemy,fun_url'})
    print('response=' + json.dumps(response))
    assert _remove_timings(response) == {
        'successes': {
            'db_engine_sqlalchemy': {
                'level': 1
            },
            'fun_url': {
                'level': 1
            }
        },
        'failures': {},
    }


def test_empty_filter(app_connection):
    response = app_connection.get_json("c2c/health_check", params={'checks': ''})
    print('response=' + json.dumps(response))
    assert _remove_timings(response) == {
        'successes': {
            'db_engine_sqlalchemy': {
                'level': 1
            },
            'db_engine_sqlalchemy_slave': {
                'level': 1
            },
            'http://localhost:8080/api/hello': {
                'level': 1
            },
            'fun_url': {
                'level': 1
            },
            'alembic_app_alembic.ini_alembic': {
                'result': '4a8c1bb4e775',
                'level': 1
            }
        },
        'failures': {},
    }


def test_failure(app_connection):
    response = app_connection.get_json("c2c/health_check", params={'max_level': '2'}, expected_status=500)
    print('response=' + json.dumps(response))
    assert _remove_timings(response) == {
        'successes': {
            'db_engine_sqlalchemy': {
                'level': 1
            },
            'db_engine_sqlalchemy_slave': {
                'level': 1
            },
            'http://localhost:8080/api/hello': {
                'level': 1
            },
            'fun_url': {
                'level': 1
            },
            'alembic_app_alembic.ini_alembic': {
                'result': '4a8c1bb4e775',
                'level': 1
            },
            'redis://redis:6379': {
                'result': response['successes']['redis://redis:6379']['result'],
                'level': 2
            },
            'version': {
                'result': response['successes']['version']['result'],
                'level': 2
            }
        },
        'failures': {
            'fail': {
                'message': 'failing check',
                'level': 2
            },
            'fail_json': {
                'message': 'failing check',
                'result': {
                    'some': 'json'
                },
                'level': 2
            },
        }
    }


def test_failure_with_stack(app_connection):
    response = app_connection.get_json("c2c/health_check", params={'max_level': '2', 'secret': 'changeme'},
                                       expected_status=500)
    print('response=' + json.dumps(response))
    assert _remove_timings(response) == {
        'successes': {
            'db_engine_sqlalchemy': {
                'level': 1
            },
            'db_engine_sqlalchemy_slave': {
                'level': 1
            },
            'http://localhost:8080/api/hello': {
                'level': 1
            },
            'fun_url': {
                'level': 1
            },
            'alembic_app_alembic.ini_alembic': {
                'result': '4a8c1bb4e775',
                'level': 1
            },
            'redis://redis:6379': {
                'result': response['successes']['redis://redis:6379']['result'],
                'level': 2
            },
            'version': {
                'result': response['successes']['version']['result'],
                'level': 2
            }
        },
        'failures': {
            'fail': {
                'message': 'failing check',
                'stacktrace': response['failures']['fail']['stacktrace'],
                'level': 2
            },
            'fail_json': {
                'message': 'failing check',
                'result': {
                    'some': 'json'
                },
                'stacktrace': response['failures']['fail_json']['stacktrace'],
                'level': 2
            },
        }
    }


def test_ping(app_connection):
    response = app_connection.get_json("c2c/health_check", params={'max_level': '0'})
    print('response=' + json.dumps(response))
    assert response == {
        'successes': {},
        'failures': {}
    }
