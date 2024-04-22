import psycopg2


class DatabaseManager:
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
        self.cursor.close()
        self.conn.close()

    def setup_database(self):
        self.connect()

        # Create a new table for products
        create_table_query = """
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE,
            price DECIMAL(10, 2),
            description TEXT,
            category VARCHAR(100)
        );
        """
        self.cursor.execute(create_table_query)
        self.conn.commit()

        self.close()

    def insert_food_items(self, file_path):
        self.connect()

        # Read data from the provided file
        with open(file_path, "r") as file:
            food_items = file.readlines()

        # Insert each food item into the database
        for line in food_items:
            name, price, description, category = line.strip().split("; ")
            price = price.replace("$", "")  # Remove the dollar sign
            insert_query = """
            INSERT INTO products (name, price, description, category)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (name) DO NOTHING;
            """
            self.cursor.execute(insert_query, (name, price, description, category))

        self.conn.commit()
        self.close()

    def query_and_print(self):
        self.connect()
        self.cursor.execute("SELECT * FROM products;")
        products = self.cursor.fetchall()
        for product in products:
            print(product)
        self.close()


if __name__ == "__main__":
    db_manager = DatabaseManager("localhost", "5432", "vectordb", "admin", "admin")
    db_manager.setup_database()
    db_manager.insert_food_items("./data/food.txt")
    db_manager.query_and_print()
