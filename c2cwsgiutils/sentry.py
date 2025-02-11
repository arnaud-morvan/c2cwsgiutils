import contextlib
import logging
import os
from typing import MutableMapping, Any, Generator, Optional, Callable  # noqa  # pylint: disable=unused-import

import pyramid.config
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration, ignore_logger
from sentry_sdk.integrations.wsgi import SentryWsgiMiddleware

from c2cwsgiutils import _utils

LOG = logging.getLogger(__name__)
_client_setup = False


def _create_before_send_filter(tags: MutableMapping[str, str]) -> Callable[[Any, Any], Any]:
    """
    A filter that adds tags to every events
    """
    def do_filter(event: Any, hint: Any) -> Any:
        event.setdefault("tags", {}).update(tags)
        return event
    return do_filter


def init(config: Optional[pyramid.config.Configurator] = None) -> None:
    global _client_setup
    sentry_url = _utils.env_or_config(config, 'SENTRY_URL', 'c2c.sentry.url')
    if sentry_url is not None and not _client_setup:
        client_info: MutableMapping[str, Any] = {
            key[14:].lower(): value
            for key, value in os.environ.items() if key.startswith('SENTRY_CLIENT_')
        }
        git_hash = _utils.env_or_config(config, 'GIT_HASH', 'c2c.git_hash')
        if git_hash is not None and not ('release' in client_info and client_info['release'] != 'latest'):
            client_info['release'] = git_hash
        client_info['ignore_errors'] = client_info.pop('ignore_exceptions', 'SystemExit').split(",")
        tags = {key[11:].lower(): value
                for key, value in os.environ.items() if key.startswith('SENTRY_TAG_')}

        sentry_logging = LoggingIntegration(
            level=logging.DEBUG,
            event_level=_utils.env_or_config(config, 'SENTRY_LEVEL', 'c2c.sentry_level', 'ERROR').upper()
        )
        sentry_sdk.init(
            dsn=sentry_url,
            integrations=[sentry_logging],
            before_send=_create_before_send_filter(tags),
            **client_info
        )
        _client_setup = True

        excludes = _utils.env_or_config(config, "SENTRY_EXCLUDES", "c2c.sentry.excludes",
                                        "sentry_sdk").split(",")
        for exclude in excludes:
            ignore_logger(exclude)

        LOG.info("Configured sentry reporting with client=%s and tags=%s",
                 repr(client_info), repr(tags))


@contextlib.contextmanager
def capture_exceptions() -> Generator[None, None, None]:
    """
    Will send exceptions raised withing the context to Sentry.

    You don't need to use that for exception terminating the process (those not catched). Sentry does that
    already.
    """
    global _client_setup
    if _client_setup:
        try:
            yield
        except Exception:
            sentry_sdk.capture_exception()
            raise
    else:
        yield


def filter_wsgi_app(application: Callable[..., Any]) -> Callable[..., Any]:
    """
    If sentry is configured, add a Sentry filter around the application
    """
    global _client_setup
    if _client_setup:
        try:
            LOG.info("Enable WSGI filter for Sentry")
            return SentryWsgiMiddleware(application)
        except Exception:
            LOG.error("Failed enabling sentry. Continuing without it.", exc_info=True)
            return application
    else:
        return application
