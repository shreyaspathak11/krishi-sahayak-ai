"""
Batch KCC Data Ingestion for Krishi Sahayak AI
Fetches farmer queries in batches and adds them to the main vector store one by one.
"""

import os
import json
import requests
import time
import sys
from datetime import datetime

from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

# Import config to check which vector store to use
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.config import Config


CACHE_DIR = "data/kcc_cache"
VECTOR_STORE_DIR = "vector_store"

def get_embeddings():
    """Get appropriate embeddings based on vector store configuration"""
    if Config.USE_REMOTE_VECTOR_STORE and Config.PINECONE_API_KEY:
        return HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5")
    else:
        return HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2") 

def fetch_kcc_data_batch(limit=1000, offset=0):
    """Fetch KCC data from government API with offset for pagination"""
    params = {"api-key": Config.GOV_IN_API_KEY, "format": "json", "limit": limit, "offset": offset}
    
    try:
        response = requests.get(Config.KCC_API_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json().get("records", [])
    except Exception as e:
        return []

def format_kcc_record(record):
    """Convert KCC record to text for vector store"""
    state = record.get('StateName', 'Unknown')
    query = record.get('QueryText', 'No query')
    answer = record.get('KccAns', 'No answer')
    crop = record.get('Crop', 'General')
    
    return f"""Farmer Query from {state}:
{query}

Expert Answer:
{answer}

Crop: {crop}
Source: Kisan Call Centre"""

def add_batch_to_vector_store(records, batch_num, embeddings=None):
    """Add a batch of KCC records to the vector store (Pinecone or ChromaDB)"""
    
    if not records:
        return False
        
    documents = []
    for record in records:
        text = format_kcc_record(record)
        metadata = {
            "source": "KCC",
            "state": record.get('StateName', 'Unknown'),
            "crop": record.get('Crop', 'General'),
            "batch": batch_num
        }
        documents.append(Document(page_content=text, metadata=metadata))
    
    if not embeddings:
        embeddings = get_embeddings()
    
    try:
        if Config.USE_REMOTE_VECTOR_STORE and Config.PINECONE_API_KEY:
            # Use Pinecone
            pc = Pinecone(api_key=Config.PINECONE_API_KEY)
            
            # Check if index exists, create if it doesn't
            existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
            if Config.PINECONE_INDEX_NAME not in existing_indexes:
                pc.create_index(
                    name=Config.PINECONE_INDEX_NAME,
                    dimension=Config.PINECONE_DIMENSIONS,
                    metric="cosine",
                    spec={
                        "serverless": {
                            "cloud": "aws",
                            "region": Config.PINECONE_ENVIRONMENT
                        }
                    }
                )
            
            index = pc.Index(Config.PINECONE_INDEX_NAME)
            vectorstore = PineconeVectorStore(index=index, embedding=embeddings)
            vectorstore.add_documents(documents)
        else:
            # Use local ChromaDB
            if os.path.exists(VECTOR_STORE_DIR):
                vectorstore = Chroma(persist_directory=VECTOR_STORE_DIR, embedding_function=embeddings)
                vectorstore.add_documents(documents)
            else:
                vectorstore = Chroma.from_documents(documents, embeddings, persist_directory=VECTOR_STORE_DIR)
        
        return True
    except Exception as e:
        return False

def save_batch_cache(records, batch_num, timestamp):
    """Save batch data to cache file"""
    if not records:
        return None
        
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_filename = f"kcc_batch_{batch_num:03d}_{timestamp}.json"
    cache_path = os.path.join(CACHE_DIR, cache_filename)
    
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        return cache_path
    except Exception as e:
        return None

def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_size = 1000
    batch_num = 1
    offset = 0
    total_processed = 0
    failed_batches = []
    
    # Load embeddings once to reuse across batches
    embeddings = get_embeddings()
    
    while True:
        # Fetch batch data
        records = fetch_kcc_data_batch(limit=batch_size, offset=offset)
        
        if not records:
            break
            
        actual_count = len(records)
        
        # Save batch to cache
        cache_path = save_batch_cache(records, batch_num, timestamp)
        
        # Add batch to vector store
        success = add_batch_to_vector_store(records, batch_num, embeddings)
        
        if success:
            total_processed += actual_count
        else:
            failed_batches.append(batch_num)
        
        # Check if we got fewer records than requested (likely the last batch)
        if actual_count < batch_size:
            break
            
        # Prepare for next batch
        batch_num += 1
        offset += batch_size
        
        # Add a small delay to be respectful to the API
        time.sleep(2)


if __name__ == "__main__":
    main()
