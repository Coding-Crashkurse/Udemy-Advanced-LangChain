import os

from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from sqlalchemy import create_engine, inspect
from tabulate import tabulate

template = """Based on the table schema below, write a SQL query that would answer the user's question:
{schema}

Question: {question}
SQL Query:"""
prompt = ChatPromptTemplate.from_template(template)


db_user = os.getenv("DB_USER", "admin")
db_password = os.getenv("DB_PASSWORD", "admin")
db_host = os.getenv("DB_HOST", "127.0.0.1")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME", "vectordb")

CONNECTION_STRING = (
    f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
)
db = SQLDatabase.from_uri(CONNECTION_STRING)


def get_schema(_):
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
    formatted_schema = f"Schema for 'PRODUCTS' table:\n{schema_output}"

    return formatted_schema


def run_query(query):
    return db.run(query)


model = ChatOpenAI()

sql_response = (
    RunnablePassthrough.assign(schema=get_schema)
    | prompt
    | model.bind(stop=["\nSQLResult:"])
    | StrOutputParser()
)


template = """Based on the table schema below, question, sql query, and sql response, write a natural language response:
{schema}

Question: {question}
SQL Query: {query}
SQL Response: {response}"""
prompt_response = ChatPromptTemplate.from_template(template)

sql_chain = (
    RunnablePassthrough.assign(query=sql_response).assign(
        schema=get_schema,
        response=lambda x: run_query(x["query"]),
    )
    | prompt_response
    | model
    | StrOutputParser()
)
