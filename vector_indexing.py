import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

# Import SemanticChunker (assuming it's available in your version of Langchain)
from langchain_experimental.text_splitter import SemanticChunker
from langchain.vectorstores.pgvector import PGVector
from langchain_community.document_loaders.directory import DirectoryLoader
from langchain.indexes import SQLRecordManager, index


class DocumentIndexer:
    def __init__(self, app_dir, data_dir):
        self.app_dir = app_dir
        self.data_dir = data_dir
        self.load_environment()
        # Initialize embeddings with specified model and dimensions
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large", dimensions=1536
        )
        self.connection_string = (
            "postgresql+psycopg2://admin:admin@127.0.0.1:5432/vectordb"
        )
        self.collection_name = "vectordb"

    def load_environment(self):
        env_path = os.path.join(self.app_dir, ".env")
        load_dotenv(env_path)

    def load_and_split_documents(self):
        loader = DirectoryLoader(self.data_dir, glob="**/*.txt")
        docs = loader.load()
        print(f"{len(docs)} documents loaded!")
        # Use SemanticChunker with the specified embeddings
        text_splitter = SemanticChunker(self.embeddings)
        chunks = text_splitter.split_documents(docs)
        print(f"{len(chunks)} chunks from {len(docs)} docs created!")
        return chunks

    def setup_vectorstore_and_record_manager(self):
        self.vectorstore = PGVector(
            connection_string=self.connection_string,
            embedding_function=self.embeddings,
            collection_name=self.collection_name,
        )
        namespace = f"pgvector/{self.collection_name}"
        self.record_manager = SQLRecordManager(namespace, db_url=self.connection_string)
        self.record_manager.create_schema()

    def index_chunks(self, chunks):
        index(
            chunks,
            self.record_manager,
            self.vectorstore,
            cleanup=None,
            source_id_key="source",
        )


if __name__ == "__main__":
    app_directory = os.getcwd()
    data_directory = "./data"
    document_indexer = DocumentIndexer(app_directory, data_directory)

    chunks = document_indexer.load_and_split_documents()
    document_indexer.setup_vectorstore_and_record_manager()
    document_indexer.index_chunks(chunks)
