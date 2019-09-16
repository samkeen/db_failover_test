#!/usr/bin/env python3

import argparse
import logging

from db_test_meter.database import Database
from db_test_meter.util import init_logger, collect_user_input, AppConfig


def create_db(db: Database) -> None:
    """
    Utility to create the db and table for the sync check
    :param db:
    :return:
    """
    try:
        log.debug(f'creating database {AppConfig.TEST_DB_NAME}')
        db.run_query(f"DROP DATABASE IF EXISTS {AppConfig.TEST_DB_NAME}")
        db.run_query(f"CREATE DATABASE IF NOT EXISTS {AppConfig.TEST_DB_NAME}")
        log.debug(f'creating table {AppConfig.TEST_DB_TABLE}')
        db.run_query(
            f"CREATE TABLE {AppConfig.TEST_DB_NAME}.{AppConfig.TEST_DB_TABLE} (`test_run_id` varchar(50) NOT NULL, `index_id` int(10) unsigned NOT NULL, `created` int(8) NOT NULL)")
        print(f'Database {AppConfig.TEST_DB_NAME} created')
        print(f'Table {AppConfig.TEST_DB_TABLE}.{AppConfig.TEST_DB_TABLE} created')
    except Exception as e:
        print(f'There was an error: {e}')


parser = argparse.ArgumentParser(
    'simple utility to create the db and table used by failover_test.py. Usage: ./create_failover_sync_db.py')
parser.add_argument('--debug', action='store_true')
init_logger(debug=parser.parse_args().debug)
log = logging.getLogger()

print('This will destroy and recreate sync database and tracking table')
if (input("enter y to continue, n to exit [n]: ") or 'n').lower() == 'y':
    db_connection_metadata = collect_user_input()
    db = Database(db_connection_metadata)
    create_db(db)
else:
    print('exiting...')
