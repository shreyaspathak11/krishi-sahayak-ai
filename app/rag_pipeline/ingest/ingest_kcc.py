"""
KCC (Kisan Call Centre) Data Ingestion Module
Handles fetching and processing KCC data from government APIs.
"""

import os
import json
import requests
import time
from datetime import datetime
from typing import List, Optional

from langchain.schema import Document

from app.config import Config
from app.utils.logs import logger


class KCCDataIngester:
    """Handles KCC (Kisan Call Centre) data ingestion from government APIs."""
    
    def __init__(self, vectorstore=None, embeddings=None):
        self.cache_dir = "data/kcc_cache"
        self.vectorstore = vectorstore
        self.embeddings = embeddings
    
    def fetch_kcc_data_batch(self, limit: int = 1000, offset: int = 0) -> List[dict]:
        """Fetch KCC data from government API with pagination."""        
        if not hasattr(Config, 'GOV_IN_API_KEY') or not hasattr(Config, 'KCC_API_URL'):
            logger.warning("KCC API configuration missing. Skipping KCC data ingestion.")
            return []
        
        if not Config.GOV_IN_API_KEY or not Config.KCC_API_URL:
            logger.warning("KCC API configuration missing. Skipping KCC data ingestion.")
            return []
        
        params = {
            "api-key": Config.GOV_IN_API_KEY,
            "format": "json",
            "limit": limit,
            "offset": offset
        }
        
        try:
            logger.info(f"Fetching KCC records {offset + 1} to {offset + limit}")
            response = requests.get(Config.KCC_API_URL, params=params, timeout=30)
            response.raise_for_status()
            records = response.json().get("records", [])
            logger.success(f"Successfully fetched {len(records)} KCC records")
            return records
        except Exception as e:
            logger.error(f"Error fetching KCC batch at offset {offset}: {str(e)}")
            return []
    
    def format_kcc_record(self, record: dict) -> Document:
        """Convert KCC record to Document format."""
        state = record.get('StateName', 'Unknown')
        query = record.get('QueryText', 'No query')
        answer = record.get('KccAns', 'No answer')
        crop = record.get('Crop', 'General')
        
        content = f"""
            Farmer Query from {state}:
            {query}

            Expert Answer:
            {answer}

            Crop: {crop}
            Source: Kisan Call Centre
            """
        
        metadata = {
            "source": "KCC",
            "state": state,
            "crop": crop,
            "type": "farmer_query"
        }
        
        return Document(page_content=content, metadata=metadata)
    
    def save_kcc_batch_cache(self, records: List[dict], batch_num: int, timestamp: str) -> Optional[str]:
        """Save KCC batch data to cache file."""
        if not records:
            return None
        
        os.makedirs(self.cache_dir, exist_ok=True)
        cache_filename = f"kcc_batch_{batch_num:03d}_{timestamp}.json"
        cache_path = os.path.join(self.cache_dir, cache_filename)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            logger.info(f"Cached batch {batch_num} to {cache_filename}")
            return cache_path
        except Exception as e:
            logger.error(f"Error caching batch {batch_num}: {str(e)}")
            return None
    
    def ingest_kcc_data(self, max_batches: Optional[int] = None) -> bool:
        """Ingest KCC data from government API."""
        logger.section("KCC Data Ingestion")
        
        if not hasattr(Config, 'GOV_IN_API_KEY') or not hasattr(Config, 'KCC_API_URL'):
            logger.warning("KCC API configuration missing. Skipping KCC data ingestion.")
            return False
        
        if not Config.GOV_IN_API_KEY or not Config.KCC_API_URL:
            logger.warning("KCC API configuration missing. Skipping KCC data ingestion.")
            return False
        
        if not self.vectorstore:
            logger.error("Vector store not initialized for KCC data ingestion")
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_size = 1000
        batch_num = 1
        offset = 0
        total_processed = 0
        failed_batches = []
        
        logger.info("Starting KCC data ingestion from government API")
        
        while True:
            if max_batches and batch_num > max_batches:
                logger.info(f"Reached maximum batch limit: {max_batches}")
                break
            
            logger.info(f"Processing KCC batch {batch_num}")
            
            # Fetch batch data
            records = self.fetch_kcc_data_batch(limit=batch_size, offset=offset)
            
            if not records:
                logger.info("No more KCC records to fetch. Stopping.")
                break
            
            actual_count = len(records)
            
            # Save batch to cache
            self.save_kcc_batch_cache(records, batch_num, timestamp)
            
            # Convert records to documents
            try:
                documents = [self.format_kcc_record(record) for record in records]
                
                # Add to vector store
                self.vectorstore.add_documents(documents)
                
                total_processed += actual_count
                logger.success(f"Batch {batch_num} processed successfully ({actual_count} records)")
                
            except Exception as e:
                failed_batches.append(batch_num)
                logger.error(f"Batch {batch_num} failed to process: {str(e)}")
            
            logger.info(f"Progress: {total_processed} KCC records processed so far")
            
            # Check if this was the last batch
            if actual_count < batch_size:
                logger.info(f"Last batch detected ({actual_count} < {batch_size})")
                break
            
            # Prepare for next batch
            batch_num += 1
            offset += batch_size
            
            # Add delay to be respectful to the API
            time.sleep(2)
        
        # Final summary
        logger.section("KCC Ingestion Summary")
        logger.success(f"Total KCC records processed: {total_processed}")
        logger.info(f"Total batches processed: {batch_num}")
        
        if failed_batches:
            logger.warning(f"Failed batches: {failed_batches}")
            return False
        else:
            logger.success("All KCC batches processed successfully")
            return True
