"""
Text Extraction Lambda Handler

Extracts text from documents using Amazon Textract.
Triggered by S3 upload events or API requests.
"""
import json
import boto3
import os
import urllib.parse

s3 = boto3.client('s3')
BUCKET_NAME = os.environ.get('DOCUMENTS_BUCKET', 'documind-documents')


def lambda_handler(event, context):
    """
    Handle text extraction requests.
    
    Can be triggered by:
    1. S3 event (automatic extraction on upload)
    2. API Gateway (manual extraction request)
    """
    try:
        # Check if this is an S3 event
        if 'Records' in event:
            return handle_s3_event(event)
        
        # Otherwise, it's an API request
        return handle_api_request(event)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {'error': 'Internal server error', 'message': str(e)})


def handle_s3_event(event):
    """Process S3 upload event and extract text."""
    from utils.textract import extract_text_from_s3
    from utils.dynamodb import get_document, store_extracted_text, update_document_status
    
    for record in event.get('Records', []):
        bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'])
        
        print(f"Processing document: s3://{bucket}/{key}")
        
        # Find document ID from key
        # Expected format: documents/{userId}/{date}/{documentId}/{filename}
        parts = key.split('/')
        if len(parts) >= 4:
            document_id = parts[3]
        else:
            print(f"Could not extract document ID from key: {key}")
            continue
        
        # Update status to processing
        update_document_status(document_id, 'PROCESSING')
        
        try:
            # Extract text using Textract
            result = extract_text_from_s3(bucket, key)
            
            # Store extracted text
            store_extracted_text(
                document_id=document_id,
                text=result['text'],
                word_count=result['word_count'],
                confidence=result['confidence']
            )
            
            print(f"Successfully extracted {result['word_count']} words from document {document_id}")
            
        except Exception as e:
            print(f"Error extracting text from {document_id}: {str(e)}")
            update_document_status(document_id, 'FAILED', {'errorMessage': str(e)})
    
    return {'statusCode': 200, 'body': 'Processing complete'}


def handle_api_request(event):
    """Handle manual extraction request via API."""
    from utils.textract import extract_text_from_s3
    from utils.dynamodb import get_document, store_extracted_text, update_document_status
    
    # Get document ID from path parameters
    path_params = event.get('pathParameters', {}) or {}
    document_id = path_params.get('documentId')
    
    if not document_id:
        return response(400, {'error': 'documentId is required'})
    
    # Get document from database
    document = get_document(document_id)
    
    if not document:
        return response(404, {'error': 'Document not found'})
    
    # Check if already extracted
    if document.get('status') == 'EXTRACTED' and document.get('extractedText'):
        return response(200, {
            'documentId': document_id,
            'text': document['extractedText'],
            'wordCount': document.get('wordCount', 0),
            'confidence': float(document.get('ocrConfidence', 0)),
            'cached': True
        })
    
    # Update status
    update_document_status(document_id, 'PROCESSING')
    
    try:
        # Extract text
        s3_key = document['s3Key']
        result = extract_text_from_s3(BUCKET_NAME, s3_key)
        
        # Store results
        store_extracted_text(
            document_id=document_id,
            text=result['text'],
            word_count=result['word_count'],
            confidence=result['confidence']
        )
        
        return response(200, {
            'documentId': document_id,
            'text': result['text'],
            'wordCount': result['word_count'],
            'confidence': result['confidence'],
            'cached': False
        })
        
    except Exception as e:
        update_document_status(document_id, 'FAILED', {'errorMessage': str(e)})
        return response(500, {'error': 'Text extraction failed', 'message': str(e)})


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
