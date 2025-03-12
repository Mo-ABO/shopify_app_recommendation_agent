from langchain import LLMChain, PromptTemplate
from langchain.chains import SequentialChain
# from langchain.llms import HuggingFaceHub
from langchain.llms import OpenAI
# from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings import OpenAIEmbeddings
from chains.retrievecontext import RetrievalChain 
import json
from config import settings as s
import os

from langchain.chains import SequentialChain

if not os.environ["OPENAI_API_KEY"]:
    os.environ["OPENAI_API_KEY"] = s.openai_api_key

# summarization chain
def generate_summarization_chain():
    summarization_template = """You are a summarization assistant.
    Below is a collection of Shopify app descriptions:
    {raw_context}

    Please generate a concise summary that captures the key features and benefits.
    Summary:"""

    summarize_prompt = PromptTemplate(input_variables=["raw_context"], template=summarization_template)
    return LLMChain(llm=OpenAI(temperature=0.4), prompt=summarize_prompt, output_key="summary")

# recommendation chain
def generate_recommendation_chain():
    recommendation_template = """You are a multilingual knowledgeable Shopify App Recommendation Agent. Given the context of various Shopify apps and a specific user query, generate a recommendation that is both concise and informative. 
    Your answer must be in the following JSON format without any extra commentary.

    Example 1:
    {{
    "app_name": "InventoryPro",
    "app_store_link": "https://apps.shopify.com/inventorypro",
    "app_description": "InventoryPro is an affordable inventory management solution tailored for small businesses.",
    "key_reasons": ["Low cost", "User-friendly interface"]
    }}

    Example 2:
    {{
    "app_name": "StockManager",
    "app_store_link": "https://apps.shopify.com/stockmanager",
    "app_description": "StockManager helps small businesses efficiently track inventory with real-time updates.",
    "key_reasons": ["Real-time tracking", "Easy setup"]
    }}

    Now, based on the context below and the user query provided, generate your recommendation.
    If the provided summarized context is empty (i.e., no relevant app descriptions were found), only output an empty JSON object like: {{}}, and make sure to only send it without any furthe thing.

    Summarized Context:
    {summary}

    User Query:
    {query}

    Your JSON response:
    """

    recommendation_prompt = PromptTemplate(input_variables=["summary", "query"], template=recommendation_template)
    return LLMChain(llm=OpenAI(temperature=0.7), prompt=recommendation_prompt, output_key="recommendation")

def build_overall_chain(db_path: str) -> SequentialChain:
    retrieval_chain = RetrievalChain(db_path=db_path, collection_name="shopify_apps", k=3)
    summarization_chain = generate_summarization_chain()
    recommendation_chain = generate_recommendation_chain()

    overall_chain = SequentialChain(
        chains=[retrieval_chain, summarization_chain, recommendation_chain],
        input_variables=["query"],
        output_variables=["raw_context", "summary", "recommendation"]
    )
    return overall_chain

def get_recommendation(query: str, db_path: str) -> dict:
    overall_chain = build_overall_chain(db_path)
    result = overall_chain({"query": query})
    print("Overall chain output:", result)
    try:
        # final recommendation is in result["recommendation"]
        recommendation_json = json.loads(result["recommendation"].strip())
    except Exception as e:
        recommendation_json = {
            "app_name": "Simulated App",
            "app_store_link": "https://apps.shopify.com/simulated-app",
            "app_description": result.get("recommendation", "").strip(),
            "key_reasons": ["Reason 1", "Reason 2"]
        }
    return recommendation_json