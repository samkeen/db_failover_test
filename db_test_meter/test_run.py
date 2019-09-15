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

    def test_db_connection(self) -> bool:
        try:
            log.debug('building connection')
            log.debug('building cursor')
            # sql = "SHOW variables LIKE 'hostname'"
            log.debug('executing query')
            result = self.db.run_query('SELECT version()')
            print(f'Result {result}')
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
                self.prev_loop_end_time = time.time()
                return False
            else:
                log.fatal('Maximum Db connection failures of 600 occurred, exiting...')
                exit(1)

    def insert_heartbeat(self, test_run_id: str, index_id: int) -> bool:
        try:
            log.debug('executing query')
            self.db.run_query("INSERT INTO db_sync SET test_run_id=%s, index_id=%s, created=now()",
                              (test_run_id, index_id,),
                              db='db_test_meter')
            print(f'Insert succeeded at {time.ctime()} test_run_id: {test_run_id}, index_id:{index_id}')
            self.prev_loop_end_time = time.time()
            self.success_connect_count += 1
            return True
        except Exception as e:
            print(f'There was an error: {e}')
            self.failed_connect_count += 1
            return False

    def recovery_detected(self) -> bool:
        if self.current_phase == 'FAILING':
            # we've recovered
            log.debug('moving from phase FAILING -> RECOVERED')
            self.current_phase = 'RECOVERED'
            return True
        return False

    def ensure_loop_time(self, loop_time_min_in_sec: float, loop_start_time: float, prev_loop_end_time: float):
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
            if last_loop_runtime < loop_time_min_in_sec:
                sleep_time = loop_time_min_in_sec - last_loop_runtime
                log.debug(f'sleeping {sleep_time}')
                time.sleep(sleep_time)