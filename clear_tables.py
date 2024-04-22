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

    def table_exists(self, table_name):
        self.connect()
        try:
            self.cursor.execute(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = %s);",
                (table_name,),
            )
            exists = self.cursor.fetchone()[0]
            return exists
        finally:
            self.close()

    def clear_table_contents(self, table_names):
        for table_name in table_names:
            if self.table_exists(table_name):
                self.connect()
                try:
                    self.cursor.execute(
                        f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;"
                    )
                    self.conn.commit()
                    print(f"Table '{table_name}' has been cleared.")
                except Exception as e:
                    print(f"Error occurred while clearing '{table_name}': {e}")
                finally:
                    self.close()
            else:
                print(f"Table '{table_name}' not found.")


if __name__ == "__main__":
    cleaner = DatabaseCleaner("localhost", "5432", "vectordb", "admin", "admin")
    cleaner.clear_table_contents(["products", "langchain_pg_embedding", "docstore"])
