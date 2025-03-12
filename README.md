# **Shopify App Recommendation Agent**

The Shopify App Recommendation Agent is an AI-powered **REST API** designed to help find the best apps for business needs. It leverages a multi-step **Retrieval-Augmented Generation (RAG)** pipeline using **LangChain** to combine semantic search (via **Chroma**) with natural language generation (via **OpenAI**). **JWT-based** authentication secures the API endpoints.

## ** Project Structure & Architecture**

```sh
project_root/
├── app/
│   ├── __init__.py
│   └── main.py                # FastAPI application endpoints
├── chains/
│   ├── __init__.py
│   ├── langchain_agent.py     # Orchestration: retrieval, summarization, and recommendation chains
│   └── retrievecontext.py     # Custom RetrievalChain (hybrid search)
├── data/
│   ├──dataset/
│   │  ├──apps.csv             # Shopify apps dataset
│   │  ├── categories.csv      # App categories
│   │  └── apps_categories.csv # Mapping of apps to categories
│   ├── __init__.py
│   └──data_index.py           # Data processing, merging CSVs, and indexing in Chroma                    
├── auth/
│   ├── __init__.py
│   └── security.py            # JWT token creation and verification
├── tests/
│   ├── __init__.py
│   ├── test_auth.py           # Simple authorization test
│   └── test_api.py            # Automated API tests using FastAPI's TestClient
├── assets/
│   └── flow_diagram.png
├── .env                       # Environment configuration file (not committed)
├── requirements.txt           # Python dependencies
├── Dockerfile 
└── README.md                 
```

---

## **Flow Diagram**

Below is a diagram illustrating how a user query is processed by the system:

![Flow Diagram](./assets/flow_diagram.png)

---

## **Installation**

First **make sure to edit** `.env` file with apropriate `OPENAI_API_KEY` or use docker image which is uploaded in dockerhub as following.

```sh
docker pull mohammada130/spoki
sudo docker run -p 80:80 -e OPENAI_API_KEY=<PLEASE PUT YOUR OPENAI_API_KEY HERE> mohammada130/spoki
```
Also you can use the following method.
**1. Clone the Repository:**

```sh
git clone https://github.com/Mo-ABO/shopify_app_recommendation_agent.git
cd shopify_app_recommendation_agent
```

**2. Create a Virtual Environment and Activate It:**

```sh
python3 -m venv env
source env/bin/activate
```

**3. Install Dependencies:**

```sh
pip install -r requirements.txt
```
**4. Configure Environment Variables:**

Create a file named `.env` in the project root with the following content:

```sh
OPENAI_API_KEY=YourOpenAIKey
SECRET_KEY=n9L2sJ6XzQ7fJYBvWm3KpXg4TzNcRqV8HsLdPz5MfC2WyGdBhX
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DB_PATH=../chroma_db
PORT=8000
```

---
### **Data Indexing**

To process and index the data (merging app and category information), run:

```sh
python data/data_index.py
```
This script loads the CSV files, enriches the app data with category information, and indexes the resulting dataset in a persistent Chroma database located at `./chroma_db`.

--
### **Running the API**

Start the FastAPI server using Uvicorn:

```sh
uvicorn app.main:app --reload
```
Your API will be available at `http://127.0.0.1:8000`, and you can access the interactive Swagger UI at `http://127.0.0.1:8000/docs` or `http://127.0.0.1:8000/redoc`.

--
### **Testing**

You can run automated tests without starting the server using FastAPI's TestClient. From the project root run:

```sh
python tests/test_api.py
```
--
### **Technologies and Rationale**
This project is built with:

- **FastAPI**: Chosen for its asynchronous capabilities, ease of development, and robust performance.
- **LangChain**: Used to orchestrate the multi-step RAG pipeline that includes retrieval, summarization, and recommendation generation.
- **OpenAI API**: Provides advanced natural language capabilities for generating embeddings and responses.
- **Chroma**: A lightweight, Python-native vector database for semantic search.
- **JWT (PyJWT)**: Implements secure authentication for API endpoints.
- **Pandas**: Used for efficient data processing and merging CSV files.
--