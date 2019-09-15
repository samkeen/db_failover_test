#!/usr/bin/env python3

import argparse
import logging
import pprint
import time

from db_test_meter.database import Database
from db_test_meter.test_run import TestRun
from db_test_meter.util import init_logger, collect_user_input

parser = argparse.ArgumentParser()
parser.add_argument('--test_run_id', metavar='<test run id>', type=str, nargs='?', required=True,
                    help='a unique identifier for this test run')
parser.add_argument('--loop_time', metavar='<seconds>', type=float, nargs='?', default='.5',
                    help='sleep is used to insure this minimum loop time in sec. Can be decimal (defaults to .5')
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()
test_run_id = args.test_run_id
loop_time = args.loop_time
if loop_time <= 0:
    print('Loop time must be >= 0, exiting...')
    exit(1)
init_logger(debug=args.debug)
log = logging.getLogger()

db_connection_metadata = collect_user_input()
db = Database(db_connection_metadata)
test_runner = TestRun(db)

if not test_runner.test_db_connection():
    log.fatal('Initial db connection failed.  Check you connection setup and try again. Exiting...')
    exit(1)

pre_failure_db_node_hostname = test_runner.get_db_node_hostname()
print(f'Test starting, initial Db node hostname: {pre_failure_db_node_hostname}')
post_failure_db_node_hostname = None

while True:
    loop_start_time = time.time()
    test_runner.ensure_minumum_loop_time(loop_time, loop_start_time, test_runner.prev_loop_end_time)
    if test_runner.db_node_heartbeat(test_run_id):
        if test_runner.recovery_detected():
            test_runner.failure_condition_end_time = time.time()
            post_failure_db_node_hostname = test_runner.get_db_node_hostname()
            test_runner.prev_loop_end_time = time.time()
            break
    test_runner.prev_loop_end_time = time.time()

pp = pprint.PrettyPrinter(indent=2)
print(f'Total Db connection attempts: {test_runner.success_connect_count + test_runner.failed_connect_count}')
print(f'Successful Db connections: {test_runner.success_connect_count}')
print(f'Failed Db connections: {test_runner.failed_connect_count}')
print(f'failure_start_time: {time.ctime(test_runner.failure_condition_start_time)}')
print(f'failure_end_time: {time.ctime(test_runner.failure_condition_end_time)}')
duration = int(test_runner.failure_condition_end_time - test_runner.failure_condition_start_time)
print(f'failure condition duration: {duration} seconds')
print(f'Last inserted sync record id on initial primary db node: {test_runner.last_inserted_heartbeat_index}')
print(f'Pre-failure Db node hostname: {pre_failure_db_node_hostname}')
print(f'Post-failure Db node hostname: {post_failure_db_node_hostname}')
print(f'Newest 5 sync records in current primary db node:')
pp.pprint(test_runner.get_last_sync_records(test_run_id, 5))
