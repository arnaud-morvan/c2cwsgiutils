from c2cwsgiutils.acceptance import retry


@retry(Exception)
def test_ok(app_connection):
    # reset the stats to be sure where we are at
    app_connection.get_json('c2c/stats.json?reset=1', cors=False)

    app_connection.get_json("hello")  # to be sure we have some stats

    stats = app_connection.get_json('c2c/stats.json', cors=False)
    print(stats)
    assert stats['timers']['render/GET/hello/200']['nb'] == 1
    assert stats['timers']['route/GET/hello/200']['nb'] == 1
    assert stats['timers']['sql/read_hello']['nb'] == 1
    assert stats['timers']['sql/SELECT FROM hello LIMIT ?']['nb'] == 1
    assert stats['gauges']['test/gauge_s/toto=tutu/value=24'] == 42
    assert stats['counters']['test/counter'] == 1


def test_server_timing(app_connection):
    r = app_connection.get_raw('hello')
    assert 'Server-Timing' in r.headers


def test_requests(app_connection):
    # reset the stats to be sure where we are at
    app_connection.get_json('c2c/stats.json?reset=1', cors=False)

    app_connection.get_json('tracking/1')

    stats = app_connection.get_json('c2c/stats.json', cors=False)
    print(stats)
    assert stats['timers']['requests/http/localhost/8080/GET/200']['nb'] == 1


def test_redis(app_connection):
    # reset the stats to be sure where we are at
    app_connection.get_json('c2c/stats.json?reset=1', cors=False)

    # that sends a few PUBLISH to redis
    app_connection.get_json('c2c/debug/stacks', params={'secret': 'changeme'})

    stats = app_connection.get_json('c2c/stats.json', cors=False)
    print(stats)
    assert stats['timers']['redis/PUBLISH/success']['nb'] >= 1
