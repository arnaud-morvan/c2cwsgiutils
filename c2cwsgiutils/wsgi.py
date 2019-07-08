import logging
import os
from typing import Optional, Any

from pyramid.paster import get_app

from c2cwsgiutils import pyramid_logging


def create_application(configuri: Optional[str] = None) -> Any:
    """
    Create a standard WSGI application with the capabilities to use environment variables in the
    configuration file (use %(ENV_VAR)s place holders)

    :param configfile: The configuration file to use
    :return: The application
    """
    configuri_ = pyramid_logging.init(configuri)
    # Load the logging config without using pyramid to be able to use environment variables in there.
    try:
        return get_app(configuri_, 'main', options=os.environ)
    except Exception:
        logging.getLogger(__name__).exception("Failed starting the application")
        raise
