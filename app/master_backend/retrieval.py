from store import create_retriever
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import redis
import uuid
import json
from fastapi.middleware.cors import CORSMiddleware
from dotenv import find_dotenv, load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.pgvector import PGVector
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
import logging
from sentence_transformers import CrossEncoder
from langchain_core.runnables import RunnableLambda, RunnableParallel


DATABASE_URL = "postgresql+psycopg2://admin:admin@localhost:5432/vectordb"
retriever = create_retriever(DATABASE_URL)

from langchain.prompts.prompt import PromptTemplate

rephrase_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
REPHRASE_TEMPLATE = PromptTemplate.from_template(rephrase_template)

template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
ANSWER_PROMPT = ChatPromptTemplate.from_template(template)

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

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
model = ChatOpenAI()

rerank_chain = RunnablePassthrough.assign(context=RunnableLambda(rerank_documents))
model_chain = prompt | model | StrOutputParser()

rag_chain = RunnableParallel({"context": retriever, "question": RunnablePassthrough()})

full_chain = rephrase_chain | rag_chain | rerank_chain | model_chain

if __name__ == "__main__":
    try:
        result = full_chain.invoke(
            {
                "question": "No, really?",
                "chat_history": [
                    HumanMessage(content="What does the dog like to eat?"),
                    AIMessage(content="Thuna!"),
                ],
            }
        )
        print(result)
    except:
        print("An error occurred")
