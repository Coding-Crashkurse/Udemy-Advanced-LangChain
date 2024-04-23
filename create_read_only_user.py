import psycopg2


class DatabaseUserCreator:
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

    def create_read_only_user(self, new_user, new_user_password):
        self.connect()
        try:
            self.cursor.execute(
                f"CREATE USER {new_user} WITH PASSWORD %s;", (new_user_password,)
            )
            self.cursor.execute(
                f"GRANT CONNECT ON DATABASE {self.conn.info.dbname} TO {new_user};"
            )
            self.cursor.execute(
                f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {new_user};"
            )
            self.cursor.execute(
                f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT TO {new_user};"
            )
            self.conn.commit()
            print(f"Read-only user '{new_user}' created successfully.")
        except Exception as e:
            self.conn.rollback()
            print(f"Error creating read-only user: {e}")
        finally:
            self.close()


if __name__ == "__main__":
    creator = DatabaseUserCreator("localhost", "5432", "vectordb", "admin", "admin")
    creator.create_read_only_user("readonly_user", "readonly_password")
