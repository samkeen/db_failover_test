#!/usr/bin/env python3

##############################################
# This script will start executing a 'heartbeat' query to the given MySQL database, roughly once every second.
# When there is a connection disruption, it will continue to try connections every sec.
# When connectivity returns, it will stop and report the total time the db was not accessible.
# This can be used measure the amount of time required for Failover in Db clusters with such capability

# Workflow:
#  1. execute this script
#  2. Take the action on you Db to initiate fail over workflow.
#
import argparse
import logging
import time

from db_test_meter.database import Database
from db_test_meter.test_run import TestRun
from db_test_meter.util import init_logger, collect_user_input

parser = argparse.ArgumentParser()
parser.add_argument('--debug', action='store_true')
init_logger(debug=parser.parse_args().debug)
log = logging.getLogger()

db_connection_metadata = collect_user_input()
db = Database(db_connection_metadata)
test_runner = TestRun(db)

if not test_runner.test_db_connection():
    log.fatal('Initial db connection failed.  Check you connection setup and try again. Exiting...')
    exit(1)

while True:
    loop_start_time = time.time()
    # ensure minimum pause of 1 sec between loop iterations
    test_runner.ensure_loop_time(1, loop_start_time, test_runner.prev_loop_end_time)
    if test_runner.test_db_connection():
        if test_runner.recovery_detected():
            test_runner.failure_condition_end_time = time.time()
            break
        else:
            # we have either not entered error state or are still in error state
            test_runner.prev_loop_end_time = time.time()
    else:
        continue

print(f'Total Db connection attempts: {test_runner.success_connect_count + test_runner.failed_connect_count}')
print(f'Successful Db connections: {test_runner.success_connect_count}')
print(f'Failed Db connections: {test_runner.failed_connect_count}')
print(f'failure_start_time: {time.ctime(test_runner.failure_condition_start_time)}')
print(f'failure_end_time: {time.ctime(test_runner.failure_condition_end_time)}')
duration = int(test_runner.failure_condition_end_time - test_runner.failure_condition_start_time)
print(f'failure condition duration: {duration} seconds')
