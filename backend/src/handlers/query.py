"""
Document Q&A Lambda Handler

Handles questions about documents using Amazon Bedrock and RAG-style prompting.
"""
import json
import os

BUCKET_NAME = os.environ.get('DOCUMENTS_BUCKET', 'documind-documents')


def lambda_handler(event, context):
    """
    Handle document Q&A requests.
    
    Expects:
    - documentId in path parameters
    - question in request body
    """
    try:
        from utils.bedrock import answer_question
        from utils.dynamodb import get_document, add_query_to_history
        
        # Get document ID
        path_params = event.get('pathParameters', {}) or {}
        document_id = path_params.get('documentId')
        
        if not document_id:
            return response(400, {'error': 'documentId is required'})
        
        # Parse request body
        try:
            body = json.loads(event.get('body', '{}'))
        except json.JSONDecodeError:
            return response(400, {'error': 'Invalid JSON body'})
        
        question = body.get('question', '').strip()
        
        if not question:
            return response(400, {'error': 'question is required in request body'})
        
        if len(question) > 1000:
            return response(400, {'error': 'Question too long (max 1000 characters)'})
        
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
        
        # Get answer using Bedrock
        result = answer_question(extracted_text, question)
        
        # Store in query history
        add_query_to_history(document_id, question, result['answer'])
        
        return response(200, {
            'documentId': document_id,
            'question': question,
            'answer': result['answer'],
            'confidence': result['confidence']
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {'error': 'Query failed', 'message': str(e)})


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
