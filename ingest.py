import psycopg2

# Database connection parameters
host = "localhost"
port = "5432"
dbname = "vectordb"
user = "admin"
password = "admin"

# Establish a connection to the database
conn_string = f"host={host} port={port} dbname={dbname} user={user} password={password}"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

# Drop existing tables if they exist
cursor.execute("DROP TABLE IF EXISTS products;")
cursor.execute("DROP TABLE IF EXISTS langchain_pg_embedding;")
conn.commit()

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
cursor.execute(create_table_query)

# Read data from food.txt
with open("./data/food.txt", "r") as file:
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
    cursor.execute(insert_query, (name, price, description, category))

# Commit the transaction
conn.commit()

# Query and print the data to verify insertion
cursor.execute("SELECT * FROM products;")
products = cursor.fetchall()
for product in products:
    print(product)

# Close the cursor and connection
cursor.close()
conn.close()
