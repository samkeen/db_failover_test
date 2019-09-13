#!/usr/bin/env python3

##############################################
#
import argparse
import logging
import time

from db_test_meter.util import ensure_loop_time, collect_user_input, test_db_connection, TestRun, init_logger, \
    insert_heartbeat

parser = argparse.ArgumentParser()
parser.add_argument('--test_run_id', metavar='test run id', type=str, nargs=1, required=True,
                    help='a unique identifier for this test run')
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()
init_logger(debug=args.debug)
log = logging.getLogger()


db_connection_metadata = collect_user_input()
test_run_id = args.test_run_id[0]

if not test_db_connection(db_connection_metadata):
    log.fatal('Initial db connection failed.  Check you connection setup and try again. Exiting...')
    exit(1)

loop_index = 1
while True:
    loop_start_time = time.time()
    # ensure minimum pause of 1 sec between loop iterations
    ensure_loop_time(.5, loop_start_time, TestRun.prev_loop_end_time)
    if insert_heartbeat(db_connection_metadata, test_run_id, loop_index):
        loop_index += 1
        continue
    else:
        break

print(f'Total Db connection attempts: {TestRun.success_connect_count + TestRun.failed_connect_count}')
print(f'Successful Db connections: {TestRun.success_connect_count}')
print(f'Failed Db connections: {TestRun.failed_connect_count}')
print(f'Last inserted record, id_index: {loop_index} for test_run_id: {test_run_id}')
