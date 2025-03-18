from app.utils.opensearch_client import client

try:
    print(client.info())
except Exception as e:
    print("Error connecting to OpenSearch:", str(e))
