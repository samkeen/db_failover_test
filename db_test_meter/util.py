import getpass
import logging
import os
import sys

log = logging.getLogger()


class AppConfig:
    TEST_DB_NAME = 'db_test_meter'
    TEST_DB_TABLE = 'db_sync'


def init_logger(debug=False) -> None:
    log_level = logging.DEBUG if debug else logging.WARNING
    logging.getLogger().setLevel(log_level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    log.addHandler(handler)


def collect_user_input() -> dict:
    user_input = {'ssl_metadata': None}
    user_input['db_interact_timeout'] = 1  # 1 sec
    user_input['db_host'] = input("RDS Endpoint [localhost]: ") or 'localhost'
    user_input['db_port'] = input("Db port [3306]: ") or '3306'
    user_input['db_user'] = input("Db User [root]: ") or 'root'
    user_input['db_password'] = getpass.getpass('Password for Db user: ')
    using_ssl = input('Connecting over SSL (y/n) [y]: ').strip().lower() or 'y'
    if using_ssl == 'y':
        path_to_ssl_cert = input('path to ssl cert [./rds-combined-ca-bundle.pem]: ') or './rds-combined-ca-bundle.pem'
        if not os.path.exists(os.path.abspath(path_to_ssl_cert)):
            log.fatal(f'SSL cert not found at: {path_to_ssl_cert}')
            exit(1)
        user_input['ssl_metadata'] = {'ssl': {'ca': path_to_ssl_cert}}
    return user_input