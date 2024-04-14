from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import redis
import uuid
import json
from fastapi.middleware.cors import CORSMiddleware
from dotenv import find_dotenv, load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
import logging
from custom_guardrails import final_chain
import nest_asyncio

nest_asyncio.apply()

load_dotenv(find_dotenv())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_user = os.getenv("DB_USER", "user")
db_password = os.getenv("DB_PASSWORD", "password")
db_host = os.getenv("DB_HOST", "127.0.0.1")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME", "restaurant")


redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=os.getenv("REDIS_PORT", 6379),
    db=os.getenv("REDIS_DB", 0),
    password=os.getenv("REDIS_PASSWORD", None),
)


class Question(BaseModel):
    question: str


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

    chain_input = {
        "question": question.question,
        "chat_history": chat_history,
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
