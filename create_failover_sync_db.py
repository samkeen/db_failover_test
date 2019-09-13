#!/usr/bin/env python3

##############################################
#
import argparse
import logging

from db_test_meter.util import collect_user_input, test_db_connection, init_logger, create_db

parser = argparse.ArgumentParser()
parser.add_argument('--debug', action='store_true')
init_logger(debug=parser.parse_args().debug)
log = logging.getLogger()

db_connection_metadata = collect_user_input()

if not test_db_connection(db_connection_metadata):
    log.fatal('Initial db connection failed.  Check you connection setup and try again. Exiting...')
    exit(1)

create_db(db_connection_metadata)

# print(f'Total Db connection attempts: {TestRun.success_connect_count + TestRun.failed_connect_count}')
# print(f'Successful Db connections: {TestRun.success_connect_count}')
# print(f'Failed Db connections: {TestRun.failed_connect_count}')
# print(f'failure_start_time: {time.ctime(TestRun.failure_condition_start_time)}')
# print(f'failure_end_time: {time.ctime(TestRun.failure_condition_end_time)}')
# print(
#     f'failure condition duration: {int(TestRun.failure_condition_end_time - TestRun.failure_condition_start_time)} seconds')
