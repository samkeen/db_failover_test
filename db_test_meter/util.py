import getpass
import logging
import os
import sys

from db_test_meter.database import Database

log = logging.getLogger()


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
        path_to_ssl_cert = os.path.abspath(
            input('path to ssl cert [./rds-combined-ca-bundle.pem]: ')) or './rds-combined-ca-bundle.pem'
        if not os.path.exists(path_to_ssl_cert):
            log.fatal(f'SSL cert not found at: {path_to_ssl_cert}')
            exit(1)
        user_input['ssl_metadata'] = {'ssl': {'ca': path_to_ssl_cert}}
    return user_input


def create_db(db: Database) -> bool:
    """
    Utility to create the db and table for the sync check
    :param db:
    :return:
    """
    try:
        log.debug('creating database db_test_meter')
        db.run_query("DROP DATABASE IF EXISTS db_test_meter")
        db.run_query("CREATE DATABASE IF NOT EXISTS db_test_meter")
        log.debug('creating table db_test_meter')
        db.run_query(
            "CREATE TABLE db_sync (`test_run_id` varchar(50) NOT NULL, `index_id` int(10) unsigned NOT NULL, `created` datetime NOT NULL)",
            db='db_test_meter')
        print('Database db_test_meter created')
        print('Table db_test_meter.db_sync created')
    except Exception as e:
        print(f'There was an error: {e}')
