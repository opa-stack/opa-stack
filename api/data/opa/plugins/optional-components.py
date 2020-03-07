import socket
import logging
from databases import DatabaseURL
from opa.core import config

from opa.utils.mongodb import connect_to_mongo, close_mongo_connection


def get_hostname_from_db_url(url):
    return DatabaseURL(url).hostname


def setup_loading(app, compconf, hostname_resolver, startup_func, shutdown_func):
    if compconf.LOAD == 'auto':
        hostname = hostname_resolver(compconf)
        try:
            socket.gethostbyname(hostname)
            should_load = True
        except socket.gaierror:
            should_load = False
    elif compconf.LOAD == 'yes':
        should_load = True
    elif compconf.LOAD == 'no':
        should_load = False
    else:
        raise Exception(
            f'Invalid load-config for component, got {compconf.LOAD}, expected (auto|yes[no)'
        )

    if should_load:
        app.add_event_handler("startup", startup_func)
        app.add_event_handler("shutdown", shutdown_func)


def setup(app, **kwargs):
    setup_loading(
        app,
        config.OPTIONAL_COMPONENTS.MONGODB,
        lambda x: get_hostname_from_db_url(x.URL),
        connect_to_mongo,
        close_mongo_connection,
    )
