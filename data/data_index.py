import pandas as pd
import chromadb
from chromadb.config import Settings
# from langchain.embeddings import HuggingFaceEmbeddings
from config import settings as s
from langchain.embeddings import OpenAIEmbeddings
import os

os.environ["OPENAI_API_KEY"] = s.openai_api_key 

def load_data(dir_path: str) -> pd.DataFrame:
    apps_df = pd.read_csv(os.path.join(dir_path,'apps.csv'))
    categories_df = pd.read_csv(os.path.join(dir_path,'categories.csv'))
    apps_cats_df = pd.read_csv(os.path.join(dir_path,'apps_categories.csv'))
    
    apps_cats_merged = pd.merge(apps_cats_df, categories_df, left_on="category_id", right_on="id", how="left")
    apps_cats_grouped = apps_cats_merged.groupby("app_id")["title"].apply(lambda x: ", ".join(x.dropna().unique())).reset_index()
    
    merged_df = pd.merge(apps_df, apps_cats_grouped, left_on="id", right_on="app_id", how="left")
    merged_df.rename(columns={"title_y": "categories"}, inplace=True)
    merged_df.rename(columns={"title_x": "title"}, inplace=True)
    merged_df["categories"] = merged_df["categories"].fillna("")
    merged_df.drop(['app_id'], axis=1)
    return merged_df

def index_data(df: pd.DataFrame, db_path: str):
    # embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    embeddings = OpenAIEmbeddings()
    
    # client = chromadb.Client(persist_directory="./database/chroma_db")
    # client = chromadb.Client(Settings(persist_directory=db_path))
    client = chromadb.PersistentClient(path = db_path)

    collection = client.get_or_create_collection(name="shopify_apps")
    
    
    document_ids = []
    documents = []
    metadatas = []
    
    for nothing, row in df.iterrows():
        doc_id = str(row['id'])
        doc_text = row['description']
        metadata = {
            "title": row['title'],
            "url": row['url'],
            "categories": row['categories']
        }
        document_ids.append(doc_id)
        documents.append(doc_text)
        metadatas.append(metadata)

    document_embeddings = embeddings.embed_documents(documents)
    
    collection.add(
        ids=document_ids,
        embeddings=document_embeddings,
        documents=documents,
        metadatas=metadatas
    )

    print(f"Data indexed successfully in {db_path} with {collection.count()} samples.")
    print("An example of stored data is:")
    print(collection.get(ids=[document_ids[0]]))

def load_document_by_id(db_path: str, collection_name: str, doc_id: str, include_fields=None):
    if include_fields is None:
        include_fields = ["embeddings", "documents", "metadatas"]
    
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name=collection_name)
    print(collection.count())
    result = collection.get(ids=[doc_id], include=include_fields)
    return result


if __name__ == "__main__":
    file_path = "./data/dataset/"
    db_path = "../chroma_db"
    df = load_data(file_path)
    index_data(df,db_path)

    document = load_document_by_id(db_path, "shopify_apps", "ee6734e5-88af-4d0f-a128-1671fed6b45c")
    print(document)