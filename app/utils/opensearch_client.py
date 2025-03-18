from opensearchpy import OpenSearch
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

# # Load OpenSearch credentials from Heroku Config Vars (or .env for local)
# OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "localhost")
# OPENSEARCH_PORT = int(os.getenv("OPENSEARCH_PORT", "9200"))  # Convert to int
# OPENSEARCH_USER = os.getenv("OPENSEARCH_USER", "admin")
# OPENSEARCH_PASSWORD = os.getenv("OPENSEARCH_PASSWORD", "Qweasd@502505")  # Default only for local

# client = OpenSearch(
#     hosts=[{'host': OPENSEARCH_HOST, 'port': OPENSEARCH_PORT}],
#     http_auth=(OPENSEARCH_USER, OPENSEARCH_PASSWORD),
#     use_ssl=OPENSEARCH_HOST != "localhost",  # Use SSL only if NOT localhost
#     verify_certs=OPENSEARCH_HOST != "localhost"
# )

# Retrieve environment variables
OPENSEARCH_HOST = os.getenv('OPENSEARCH_HOST')
OPENSEARCH_USER = os.getenv('OPENSEARCH_USER')
OPENSEARCH_PASSWORD = os.getenv('OPENSEARCH_PASSWORD')

logging.debug(f"Connecting to OpenSearch at {OPENSEARCH_HOST} with user {OPENSEARCH_USER}")

# Initialize OpenSearch client
client = OpenSearch(
    hosts=[{'host': OPENSEARCH_HOST, 'port': 443}],
    http_auth=(OPENSEARCH_USER, OPENSEARCH_PASSWORD),
    use_ssl=True,
    verify_certs=True
)


# Example: Check if the cluster is reachable
try:
    info = client.info()
    logging.debug("OpenSearch cluster info:", info)
except Exception as e:
    logging.error("Failed to connect to OpenSearch:", e)

def create_index(index_name):
    if not client.indices.exists(index=index_name):
        client.indices.create(
            index=index_name,
            body={
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                },
                "mappings": {
                    "properties": {
                        "title": {"type": "text"},
                        "description": {"type": "text"},
                        "category": {"type": "keyword"},
                        "filename": {"type": "keyword"},
                        "download_url": {"type": "text"},
                        "content": {"type": "text"}
                    }
                }
            }
        )
        print(f"Index '{index_name}' created successfully.")


def index_document(index_name, doc_id, document_data):
    document = {
        "title": document_data["title"],
        "description": document_data["description"],
        "category": document_data["category"],
        "filename": document_data["filename"],
        "download_url": document_data["download_url"],
        "content": str(document_data["content"])  # 🔹 Ensure this is stored as plain text
    }

    response = client.index(index=index_name, id=doc_id, body=document)
    print(f"Indexed document: {response}")


def search_documents(index_name, query):
    response = client.search(
        index=index_name,
        body={
            "query": {
                "match": {
                    "content": query
                }
            }
        }
        )
    return response['hits']['hits']
