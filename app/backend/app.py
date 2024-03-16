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

load_dotenv(find_dotenv())

db_user = os.getenv("DB_USER", "user")
db_password = os.getenv("DB_PASSWORD", "password")
db_host = os.getenv("DB_HOST", "127.0.0.1")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME", "restaurant")

CONNECTION_STRING = (
    f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Question(BaseModel):
    question: str


embeddings = OpenAIEmbeddings()
chat = ChatOpenAI(temperature=0)
store = PGVector(
    collection_name=db_name,
    connection_string=CONNECTION_STRING,
    embedding_function=embeddings,
)
retriever = store.as_retriever()

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

retrieval_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | ANSWER_PROMPT
    | ChatOpenAI(temperature=0)
    | StrOutputParser()
)

final_chain = rephrase_chain | retrieval_chain

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=os.getenv("REDIS_PORT", 6379),
    db=os.getenv("REDIS_DB", 0),
    password=os.getenv("REDIS_PASSWORD", None),
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/conversation/{conversation_id}")
async def conversation(conversation_id: str, question: Question):
    conversation_history_json = redis_client.get(conversation_id)
    if conversation_history_json is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    chat_history = json.loads(conversation_history_json.decode("utf-8"))

    chat_history_formatted = [
        (
            HumanMessage(content=msg["content"])
            if msg["role"] == "human"
            else AIMessage(content=msg["content"])
        )
        for msg in chat_history
    ]

    chain_input = {
        "question": question.question,
        "chat_history": chat_history_formatted,
    }
    logger.info(f"Conversation ID: {conversation_id}, Chain Input: {chain_input}")

    response = final_chain.invoke(chain_input)

    chat_history.append({"role": "human", "content": question.question})
    chat_history.append({"role": "assistant", "content": response})

    redis_client.set(conversation_id, json.dumps(chat_history))
    print(chat_history)
    return {"response": chat_history}


@app.post("/start_conversation")
async def start_conversation():
    conversation_id = str(uuid.uuid4())
    redis_client.set(conversation_id, json.dumps([]))
    return {"conversation_id": conversation_id}


@app.delete("/end_conversation/{conversation_id}")
async def end_conversation(conversation_id: str):
    if not redis_client.exists(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    redis_client.delete(conversation_id)
    return {"message": "Conversation deleted"}
