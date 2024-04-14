from retrieval import full_chain

from nemoguardrails import RailsConfig
from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails
from langchain_core.runnables import RunnableLambda
from langchain_openai.chat_models import ChatOpenAI

config = RailsConfig.from_path("./config")
guardrails = RunnableRails(config, input_key="question")


# def input_chain(input):
#     print("Input Guardrails: ", input)


# def debug_chain(input):
#     print("Output Guardrails: ", input)
#     return input


final_chain = guardrails | full_chain

if __name__ == "__main__":

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
