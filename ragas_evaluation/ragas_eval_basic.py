import os

from dotenv import load_dotenv
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.directory import DirectoryLoader
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from ragas_prep import RAGASEvaluator, ground_truth, questions

parent_dir = os.path.dirname(os.getcwd())
app_dir = os.path.join(parent_dir, "app")
env_path = os.path.join(app_dir, ".env")
load_dotenv(env_path)

data_folder = os.path.join(parent_dir, "data")

loader = DirectoryLoader(data_folder, glob="**/*.txt")
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=350,
    chunk_overlap=20,
    length_function=len,
    is_separator_regex=False,
)
chunks = text_splitter.split_documents(docs)


template = """Answer the question based on the following context.
{context}
If you can´t answer the question based on the context, just say: "I am sorry, I am not allowed to answer about this topic."


Question: {question}
"""

prompt = PromptTemplate(template=template, input_variables=["context", "question"])

embedding = OpenAIEmbeddings()
model = ChatOpenAI()

vectorstore = Chroma.from_documents(chunks, embedding)
retriever = vectorstore.as_retriever()


rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)


evaluator = RAGASEvaluator(questions, ground_truth, rag_chain, retriever)
evaluator.create_dataset()
evaluation_results = evaluator.evaluate()
evaluator.print_evaluation(
    save_csv=True, sep=";", decimal=",", file_name="ragas_evaluation_basics.csv"
)
