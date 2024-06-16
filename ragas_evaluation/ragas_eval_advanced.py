import logging
import os
from typing import Generic, Iterator, Optional, Sequence, TypeVar

from dotenv import load_dotenv
from langchain.prompts.prompt import PromptTemplate
from langchain.retrievers import ParentDocumentRetriever
from langchain.schema import Document
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.vectorstores.pgvector import PGVector
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import (RunnableLambda, RunnableParallel,
                                      RunnablePassthrough)
from langchain_core.stores import BaseStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from nemoguardrails import RailsConfig
from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails
from pydantic import BaseModel, Field
from ragas_prep import RAGASEvaluator, ground_truth, questions
from sentence_transformers import CrossEncoder
from sqlalchemy import Column, String, create_engine, inspect
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker
from tabulate import tabulate

parent_dir = os.path.dirname(os.getcwd())
app_dir = os.path.join(parent_dir, "app")
env_path = os.path.join(app_dir, ".env")
load_dotenv(env_path)


Base = declarative_base()


class DocumentModel(BaseModel):
    key: Optional[str] = Field(None)
    page_content: Optional[str] = Field(None)
    metadata: dict = Field(default_factory=dict)


class SQLDocument(Base):
    __tablename__ = "docstore"
    key = Column(String, primary_key=True)
    value = Column(JSONB)

    def __repr__(self):
        return f"<SQLDocument(key='{self.key}', value='{self.value}')>"


logger = logging.getLogger(__name__)

D = TypeVar("D", bound=Document)


class PostgresStore(BaseStore[str, DocumentModel], Generic[D]):
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        Base.metadata.create_all(self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def serialize_document(self, doc: Document) -> dict:
        return {"page_content": doc.page_content, "metadata": doc.metadata}

    def deserialize_document(self, value: dict) -> Document:
        return Document(
            page_content=value.get("page_content", ""),
            metadata=value.get("metadata", {}),
        )

    def mget(self, keys: Sequence[str]) -> list[Document]:
        with self.Session() as session:
            try:
                sql_documents = (
                    session.query(SQLDocument).filter(SQLDocument.key.in_(keys)).all()
                )
                return [
                    self.deserialize_document(sql_doc.value)
                    for sql_doc in sql_documents
                ]
            except Exception as e:
                logger.error(f"Error in mget: {e}")
                session.rollback()
                return []

    def mset(self, key_value_pairs: Sequence[tuple[str, Document]]) -> None:
        with self.Session() as session:
            try:
                serialized_docs = []
                for key, document in key_value_pairs:
                    serialized_doc = self.serialize_document(document)
                    serialized_docs.append((key, serialized_doc))

                documents_to_update = [
                    SQLDocument(key=key, value=value) for key, value in serialized_docs
                ]
                session.bulk_save_objects(documents_to_update, update_changed_only=True)
                session.commit()
            except Exception as e:
                logger.error(f"Error in mset: {e}")
                session.rollback()

    def mdelete(self, keys: Sequence[str]) -> None:
        with self.Session() as session:
            try:
                session.query(SQLDocument).filter(SQLDocument.key.in_(keys)).delete(
                    synchronize_session=False
                )
                session.commit()
            except Exception as e:
                logger.error(f"Error in mdelete: {e}")
                session.rollback()

    def yield_keys(self, *, prefix: Optional[str] = None) -> Iterator[str]:
        with self.Session() as session:
            try:
                query = session.query(SQLDocument.key)
                if prefix:
                    query = query.filter(SQLDocument.key.like(f"{prefix}%"))
                for key in query:
                    yield key[0]
            except Exception as e:
                logger.error(f"Error in yield_keys: {e}")
                session.rollback()


# Function to create a retriever
def create_retriever(
    database_url: str,
    embedding_model: str = "text-embedding-3-large",
    embedding_dimensions: int = 1536,
) -> ParentDocumentRetriever:
    """
    Create and return a ParentDocumentRetriever.

    :param database_url: The connection string for the database.
    :param embedding_model: The OpenAI embedding model to use. Default is 'text-embedding-3-large'.
    :param embedding_dimensions: The dimensions of the embeddings. Default is 1536.
    :return: An instance of ParentDocumentRetriever.
    """

    embeddings = OpenAIEmbeddings(
        model=embedding_model, dimensions=embedding_dimensions
    )
    docstore = PostgresStore(connection_string=database_url)

    vectorstore = PGVector(
        collection_name="vectordb",
        connection_string=database_url,
        embedding_function=embeddings,
    )

    text_splitter_child = RecursiveCharacterTextSplitter(
        chunk_size=150, chunk_overlap=20
    )
    text_splitter_parent = RecursiveCharacterTextSplitter(
        chunk_size=400, chunk_overlap=20
    )
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=docstore,
        parent_splitter=text_splitter_parent,
        child_splitter=text_splitter_child,
    )

    return retriever


classification_template = PromptTemplate.from_template(
    """You are good at classifying a question.
    Given the user question below, classify it as either being about `Database`, `Chat` or 'Offtopic'.

    <If the question is about products of the restaurant like food, drinks and anything related to the products of a restaurant, classify the question as 'Database'>
    <If the question is about restaurant related topics like opening hours, the history of the restaurant and similar topics, classify it as 'Chat'>
    <If the question is about whether, football or anything not related to the restaurant or
    products, classify the question as 'offtopic'>

    <question>
    {question}
    </question>

    Classification:"""
)

classification_chain = classification_template | ChatOpenAI() | StrOutputParser()


CONNECTION_STRING = "postgresql+psycopg2://admin:admin@127.0.0.1:5432/vectordb"
retriever = create_retriever(CONNECTION_STRING)

rephrase_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
REPHRASE_TEMPLATE = PromptTemplate.from_template(rephrase_template)

rephrase_chain = REPHRASE_TEMPLATE | ChatOpenAI(temperature=0) | StrOutputParser()


def rerank_documents(input_data):
    query = input_data["question"]
    docs = input_data["context"]

    cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    contents = [doc.page_content for doc in docs]

    pairs = [(query, text) for text in contents]
    scores = cross_encoder.predict(pairs)

    scored_docs = zip(scores, docs)
    sorted_docs = sorted(scored_docs, key=lambda x: x[0], reverse=True)
    return [doc for _, doc in sorted_docs]


template = """Answer the question based only on the following context:
{context}
If you can´t answer the question with the context, just answer: "I am sorry, I am not allowed to answer about this topic."

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
model = ChatOpenAI()

rerank_chain = RunnablePassthrough.assign(context=RunnableLambda(rerank_documents))
model_chain = prompt | model | StrOutputParser()

rag_chain = RunnableParallel({"context": retriever, "question": RunnablePassthrough()})

full_chain = rephrase_chain | rag_chain | rerank_chain | model_chain


template = """Based on the table schema below, write a SQL query that would answer the user's question:
{schema}

Question: {question}
SQL Query:"""
prompt = ChatPromptTemplate.from_template(template)


CONNECTION_STRING = "postgresql+psycopg2://admin:admin@127.0.0.1:5432/vectordb"
db = SQLDatabase.from_uri(CONNECTION_STRING)


from sqlalchemy import create_engine, inspect
from tabulate import tabulate


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

config_dir = os.path.join(parent_dir, "config")

config = RailsConfig.from_path(config_dir)
guardrails = RunnableRails(config, input_key="question", output_key="answer")


def route(info):
    if "database" in info["topic"].lower():
        return sql_chain
    elif "chat" in info["topic"].lower():
        return guardrails | full_chain
    else:
        return "I am sorry, I am not allowed to answer about this topic."


full_chain_with_classification = RunnableParallel(
    {
        "topic": classification_chain,
        "question": lambda x: x["question"],
        "chat_history": lambda x: x["chat_history"],
    }
) | RunnableLambda(route)


evaluator = RAGASEvaluator(
    questions, ground_truth, full_chain_with_classification, retriever, use_history=True
)


evaluator.create_dataset()
evaluation_results = evaluator.evaluate()
evaluator.print_evaluation(
    save_csv=True, sep=";", decimal=",", file_name="ragas_evaluation_basics.csv"
)
