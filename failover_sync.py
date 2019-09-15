#!/usr/bin/env python3

import argparse
import logging
import time

from db_test_meter.database import Database
from db_test_meter.test_run import TestRun
from db_test_meter.util import ensure_loop_time, init_logger, collect_user_input

parser = argparse.ArgumentParser()
parser.add_argument('--test_run_id', metavar='<test run id>', type=str, nargs=1, required=True,
                    help='a unique identifier for this test run')
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()
test_run_id = args.test_run_id[0]
init_logger(debug=args.debug)
log = logging.getLogger()

db_connection_metadata = collect_user_input()
db = Database(db_connection_metadata)
test_runner = TestRun(db)

if not test_runner.test_db_connection():
    log.fatal('Initial db connection failed.  Check you connection setup and try again. Exiting...')
    exit(1)

loop_index = 1
while True:
    loop_start_time = time.time()
    # ensure minimum pause of 1 sec between loop iterations
    ensure_loop_time(.5, loop_start_time, test_runner.prev_loop_end_time)
    if test_runner.insert_heartbeat(test_run_id, loop_index):
        loop_index += 1
        continue
    else:
        break

print(f'Total Db connection attempts: {test_runner.success_connect_count + test_runner.failed_connect_count}')
print(f'Successful Db connections: {test_runner.success_connect_count}')
print(f'Failed Db connections: {test_runner.failed_connect_count}')
print(f'Last inserted record, id_index: {loop_index} for test_run_id: {test_run_id}')
