from celery import Celery
from opensearchpy import OpenSearch
import os
from app.utils.opensearch_client import index_document

# Initialize Celery
celery = Celery('tasks', broker='redis://localhost:6379')



# Define Celery Task for Indexing
@celery.task
def index_document_async(index_name, doc_id, document_data):
    try:
        index_document(index=index_name, id=doc_id, body=document_data)
        print(f"✅ Indexed document {doc_id} successfully!")
    except Exception as e:
        print(f"❌ Error indexing document {doc_id}: {e}")
