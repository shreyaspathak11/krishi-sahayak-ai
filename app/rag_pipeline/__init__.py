"""
Knowledge Base Package - Krishi Sahayak AI
"""

# Import specific functions instead of using *
try:
    from .ingest import get_embeddings as ingest_get_embeddings, get_vector_store as ingest_get_vector_store
    from .ingest_kcc_data import (
        fetch_kcc_data_batch, 
        format_kcc_record, 
        add_batch_to_vector_store,
        get_embeddings as kcc_get_embeddings
    )
    
    __all__ = [
        "ingest_get_embeddings",
        "ingest_get_vector_store", 
        "fetch_kcc_data_batch",
        "format_kcc_record",
        "add_batch_to_vector_store",
        "kcc_get_embeddings"
    ]
except ImportError as e:
    print(f"Warning: Could not import knowledge base functions: {e}")
    __all__ = []