from opensearchpy import OpenSearch
import os
from dotenv import load_dotenv

load_dotenv()

OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "localhost")
OPENSEARCH_PORT = os.getenv("OPENSEARCH_PORT", 9200)

client = OpenSearch(
    hosts=[{'host': OPENSEARCH_HOST, 'port': OPENSEARCH_PORT}],
    http_auth=('admin', 'Qweasd@502505'),  # default credentials
    use_ssl=False,                # since we're not using SSL locally
    verify_certs=False
)


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
