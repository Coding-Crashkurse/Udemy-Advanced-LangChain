from pydantic import BaseModel, Field
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, Generic, Sequence, TypeVar, Iterator
import logging

from langchain.schema import Document
from langchain_core.stores import BaseStore
from langchain_community.vectorstores.pgvector import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers import ParentDocumentRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter

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

    text_splitter = RecursiveCharacterTextSplitter()
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=docstore,
        child_splitter=text_splitter,
    )

    return retriever
