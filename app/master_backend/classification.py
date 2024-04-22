from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI


classification_template = PromptTemplate.from_template(
    """You are good at classifying a question.
    Given the user question below, classify it as either being about `Database`, `Chat` or 'Offtopic'.

    <If the question is about products of the restaurant OR ordering food, drinks and anything related to the products of a restaurant, classify the question as 'Database'>
    <If the question is about restaurant related topics like opening hours and similar topics, classify it as 'Chat'>
    <If the question is about whether, football or anything not related to the restaurant or
    products, classify the question as 'offtopic'>

    <question>
    {question}
    </question>

    Classification:"""
)

classification_chain = classification_template | ChatOpenAI() | StrOutputParser()
