from retrieval import full_chain

from nemoguardrails import RailsConfig
from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails
from langchain_core.runnables import RunnableLambda
from langchain_openai.chat_models import ChatOpenAI

config = RailsConfig.from_path("./config")
guardrails = RunnableRails(config)


def input_chain(input):
    print("Output Guardrails: ", input["question"])
    return {"input": input["question"]}


def debug_chain(input):
    print("Output Guardrails: ", input)
    return input


final_chain = RunnableLambda(input_chain) | guardrails | RunnableLambda(debug_chain)
