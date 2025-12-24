"""
Document Summarization Lambda Handler

Generates AI-powered summaries using Amazon Bedrock.
"""
import json
import os

BUCKET_NAME = os.environ.get('DOCUMENTS_BUCKET', 'documind-documents')


def lambda_handler(event, context):
    """
    Handle document summarization requests.
    
    Expects documentId in path parameters.
    """
    try:
        from utils.bedrock import summarize_document, extract_key_entities, generate_document_questions
        from utils.dynamodb import get_document, store_summary, update_document_status
        
        # Get document ID
        path_params = event.get('pathParameters', {}) or {}
        document_id = path_params.get('documentId')
        
        if not document_id:
            return response(400, {'error': 'documentId is required'})
        
        # Get query parameters for options
        query_params = event.get('queryStringParameters', {}) or {}
        include_entities = query_params.get('entities', 'false').lower() == 'true'
        include_questions = query_params.get('questions', 'false').lower() == 'true'
        max_length = int(query_params.get('maxLength', 500))
        
        # Get document
        document = get_document(document_id)
        
        if not document:
            return response(404, {'error': 'Document not found'})
        
        # Check if text has been extracted
        extracted_text = document.get('extractedText')
        
        if not extracted_text:
            return response(400, {
                'error': 'Document text has not been extracted yet',
                'hint': 'Call the extract endpoint first'
            })
        
        # Check if we already have a summary (caching)
        if document.get('summary') and not include_entities and not include_questions:
            return response(200, {
                'documentId': document_id,
                'summary': document['summary'],
                'cached': True
            })
        
        # Generate summary using Bedrock
        summary = summarize_document(extracted_text, max_length)
        
        # Store summary
        store_summary(document_id, summary)
        
        result = {
            'documentId': document_id,
            'summary': summary,
            'wordCount': document.get('wordCount', 0),
            'cached': False
        }
        
        # Optionally extract entities
        if include_entities:
            entities = extract_key_entities(extracted_text)
            result['entities'] = entities
        
        # Optionally generate suggested questions
        if include_questions:
            questions = generate_document_questions(extracted_text, num_questions=5)
            result['suggestedQuestions'] = questions
        
        return response(200, result)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {'error': 'Summarization failed', 'message': str(e)})


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
