# Advanced RAG with Langchain - Udemy Course

Welcome to the course on **Advanced RAG with Langchain**. This repository contains Jupyter notebooks, helper scripts, app files, and Docker resources designed to guide you through advanced Retrieval-Augmented Generation (RAG) techniques with Langchain.

## Course Content

### Jupyter Notebooks

Below is a list of Jupyter notebooks included in this course:

- `00_LCEL_Deepdive.ipynb`: Intro to LangChain Expression Language with custom LCEL which explains the pipe operator.
- `01_LangChain_Expression_Language.ipynb`: Introduction to LangChain's expression language with real world examples.
- `02_LCEL_ChatWithHistory.ipynb`: Implementing chat with history in LangChain.
- `03_IndexingAPI.ipynb`: Exploring LangChain's indexing API.
- `04_Ragas.ipynb`: An introduction to RAG pipelines.
- `05_BetterChunking.ipynb`: Techniques for improving text chunking.
- `06_BetterEmbeddings.ipynb`: Best practices for creating embeddings.
- `07_BetterQueries.ipynb`: Improving query formulation in RAG.
- `08_BetterRetriever.ipynb`: Techniques for enhancing retriever performance.
- `08_RerankingCrossEncoder.ipynb`: Using a cross-encoder for re-ranking.
- `09_RAG_with_Agents.ipynb`: Basics of routing in LangChain using agents.
- `10_Routing.ipynb`: Routing with database queries.
- `11_RoutingAndDBQueries.ipynb`: Advanced routing with database queries.
- `12_ToolCalling.ipynb`: Implementing external tool calling in LangChain.
- `13_NemoGuardRails.ipynb`: Implementing guardrails with NeMo.
- `14_GuardrailswithHistory.ipynb`: Using guardrails with chat history.
- `15_Langfuse.ipynb`: An introduction to Langfuse integration with LangChain.

### Helper Scripts

These scripts are designed to assist with data ingestion, inspection, and cleanup:

- `clear_tables.py`: Clears database tables for a fresh start.
- `ingest_data.py`: Ingests data into the database.
- `inspect_db.py`: Inspects the database structure and content.

### Full-Stack App and Docker

The `app` folder contains a full-stack chatbot application using React for the frontend and FastAPI for the backend. It has both basic and advanced backend implementations.

The app folder includes a `docker-compose.yml` file to start all required services in a Docker environment. To run the full-stack app with Docker, follow these steps:

1. Navigate to the `app` folder.
2. Run `docker-compose up` to start all services.
3. Access the chatbot via your browser at the specified address.

### Ragas Folder

The `ragas` folder contains files for evaluating RAG pipelines, providing tools to assess their effectiveness and accuracy.

## License

This course repository is licensed under a restricted license. You are allowed to use the content for learning and personal projects but are prohibited from modifying, chaining, or redistributing it in any form. For detailed terms, refer to the `LICENSE` file in the root directory of the repository.

## How to Use

1. Clone this repository to your local machine.
2. Open the Jupyter notebooks in your preferred environment and follow along with the course.
3. Use the helper scripts to manage data and database tables.
4. Start the full-stack app with Docker from the `app` folder.
5. Experiment with the RAG pipelines in the `ragas` folder to understand their evaluation process.

Happy learning!
