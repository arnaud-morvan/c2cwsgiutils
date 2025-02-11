"""
Generate statsd metrics for pyramid and SQLAlchemy events.
"""
import pyramid.config
import pyramid.request

from c2cwsgiutils import stats


def init(config: pyramid.config.Configurator) -> None:
    """
    Initialize the whole stats module.

    :param config: The Pyramid config
    """
    stats.init_backends(config.get_settings())
    if stats.BACKENDS:  # pragma: nocover
        if 'memory' in stats.BACKENDS:  # pragma: nocover
            from . import _views
            _views.init(config)
        from . import _pyramid_spy
        _pyramid_spy.init(config)
        init_db_spy()


def init_db_spy() -> None:
    from . import _db_spy
    _db_spy.init()
