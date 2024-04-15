from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.output_parsers import StrOutputParser

template = """Based on the table schema below, write a SQL query that would answer the user's question:
{schema}

Question: {question}
SQL Query:"""
prompt = ChatPromptTemplate.from_template(template)


DATABASE_URL = "postgresql+psycopg2://admin:admin@localhost:5432/vectordb"

db = SQLDatabase.from_uri(DATABASE_URL)


def get_schema(_):
    schema = db.get_table_info()
    return schema


def run_query(query):
    return db.run(query)


DATABASE_URL = "postgresql+psycopg2://admin:admin@localhost:5432/vectordb"

db = SQLDatabase.from_uri(DATABASE_URL)


def get_schema(_):
    schema = db.get_table_info()
    return schema


def run_query(query):
    return db.run(query)


from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

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
