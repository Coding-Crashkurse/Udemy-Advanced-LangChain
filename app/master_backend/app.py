import json
import logging
import os
import uuid
from contextlib import asynccontextmanager

import nest_asyncio
import redis
from custom_guardrails import full_chain_with_classification
from data_init import DataIngestionManager
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langfuse.callback import CallbackHandler
from pydantic import BaseModel

langfuse_handler = CallbackHandler()
langfuse_handler.auth_check()

nest_asyncio.apply()

load_dotenv(find_dotenv())


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=os.getenv("REDIS_PORT", 6379),
    db=os.getenv("REDIS_DB", 0),
    password=os.getenv("REDIS_PASSWORD", None),
)


class Question(BaseModel):
    question: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    data_manager = DataIngestionManager()
    data_manager.ingest_vector_data(["./data/restaurant.txt", "./data/founder.txt"])
    data_manager.ingest_tabular_data("./data/food.txt")
    data_manager.query_products()
    yield


app = FastAPI(lifespan=lifespan)
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

    response = full_chain_with_classification.invoke(
        chain_input, config={"callbacks": [langfuse_handler]}
    )

    chat_history.append({"role": "human", "content": question.question})
    chat_history.append({"role": "assistant", "content": response})

    redis_client.set(conversation_id, json.dumps(chat_history))
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
