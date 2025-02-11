import logging
from typing import Mapping, Any, Generator, Tuple

import pyramid.request

from c2cwsgiutils import _utils, auth, broadcast

LOG = logging.getLogger(__name__)
CONFIG_KEY = 'c2c.log_view_enabled'
ENV_KEY = 'C2C_LOG_VIEW_ENABLED'
REDIS_PREFIX = 'c2c_logging_level_'


def install_subscriber(config: pyramid.config.Configurator) -> None:
    """
    Install the view to configure the loggers, if configured to do so.
    """
    if auth.is_enabled(config, ENV_KEY, CONFIG_KEY):
        config.add_route("c2c_logging_level", _utils.get_base_path(config) + r"/logging/level",
                         request_method="GET")
        config.add_view(_logging_change_level, route_name="c2c_logging_level", renderer="fast_json",
                        http_cache=0)
        _restore_overrides(config)
        LOG.info("Enabled the /logging/level API")


def _logging_change_level(request: pyramid.request.Request) -> Mapping[str, Any]:
    auth.auth_view(request)
    name = request.params.get('name')
    if name is not None:
        level = request.params.get('level')
        logger = logging.getLogger(name)
        if level is not None:
            LOG.critical("Logging of %s changed from %s to %s",
                         name, logging.getLevelName(logger.level), level)
            _set_level(name=name, level=level)
            _store_override(request.registry.settings, name, level)
        return {'status': 200, 'name': name, 'level': logging.getLevelName(logger.level),
                'effective_level': logging.getLevelName(logger.getEffectiveLevel())}
    else:
        return {'status': 200, 'overrides': dict(_list_overrides(request.registry.settings))}


@broadcast.decorator(expect_answers=True)
def _set_level(name: str, level: str) -> bool:
    logging.getLogger(name).setLevel(level)
    return True


def _restore_overrides(config: pyramid.config.Configurator) -> None:
    try:
        for name, level in _list_overrides(config.get_settings()):
            LOG.debug("Restoring logging level override for %s: %s", name, level)
            logging.getLogger(name).setLevel(level)
    except ImportError:
        pass  # don't have redis
    except Exception:
        # survive an error there. Logging levels is not business critical...
        LOG.warning("Cannot restore logging levels", exc_info=True)


def _store_override(settings: Mapping[str, Any], name: str, level: str) -> None:
    try:
        import redis
        redis_url = _utils.env_or_settings(settings, broadcast.REDIS_ENV_KEY, broadcast.REDIS_CONFIG_KEY)
        if redis_url:
            con = redis.StrictRedis.from_url(redis_url, socket_timeout=3, decode_responses=True)
            con.set(REDIS_PREFIX + name, level)
    except ImportError:
        pass


def _list_overrides(settings: Mapping[str, Any]) -> Generator[Tuple[str, str], None, None]:
    import redis
    redis_url = _utils.env_or_settings(settings, broadcast.REDIS_ENV_KEY, broadcast.REDIS_CONFIG_KEY)
    if redis_url is None:
        return
    con = redis.StrictRedis.from_url(redis_url, socket_timeout=3, decode_responses=True)
    for key in con.scan_iter(REDIS_PREFIX + '*'):
        level = con.get(key)
        name = key[len(REDIS_PREFIX):]
        if level is not None:
            yield name, level
