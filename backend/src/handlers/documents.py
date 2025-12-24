"""
Documents CRUD Lambda Handler

Handles listing, getting, and deleting documents.
"""
import json
import boto3
import os

s3 = boto3.client('s3')
BUCKET_NAME = os.environ.get('DOCUMENTS_BUCKET', 'documind-documents')


def lambda_handler(event, context):
    """
    Handle document CRUD operations.
    
    Routes:
    - GET /documents - List all documents for user
    - GET /documents/{documentId} - Get document details
    - DELETE /documents/{documentId} - Delete a document
    """
    try:
        http_method = event.get('httpMethod', 'GET')
        path_params = event.get('pathParameters', {}) or {}
        document_id = path_params.get('documentId')
        
        if http_method == 'GET':
            if document_id:
                return get_document_handler(event, document_id)
            else:
                return list_documents_handler(event)
        elif http_method == 'DELETE':
            return delete_document_handler(event, document_id)
        else:
            return response(405, {'error': 'Method not allowed'})
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {'error': 'Internal server error', 'message': str(e)})


def list_documents_handler(event):
    """List all documents for the current user."""
    from utils.dynamodb import get_user_documents
    
    user_id = get_user_id(event)
    
    # Get query parameters
    query_params = event.get('queryStringParameters', {}) or {}
    limit = min(int(query_params.get('limit', 50)), 100)
    
    documents = get_user_documents(user_id, limit)
    
    # Remove extracted text from list view (too large)
    for doc in documents:
        doc.pop('extractedText', None)
        doc.pop('queryHistory', None)
    
    return response(200, {
        'documents': documents,
        'count': len(documents)
    })


def get_document_handler(event, document_id):
    """Get a specific document by ID."""
    from utils.dynamodb import get_document
    
    document = get_document(document_id)
    
    if not document:
        return response(404, {'error': 'Document not found'})
    
    # Check if user owns this document
    user_id = get_user_id(event)
    if document.get('userId') != user_id and user_id != 'anonymous':
        return response(403, {'error': 'Access denied'})
    
    # Get query parameters
    query_params = event.get('queryStringParameters', {}) or {}
    include_text = query_params.get('includeText', 'false').lower() == 'true'
    include_history = query_params.get('includeHistory', 'false').lower() == 'true'
    
    # Optionally exclude large fields
    if not include_text:
        document.pop('extractedText', None)
    if not include_history:
        document.pop('queryHistory', None)
    
    # Generate download URL
    if document.get('s3Key'):
        download_url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': document['s3Key']
            },
            ExpiresIn=3600
        )
        document['downloadUrl'] = download_url
    
    return response(200, {'document': document})


def delete_document_handler(event, document_id):
    """Delete a document."""
    from utils.dynamodb import get_document, delete_document
    
    if not document_id:
        return response(400, {'error': 'documentId is required'})
    
    # Get document
    document = get_document(document_id)
    
    if not document:
        return response(404, {'error': 'Document not found'})
    
    # Check ownership
    user_id = get_user_id(event)
    if document.get('userId') != user_id and user_id != 'anonymous':
        return response(403, {'error': 'Access denied'})
    
    # Delete from S3
    if document.get('s3Key'):
        try:
            s3.delete_object(Bucket=BUCKET_NAME, Key=document['s3Key'])
        except Exception as e:
            print(f"Warning: Could not delete S3 object: {str(e)}")
    
    # Delete from DynamoDB
    delete_document(document_id)
    
    return response(200, {
        'message': 'Document deleted successfully',
        'documentId': document_id
    })


def get_user_id(event):
    """Extract user ID from request context or headers."""
    request_context = event.get('requestContext', {})
    authorizer = request_context.get('authorizer', {})
    
    if 'claims' in authorizer:
        return authorizer['claims'].get('sub', 'anonymous')
    
    headers = event.get('headers', {}) or {}
    return headers.get('X-User-Id', 'anonymous')


def response(status_code, body):
    """Generate API Gateway response."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-User-Id,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,DELETE,OPTIONS'
        },
        'body': json.dumps(body, default=str)
    }
