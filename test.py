CONNECTION_STRING = "postgresql+psycopg2://admin:admin@127.0.0.1:5432/vectordb"


from sqlalchemy import create_engine, inspect
from tabulate import tabulate


def get_schema():
    engine = create_engine(CONNECTION_STRING)

    inspector = inspect(engine)
    columns = inspector.get_columns("products")

    column_data = [
        {
            "Column Name": col["name"],
            "Data Type": str(col["type"]),
            "Nullable": "Yes" if col["nullable"] else "No",
            "Default": col["default"] if col["default"] else "None",
            "Autoincrement": "Yes" if col["autoincrement"] else "No",
        }
        for col in columns
    ]
    schema_output = tabulate(column_data, headers="keys", tablefmt="grid")
    formatted_schema = f"Schema for 'products' table:\n{schema_output}"

    return formatted_schema


print(get_schema())
