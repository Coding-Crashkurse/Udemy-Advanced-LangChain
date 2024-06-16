import decimal
import os

import psycopg2
from langchain_community.document_loaders.text import TextLoader
from store import create_retriever


class DataIngestionManager:
    def __init__(self):
        db_user = os.getenv("DB_USER", "admin")
        db_password = os.getenv("DB_PASSWORD", "admin")
        db_host = os.getenv("DB_HOST", "127.0.0.1")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "vectordb")

        # Correct format for psycopg2
        self.conn_string = f"host={db_host} port={db_port} dbname={db_name} user={db_user} password={db_password}"

        # SQLAlchemy connection string for retriever
        self.vector_connection_string = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

        self.conn = None
        self.cursor = None
        self.retriever = create_retriever(self.vector_connection_string)

    def connect(self):
        if not self.conn:
            # psycopg2 uses the plain connection string format
            self.conn = psycopg2.connect(self.conn_string)
            self.cursor = self.conn.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def ingest_vector_data(self, file_paths):
        docs = []
        for file_path in file_paths:
            loader = TextLoader(file_path)
            docs.extend(loader.load())

        self.retriever.add_documents(docs)

    def ingest_tabular_data(self, file_path):
        self.connect()

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

        with open(file_path, "r") as file:
            food_items = file.readlines()

        insert_query = """
        INSERT INTO products (name, price, description, category)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (name) DO NOTHING;
        """
        for line in food_items:
            name, price_str, description, category = line.strip().split("; ")

            # Strip the dollar sign and convert the price to a decimal
            price = decimal.Decimal(price_str.replace("$", ""))

            # Execute the insert query with the converted price
            self.cursor.execute(insert_query, (name, price, description, category))

        self.conn.commit()

    def query_products(self):
        self.connect()
        self.cursor.execute("SELECT * FROM products;")
        products = self.cursor.fetchall()
        for product in products:
            print(product)
        self.close()


if __name__ == "__main__":
    data_manager = DataIngestionManager()
    data_manager.ingest_vector_data(["./data/restaurant.txt", "./data/founder.txt"])
    data_manager.ingest_tabular_data("./data/food.txt")
