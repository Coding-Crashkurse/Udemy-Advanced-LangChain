import psycopg2
from psycopg2 import sql


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
                sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                    sql.Identifier(new_user)
                ),
                [new_user_password],
            )
            self.cursor.execute(
                sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                    sql.Identifier(self.conn.info.dbname),
                    sql.Identifier(new_user),
                )
            )
            self.cursor.execute(
                sql.SQL("GRANT SELECT ON ALL TABLES IN SCHEMA public TO {}").format(
                    sql.Identifier(new_user)
                )
            )
            self.cursor.execute(
                sql.SQL(
                    "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO {}"
                ).format(sql.Identifier(new_user))
            )
            self.conn.commit()
            print(f"Read-only user {new_user} created successfully.")
        except Exception as e:
            self.conn.rollback()
            print(f"Error creating read-only user: {e}")
        finally:
            self.close()

    def list_users(self):
        self.connect()
        try:
            self.cursor.execute(sql.SQL("SELECT usename FROM pg_user"))
            users = self.cursor.fetchall()
            return users
        finally:
            self.close()

    def list_roles(self):
        self.connect()
        try:
            self.cursor.execute(
                sql.SQL(
                    "SELECT rolname AS role_name, rolsuper AS is_superuser FROM pg_roles"
                )
            )
            roles = self.cursor.fetchall()
            return roles
        finally:
            self.close()


if __name__ == "__main__":
    creator = DatabaseUserCreator("localhost", "5432", "vectordb", "admin", "admin")

    creator.create_read_only_user("readonlyuser", "readonlypassword")

    users = creator.list_users()
    print("Users:", users)

    roles = creator.list_roles()
    print("Roles:", roles)
