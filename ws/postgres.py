import psycopg2

class PostgresConnection():
    def __init__(self):
        # should it go inside __enter__?
        # host= IP it seems that may change...
        self.conn = psycopg2.connect(
            host="192.168.0.7", #
            database="pladigpsico",
            user="pladigpsico",
            password="pladigpsico"
        )

    def __enter__(self):
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.conn is not None:
                self.conn.close()
                print('Database connection closed.')
        except Exception as error:
            print('Exception when closing database connection')


def postgresVersion():
    with PostgresConnection() as conn:
        with conn.cursor() as cur:
            print('PostgreSQL database version:')
            cur.execute('select version()')
            db_version = cur.fetchone()
            print(db_version)
    
    pass

if __name__ == '__main__':
    postgresVersion()