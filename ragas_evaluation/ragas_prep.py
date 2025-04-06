import os

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    context_precision,
    context_recall,
    context_relevancy,
    faithfulness,
)
from tqdm import tqdm

questions = [
    "Where is Chef Amico's restaurant located?",
    "What makes Chef Amico's restaurant more than a mere eatery?",
    "What greets patrons as they enter Chef Amico's restaurant?",
    "What do the walls of Chef Amico's restaurant feature?",
    "What fills the air in Chef Amico's restaurant besides the aromas of food?",
    "Who founded Chef Amico's restaurant?",
    "What is unique about Chef Amico's cooking style?",
    "What does Chef Amico's restaurant aim to capture in its dishes?",
    "What is Chef Amico's approach to hospitality?",
    "What impression does Chef Amico aim to leave on his patrons?",
    "Who is the renowned food critic that visited Chef Amico's restaurant?",
    "What was Elena Rossi's mission when visiting Chef Amico's restaurant?",
    "Who greeted Elena Rossi upon her arrival at Chef Amico's restaurant?",
    "What was the first course served to Elena Rossi?",
    "What did the Risotto al Nero di Seppia represent to Elena Rossi?",
    "What was the final dish served to Elena Rossi during her visit?",
    "How did Elena Rossi describe her experience at Chef Amico's restaurant?",
    "What did Elena Rossi realize about Chef Amico's restaurant while eating Cannoli?",
    "What did Elena Rossi understand about the essence of Chef Amico's restaurant?",
    "How did Elena Rossi leave Chef Amico's restaurant?",
    # Customer-oriented questions about the menu
    "Which dish on the menu is the most expensive?",
    "What's the least expensive item you offer?",
    "How many main dishes do you have?",
    "How many categories of dishes do you offer?",
    "What drinks do you serve?",
    "What desserts do you have on the menu?",
    "Which appetizers can I choose from?",
    "What is the average price of your dishes?",
    # Off-topic questions
    "Who is your creator?",
    "What is your opinion on politics?",
    "Can you provide personal advice?",
    "What is your stance on religious topics?",
    "Can you predict lottery numbers?",
    "How do you feel about artificial intelligence taking jobs?",
    "What is your favorite movie or book?",
    "Can you give me medical advice?",
    "Can you tell me the meaning of life?",
    "Can you recommend investment strategies?",
]
# Updated ground truth
ground_truth = [
    "Palermo, Sicily",
    "A slice of Sicilian heaven",
    "Aromas of garlic and olive oil",
    "Photos of Amico's travels and family recipes",
    "Chatter and laughter of patrons",
    "Chef Amico",
    "Reflects his journey through Italian cuisine and commitment to Sicilian flavors",
    "Stories, traditions, and heart",
    "Hospitality as an art form",
    "Every dish is a journey through Sicily",
    "Elena Rossi",
    "To uncover the secret behind the restaurant's growing fame",
    "Amico himself",
    "Caponata",
    "Sicily's love affair with the sea",
    "Cannoli",
    "It's about the stories, traditions, and heart poured into every dish",
    "That Chef Amico's restaurant wasn't just about the food; it was about passion and love in each dish",
    "Every dish told a story and reflected the soul of Chef Amico's journey through Sicily",
    "Knowing her review would sing praises not just of the food but of the soul of the place",
    # Ground truth for customer-oriented questions
    "The most expensive dish is Frutti di Mare, priced at $22.",
    "The least expensive item on the menu is Espresso, priced at $4.",
    "We offer 17 different main dishes.",
    "We offer six categories: Main Dishes, Appetizers, Salads, Desserts, Drinks, and Side Dishes.",
    "Our drinks include Prosecco, Chianti, Espresso, Negroni, Aperol Spritz, Grappa, Sangiovese, Italian Soda, Americano, and Limoncello.",
    "We offer a variety of desserts, including Tiramisu, Gelato, Cannoli, Affogato, Panna Cotta, Biscotti, Zabaglione, and Panettone.",
    "Our appetizers include Bruschetta, Calamari, Arancini, Carpaccio, Crostini, and Bresaola.",
    "The average price of our dishes is about $11.52.",
    # Ground truth for off-topic questions
    "I am sorry, I am not allowed to answer about this topic.",
    "I am sorry, I am not allowed to answer about this topic.",
    "I am sorry, I am not allowed to answer about this topic.",
    "I am sorry, I am not allowed to answer about this topic.",
    "I am sorry, I am not allowed to answer about this topic.",
    "I am sorry, I am not allowed to answer about this topic.",
    "I am sorry, I am not allowed to answer about this topic.",
    "I am sorry, I am not allowed to answer about this topic.",
    "I am sorry, I am not allowed to answer about this topic.",
    "I am sorry, I am not allowed to answer about this topic.",
]


class RAGASEvaluator:
    def __init__(
        self,
        questions,
        ground_truth,
        rag_chain,
        retriever,
        metrics=None,
        chat_history=None,
        use_history=False,
    ):
        self.questions = questions
        self.ground_truth = ground_truth
        self.rag_chain = rag_chain
        self.retriever = retriever
        self.chat_history = chat_history if chat_history is not None else []
        self.use_history = use_history
        self.metrics = (
            metrics
            if metrics is not None
            else [
                context_relevancy,
                context_precision,
                context_recall,
                faithfulness,
                answer_relevancy,
            ]
        )
        self.data = {
            "question": [],
            "answer": [],
            "contexts": [],
            "ground_truth": ground_truth,
        }
        self.dataset = None

    def create_dataset(self):
        for query in tqdm(self.questions, desc="Creating dataset..."):
            self.data["question"].append(query)

            if self.use_history:
                chain_input = {"question": query, "chat_history": self.chat_history}
                answer = self.rag_chain.invoke(chain_input)
            else:
                answer = self.rag_chain.invoke(query)

            self.data["answer"].append(answer)

            contexts = [
                doc.page_content for doc in self.retriever.invoke(query)
            ]
            self.data["contexts"].append(contexts)

        self.dataset = Dataset.from_dict(self.data)

    def print_evaluation(
        self,
        save_csv=True,
        sep=",",
        file_name="ragas_evaluation.csv",
        decimal=".",
    ):
        if hasattr(self, "result"):
            df = self.result.to_pandas()

            print("RAGAS Evaluation Results:")
            print(df)
            if save_csv:
                output_path = os.path.join(os.getcwd(), file_name)
                df.to_csv(output_path, index=False, sep=sep, decimal=decimal)
                print(
                    f"Results saved to {output_path} with separator '{sep}' and decimal '{decimal}'"
                )
        else:
            print("Please run the evaluation before printing the results.")
