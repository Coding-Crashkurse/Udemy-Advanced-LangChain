from retrieval import full_chain
from nemoguardrails import RailsConfig
from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails
from langchain_core.runnables import RunnableLambda, RunnableParallel
from classification import classification_chain
from sql_queries import sql_chain
from langchain_openai.chat_models import ChatOpenAI


config = RailsConfig.from_path("./config")
guardrails = RunnableRails(config, input_key="question")


def debug_route(input):
    print("INPUT", input)
    return input


def get_chat(input):
    return []


def route(info):
    if "database" in info["topic"].lower():
        return RunnableLambda(debug_route) | sql_chain
    elif "chat" in info["topic"].lower():
        return RunnableLambda(debug_route) | guardrails | full_chain
    else:
        return "I am sorry, I am not allowed to answer about this topic."


full_chain_with_classification = RunnableParallel(
    {
        "topic": classification_chain,
        "question": lambda x: x["question"],
        "chat_history": lambda x: x["chat_history"],
    }
) | RunnableLambda(route)


final_chain = guardrails | full_chain

if __name__ == "__main__":

    # print(
    #     full_chain_with_classification.invoke(
    #         {"question": "What food do you offer?", "chat_history": []}
    #     )
    # )

    print(
        full_chain.invoke(
            {
                "question": "What food do you offer?",
                "chat_history": [
                    {"role": "user", "content": "What does the dog like to eat?"},
                    {"role": "assistant", "content": "Thuna!"},
                ],
            }
        )
    )
