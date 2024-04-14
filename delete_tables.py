import psycopg2


class DatabaseCleaner:
    def __init__(self, host, port, dbname, user, password):
        self.conn_string = (
            f"host={host} port={port} dbname={dbname} user={user} password={password}"
        )
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = psycopg2.connect(self.conn_string)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None:
            self.conn.close()

    def drop_tables(self, table_names):
        self.connect()
        try:
            for table_name in table_names:
                self.cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            self.conn.commit()
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            self.close()


if __name__ == "__main__":
    cleaner = DatabaseCleaner("localhost", "5432", "vectordb", "admin", "admin")
    cleaner.drop_tables(["products", "langchain_pg_embedding"])
89
