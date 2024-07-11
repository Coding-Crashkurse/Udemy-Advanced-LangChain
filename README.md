# Advanced RAG with Langchain - Udemy Course

Welcome to the course on **Advanced RAG with Langchain**. This repository contains Jupyter notebooks, helper scripts, app files, and Docker resources designed to guide you through advanced Retrieval-Augmented Generation (RAG) techniques with Langchain.

## Course Content

### Jupyter Notebooks

Below is a list of Jupyter notebooks included in this course:

- `00_LCEL_Deepdive.ipynb`: Intro to LangChain Expression Language with custom LCEL which explains the pipe operator.
- `01_LCEL_And_Runnables.ipynb`: Introduction to LangChain's expression language with real-world examples.
- `02_LCEL_ChatWithHistory.ipynb`: Implementing chat with history in LangChain.
- `03_IndexingAPI.ipynb`: Exploring LangChain's indexing API.
- `04_Ragas.ipynb`: Evaluate RAG Pipelines with the RAGAS Framework.
- `05_BetterChunking.ipynb`: Techniques for improving text chunking.
- `06_BetterEmbeddings.ipynb`: Best practices for creating embeddings.
- `07_BetterQueries.ipynb`: Improving query formulation in RAG.
- `08_BetterRetriever.ipynb`: Techniques for enhancing retriever performance.
- `09_RAG_with_Agents.ipynb`: Implementing RAG with agents.
- `10_RerankingCrossEncoder.ipynb`: Using a cross-encoder for re-ranking.
- `11_Routing.ipynb`: Basics of routing in LangChain using agents.
- `12_RoutingAndDBQueries.ipynb`: Advanced routing with database queries.
- `13_NemoGuardRails.ipynb`: Implementing guardrails with NeMo Guardrails.
- `14_GuardrailswithHistory.ipynb`: Using guardrails with chat history.
- `15_Langfuse.ipynb`: An introduction to Langfuse integration with LangChain for tracing.
- `16_ToolCalling.ipynb`: Implementing external tool calling in LangChain.

### Helper Scripts

These scripts are designed to assist with data ingestion, inspection, and cleanup:

- `clear_tables.py`: Clears database tables for a fresh start.
- `ingest_data.py`: Ingests data into the database.
- `inspect_db.py`: Inspects the database structure and content.
- `create_read_only_user.py`: Creates a read-only user in the database.
- `fake_api.py`: Contains a fake API for testing purposes.

### Full-Stack App and Docker

The `app` folder contains a full-stack chatbot application using React for the frontend and FastAPI for the backend. It has both basic and advanced backend implementations.

The `app` folder includes a `docker-compose.yaml` file to start all required services in a Docker environment. To run the full-stack app with Docker, follow these steps:

1. Navigate to the `app` folder.
2. Run `docker-compose up` to start all services.
3. Access the chatbot via your browser at the specified address.

### Data Folder

The `data` folder contains datasets required for the exercises and examples provided in the notebooks.

### Questions and Answers Folder

The `questions_answers` folder contains a set of Q&A pairs to be used with the RAG pipelines.

## License

This course repository is licensed under a restricted license. You are allowed to use the content for learning and personal projects but are prohibited from modifying, chaining, or redistributing it in any form. For detailed terms, refer to the `LICENSE.md` file in the root directory of the repository.

## How to Use

1. Clone this repository to your local machine.
2. Open the Jupyter notebooks in your preferred environment and follow along with the course.
3. Use the helper scripts to manage data and database tables.
4. Start the full-stack app with Docker from the `app` folder.
5. Experiment with the RAG pipelines in the notebooks to understand their evaluation process.

Happy learning!
