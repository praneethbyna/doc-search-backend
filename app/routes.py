from flask import Blueprint, request, jsonify, current_app, send_file, url_for
from app.utils.opensearch_client import create_index, client, index_document
from PyPDF2 import PdfReader
import os
import uuid
import redis
import json



api_bp = Blueprint('api', __name__)
INDEX_NAME = 'documents'


# connect to redis
redis_client = redis.Redis(host="host.docker.internal", port=6379, db=0, decode_responses=True)


create_index(INDEX_NAME)

@api_bp.route('/upload', methods=['POST'])
def upload_document():
    file = request.files.get('file')
    title = request.form.get('title', 'Untitled Document')
    description = request.form.get('description', '')
    category = request.form.get('category', 'General')
 
    # Edge Cases -- 
    # No file uploaded
    if not file:
        return jsonify({"message": "No file uploaded.Please select a file to upload"}), 400
    
    # Allow only PDFs
    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400
    

    # Limit file size (20MB)
    if len(file.read()) > 20 * 1024 * 1024:  # 5MB limit
        return jsonify({"error": "File size exceeds 20 MB limit."}), 400
    
    file.seek(0)  # Reset file pointer after checking size
    

    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Extract text content
    reader = PdfReader(filepath)
    content = ''
    for page in reader.pages:
        extracted_text = page.extract_text()
        if extracted_text:
            content += extracted_text

    # Ensure at least some content is extracted
    if not content.strip():
        return jsonify({"error": "PDF does not contain readable text."}), 400
    


    # Index metadata and content
    document_data = {
        "title": title,
        "description": description,
        "category": category,
        "filename": filename,
        "download_url": url_for('api.download_document', filename=filename, _external=True),
        "content": content
    }

    # Run indexing as a background task
    index_document(INDEX_NAME, filename, document_data)


    return jsonify({"message": "File uploaded and indexed successfully.", "download_url": document_data["download_url"]}), 201



@api_bp.route('/search', methods=['GET'])
def search_documents_route():
    query = request.args.get('query', '').strip()

    #Edge Cases --

    # No Query Provided
    if not query:
        return jsonify({"error": "No query provided."}), 400
    

    # Check if query result is cached
    cached_result = redis_client.get(query)
    if cached_result:
        print(f"🔹 Cache Hit: Serving results for '{query}' from Redis")
        return jsonify(json.loads(cached_result)), 200
    

    print(f"❌ Cache Miss: Fetching results from OpenSearch for '{query}'")


    response = client.search(
        index=INDEX_NAME,
        body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["content", "title", "description", "category"]
                }
            }
        }
    )

    hits = response['hits']['hits']

    if not hits:
        return jsonify({"message": "No results found"}), 200
    

    results = [{
        "title": hit["_source"]["title"],
        "description": hit["_source"]["description"],
        "category": hit["_source"]["category"],
        "filename": hit["_source"]["filename"],
        "download_url": hit["_source"]["download_url"],
        "score": hit["_score"]
    } for hit in hits]


    # Store search results in Redis for 10 minutes (600 seconds)
    redis_client.setex(query, 600, json.dumps(results))
    print(f"✅ Data Cached: Search results for '{query}' stored in Redis")


    return jsonify(results), 200





@api_bp.route('/download/<filename>', methods=['GET'])
def download_document(filename):
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    return send_file(file_path, as_attachment=True)




