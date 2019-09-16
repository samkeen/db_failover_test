import time

from db_test_meter.database import Database
from db_test_meter.util import log


class TestRun:

    def __init__(self, db: Database):
        self.db = db
        self.success_connect_count: int = 0
        self.failed_connect_count: int = 0
        self.current_phase: str = 'INIT'
        self.prev_loop_end_time: float = 0
        self.failure_condition_start_time: float = 0
        self.failure_condition_end_time: float = 0
        self.heartbeat_index = 0
        self.last_inserted_heartbeat_index = 0

    def test_db_connection(self) -> bool:
        try:
            self.db.run_query('SELECT version()')
            print(f'Connection succeeded at {time.ctime()}')
            self.success_connect_count += 1
            return True
        except Exception as e:
            print(f'There was an error: {e}')
            if self.current_phase == 'INIT':
                self.failure_condition_start_time = time.time()
            self.current_phase = 'FAILING'
            self.failed_connect_count += 1
            if self.failed_connect_count <= 600:  # limit error start to ~ 10 minutes
                return False
            else:
                log.fatal('Maximum Db connection failures of 600 occurred, exiting...')
                exit(1)

    def get_db_node_hostname(self):
        query = "SHOW variables LIKE 'hostname'"
        result = self.db.run_query(query)
        if result and 'Value' in result[0]:
            db_node_hostname = result[0]["Value"]
            log.debug(f'Db node Hostname: {db_node_hostname}')
        else:
            raise Exception(f'Unable to retrieve db node hostname with query: {query}')
        return db_node_hostname

    def db_node_heartbeat(self, test_run_id: str) -> bool:
        try:
            if self.current_phase == 'FAILING':
                return self.test_db_connection()
            else:
                self.db.run_query(
                    "INSERT INTO db_test_meter.db_sync SET test_run_id=%s, index_id=%s, created=UNIX_TIMESTAMP()",
                    (test_run_id, self.heartbeat_index,))
                self.last_inserted_heartbeat_index = self.heartbeat_index
                self.heartbeat_index += 1
                print(f'Insert succeeded at {time.ctime()} test_run_id: {test_run_id}, index_id:{self.heartbeat_index}')
                self.success_connect_count += 1
            return True
        except Exception as e:
            print(f'There was an error: {e}')
            if self.current_phase == 'INIT':
                self.failure_condition_start_time = time.time()
            self.current_phase = 'FAILING'
            # we've failed so kill this connection
            self.db.close_connection()
            self.failed_connect_count += 1
            if self.failed_connect_count <= 600:  # limit error start to ~ 10 minutes
                return False
            else:
                log.fatal('Maximum Db connection failures of 600 occurred, exiting...')
                exit(1)

    def recovery_detected(self) -> bool:
        if self.current_phase == 'FAILING':
            # we've recovered
            log.debug('moving from phase FAILING -> RECOVERED')
            self.current_phase = 'RECOVERED'
            return True
        return False

    def ensure_minumum_loop_time(self, loop_time_min_in_sec: float, loop_start_time: float, prev_loop_end_time: float):

        if prev_loop_end_time != 0:
            log.debug(f'this loop start time: {loop_start_time}')
            log.debug(f'prev loop start end time: {prev_loop_end_time}')
            last_loop_runtime = loop_start_time - prev_loop_end_time
            log.debug(f'last loop runtime: {last_loop_runtime}')
            if last_loop_runtime < loop_time_min_in_sec:
                sleep_time = loop_time_min_in_sec - last_loop_runtime
                log.debug(f'sleeping {sleep_time}')
                time.sleep(sleep_time)

    def get_last_sync_records(self, test_run_id: str, number_of_records: int) -> dict:
        result = self.db.run_query(
            'SELECT * FROM db_test_meter.db_sync WHERE test_run_id = %s ORDER BY `index_id` DESC LIMIT %s',
            (test_run_id, number_of_records))
        return result

    def shutdown(self):
        self.db.close_connection()
