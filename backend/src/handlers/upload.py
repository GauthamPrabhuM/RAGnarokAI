"""
Document Upload Lambda Handler

Handles document uploads, generates presigned URLs, and creates document records.
"""
import json
import boto3
import os
import uuid
from datetime import datetime

s3 = boto3.client('s3')
BUCKET_NAME = os.environ.get('DOCUMENTS_BUCKET', 'documind-documents')
ALLOWED_TYPES = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg', 'text/plain']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def lambda_handler(event, context):
    """
    Handle document upload requests.
    
    Supports two modes:
    1. Generate presigned URL for client-side upload
    2. Process uploaded document metadata
    """
    try:
        http_method = event.get('httpMethod', 'POST')
        
        if http_method == 'POST':
            return handle_upload_request(event)
        elif http_method == 'GET':
            return handle_get_presigned_url(event)
        else:
            return response(405, {'error': 'Method not allowed'})
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {'error': 'Internal server error', 'message': str(e)})


def handle_get_presigned_url(event):
    """Generate a presigned URL for uploading a document."""
    params = event.get('queryStringParameters', {}) or {}
    
    filename = params.get('filename')
    content_type = params.get('contentType', 'application/pdf')
    user_id = get_user_id(event)
    
    if not filename:
        return response(400, {'error': 'filename is required'})
    
    if content_type not in ALLOWED_TYPES:
        return response(400, {
            'error': f'Invalid content type. Allowed types: {ALLOWED_TYPES}'
        })
    
    # Generate unique S3 key
    document_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().strftime('%Y/%m/%d')
    s3_key = f"documents/{user_id}/{timestamp}/{document_id}/{filename}"
    
    # Generate presigned URL for upload
    presigned_url = s3.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': s3_key,
            'ContentType': content_type
        },
        ExpiresIn=3600  # 1 hour
    )
    
    return response(200, {
        'uploadUrl': presigned_url,
        'documentId': document_id,
        's3Key': s3_key,
        'expiresIn': 3600
    })


def handle_upload_request(event):
    """Process document upload notification and create record."""
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return response(400, {'error': 'Invalid JSON body'})
    
    document_id = body.get('documentId')
    s3_key = body.get('s3Key')
    filename = body.get('filename')
    content_type = body.get('contentType', 'application/pdf')
    file_size = body.get('fileSize', 0)
    user_id = get_user_id(event)
    
    if not all([document_id, s3_key, filename]):
        return response(400, {
            'error': 'documentId, s3Key, and filename are required'
        })
    
    # Verify the file exists in S3
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=s3_key)
    except s3.exceptions.ClientError:
        return response(404, {'error': 'Document not found in S3'})
    
    # Import here to avoid cold start issues
    from utils.dynamodb import create_document
    
    # Create document record
    document = create_document(
        user_id=user_id,
        filename=filename,
        s3_key=s3_key,
        content_type=content_type,
        file_size=file_size
    )
    
    return response(201, {
        'message': 'Document uploaded successfully',
        'document': document
    })


def get_user_id(event):
    """Extract user ID from request context or headers."""
    # Try to get from Cognito authorizer
    request_context = event.get('requestContext', {})
    authorizer = request_context.get('authorizer', {})
    
    if 'claims' in authorizer:
        return authorizer['claims'].get('sub', 'anonymous')
    
    # Fallback to header or anonymous
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
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        },
        'body': json.dumps(body, default=str)
    }
