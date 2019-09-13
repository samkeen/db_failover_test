import getpass
import logging
import os
import sys
import time

import pymysql

log = logging.getLogger()


def init_logger(debug=False) -> None:
    log_level = logging.DEBUG if debug else logging.WARNING
    logging.getLogger().setLevel(log_level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    log.addHandler(handler)


def ensure_loop_time(loop_time_min_in_sec: float, loop_start_time: float, prev_loop_end_time: float):
    """
    Used to ensure a minimum runtime for a given loop iteration.

    :param loop_time_min_in_sec: The minimum runtime allowed for a loop.  We will sleep any time needed to meet this
    minimum
    :type loop_time_min_in_sec: float
    :param loop_start_time:
    :type loop_start_time: float
    :param prev_loop_end_time:
    :type prev_loop_end_time: float
    :return:
    :rtype: None
    """
    if prev_loop_end_time is not None:
        log.debug(f'this loop start time: {loop_start_time}')
        log.debug(f'prev loop start end time: {prev_loop_end_time}')
        last_loop_runtime = loop_start_time - prev_loop_end_time
        log.debug(f'last loop runtime: {last_loop_runtime}')
        if last_loop_runtime < 1:
            sleep_time = 1 - last_loop_runtime
            log.debug(f'sleeping {sleep_time}')
            time.sleep(sleep_time)


def get_db_connection(db_connection_metadata: dict) -> pymysql.Connection:
    """

    :param db_connection_metadata:
    :type db_connection_metadata: dict
    :return:
    :rtype: pymysql.Connection
    """
    return pymysql.connect(host=db_connection_metadata['db_host'],
                           port=int(db_connection_metadata['db_port']),
                           user=db_connection_metadata['db_user'],
                           password=db_connection_metadata['db_password'],
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor,
                           read_timeout=db_connection_metadata['db_interact_timeout'],  # 1 sec
                           write_timeout=db_connection_metadata['db_interact_timeout'],  # 1 sec
                           connect_timeout=db_connection_metadata['db_interact_timeout'],  # 1 sec
                           ssl=db_connection_metadata['ssl_metadata']
                           )


def collect_user_input() -> dict:
    db_connection_metadata = {'ssl_metadata': None}
    db_connection_metadata['db_interact_timeout'] = 1  # 1 sec
    db_connection_metadata['db_host'] = input("RDS Endpoint: [localhost]") or 'localhost'
    db_connection_metadata['db_port'] = input("Db port [3306]: ") or '3306'
    db_connection_metadata['db_user'] = input("Db User [root]: ") or 'root'
    db_connection_metadata['db_password'] = getpass.getpass('Password for Db user: ')
    using_ssl = input('Connecting over SSL (y/n) [y]: ').strip().lower() or 'y'
    if using_ssl == 'y':
        path_to_ssl_cert = os.path.abspath(
            input('path to ssl cert [./rds-combined-ca-bundle.pem]: ')) or './rds-combined-ca-bundle.pem'
        if not os.path.exists(path_to_ssl_cert):
            log.fatal(f'SSL cert not found at: {path_to_ssl_cert}')
            exit(1)
        db_connection_metadata['ssl_metadata'] = {'ssl': {'ca': path_to_ssl_cert}}
    return db_connection_metadata


def test_db_connection(db_connection_metadata) -> bool:
    connection = None
    try:
        log.debug('building connection')
        connection = get_db_connection(db_connection_metadata)
        log.debug('building cursor')
        cursor = connection.cursor()
        sql = "SELECT version()"
        log.debug('executing query')
        cursor.execute(sql)
        print(f'Connection succeeded at {time.ctime()}')
        cursor.close()
        connection.close()
        TestRun.success_connect_count += 1
        return True
    except Exception as e:
        print(f'There was an error: {e}')
        if TestRun.current_phase == 'INIT':
            TestRun.failure_condition_start_time = time.time()
        TestRun.current_phase = 'FAILING'
        TestRun.failed_connect_count += 1
        if TestRun.failed_connect_count <= 600:  # limit error start to ~ 10 minutes
            TestRun.prev_loop_end_time = time.time()
            return False
        else:
            log.fatal('Maximum Db connection failures of 600 occurred, exiting...')
            exit(1)
    finally:
        if connection and connection.open:
            connection.close()


def recovery_detected() -> bool:
    if TestRun.current_phase == 'FAILING':
        # we've recovered
        log.debug('moving from phase FAILING -> RECOVERED')
        TestRun.current_phase = 'RECOVERED'
        return True
    return False


# little state tracking class
class TestRun:
    success_connect_count: int = 0
    failed_connect_count: int = 0
    current_phase: str = 'INIT'
    prev_loop_end_time: float = 0
    failure_condition_start_time: float = 0
    failure_condition_end_time: float = 0
