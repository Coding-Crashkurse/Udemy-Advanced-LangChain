from retrieval import full_chain

from nemoguardrails import RailsConfig
from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails

config = RailsConfig.from_path("../config")
guardrails = RunnableRails(config)

final_chain = full_chain | guardrails
