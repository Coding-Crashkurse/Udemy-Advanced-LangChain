from retrieval import full_chain
from nemoguardrails import RailsConfig
from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails
from langchain_core.runnables import RunnableLambda, RunnableParallel
from classification import classification_chain
from sql_queries import sql_chain


config = RailsConfig.from_path("./config")
guardrails = RunnableRails(config, input_key="question")


def route(info):
    if "database" in info["topic"].lower():
        return sql_chain
    elif "chat" in info["topic"].lower():
        return full_chain
    else:
        return "I am sorry, I am not allowed to answer about this topic."


full_chain_with_classification = RunnableParallel(
    {
        "topic": classification_chain,
        "question": lambda x: x["question"],
        "chat_history": lambda x: x["chat_history"],
    }
) | RunnableLambda(route)

if __name__ == "__main__":

    print(
        full_chain_with_classification.invoke(
            {
                "question": "What makes Chef Amico's restaurant more than a mere eatery?",
                "chat_history": [],
            }
        )
    )
