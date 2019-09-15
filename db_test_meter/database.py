import sys
import pymysql
import logging


class Database:
    """Database connection class."""

    def __init__(self, db_connection_metadata):
        self.host = db_connection_metadata['db_host']
        self.port = int(db_connection_metadata['db_port'])
        self.username = db_connection_metadata['db_user']
        self.password = db_connection_metadata['db_password']
        self.charset = 'utf8mb4'
        self.cursorclass = pymysql.cursors.DictCursor
        self.read_timeout = db_connection_metadata['db_interact_timeout']  # 1 sec
        self.write_timeout = db_connection_metadata['db_interact_timeout']  # 1 sec
        self.connect_timeout = db_connection_metadata['db_interact_timeout']  # 1 sec
        self.ssl_metadata = db_connection_metadata['ssl_metadata']

        # self.dbname = config.db_name
        self.conn = None

    def open_connection(self, db=None):

        if self.conn is None:
            self.conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                read_timeout=self.read_timeout,  # 1 sec
                write_timeout=self.write_timeout,  # 1 sec
                connect_timeout=self.connect_timeout,  # 1 sec
                ssl=self.ssl_metadata,
                database=db
            )
            logging.info('Connection opened successfully.')

    def run_query(self, query, query_params=None, db=None):
        """Execute SQL query."""
        try:
            self.open_connection(db)
            with self.conn.cursor() as cur:
                if 'SELECT' in query or 'SHOW' in query:
                    records = []
                    cur.execute(query)
                    result = cur.fetchall()
                    for row in result:
                        records.append(row)
                    cur.close()
                    return records
                else:
                    result = cur.execute(query, query_params)
                    self.conn.commit()
                    affected = f"{cur.rowcount} rows affected."
                    cur.close()
                    return affected
        except pymysql.MySQLError as e:
            print(e)
            raise Exception('Db Connection failed')
        finally:
            if self.conn:
                self.conn.close()
                self.conn = None
                logging.info('Database connection closed.')
