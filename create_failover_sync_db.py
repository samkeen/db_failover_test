#!/usr/bin/env python3

import argparse
import logging

from db_test_meter.database import Database
from db_test_meter.util import init_logger, create_db, collect_user_input

parser = argparse.ArgumentParser()
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
