"""
DynamoDB utility functions for document metadata storage.
"""
import boto3
import os
from datetime import datetime
from typing import Optional, List
import uuid

# Initialize DynamoDB resource
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.environ.get('AWS_REGION', 'us-east-1')
)

TABLE_NAME = os.environ.get('DOCUMENTS_TABLE', 'DocuMindDocuments')


def get_table():
    """Get the DynamoDB table resource."""
    return dynamodb.Table(TABLE_NAME)


def create_document(
    user_id: str,
    filename: str,
    s3_key: str,
    content_type: str,
    file_size: int
) -> dict:
    """
    Create a new document record in DynamoDB.
    
    Args:
        user_id: The user who uploaded the document
        filename: Original filename
        s3_key: S3 object key
        content_type: MIME type of the document
        file_size: File size in bytes
        
    Returns:
        The created document record
    """
    table = get_table()
    
    document_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    item = {
        'documentId': document_id,
        'userId': user_id,
        'filename': filename,
        's3Key': s3_key,
        'contentType': content_type,
        'fileSize': file_size,
        'status': 'UPLOADED',
        'createdAt': timestamp,
        'updatedAt': timestamp
    }
    
    table.put_item(Item=item)
    
    return item


def update_document_status(document_id: str, status: str, metadata: Optional[dict] = None) -> dict:
    """
    Update document status and optionally add metadata.
    
    Args:
        document_id: The document ID
        status: New status (UPLOADED, PROCESSING, EXTRACTED, COMPLETED, FAILED)
        metadata: Additional metadata to store
        
    Returns:
        Updated document record
    """
    table = get_table()
    
    update_expression = "SET #status = :status, updatedAt = :updatedAt"
    expression_values = {
        ':status': status,
        ':updatedAt': datetime.utcnow().isoformat()
    }
    expression_names = {
        '#status': 'status'
    }
    
    if metadata:
        for key, value in metadata.items():
            update_expression += f", {key} = :{key}"
            expression_values[f':{key}'] = value
    
    response = table.update_item(
        Key={'documentId': document_id},
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_names,
        ExpressionAttributeValues=expression_values,
        ReturnValues='ALL_NEW'
    )
    
    return response.get('Attributes', {})


def get_document(document_id: str) -> Optional[dict]:
    """
    Get a document by ID.
    
    Args:
        document_id: The document ID
        
    Returns:
        Document record or None if not found
    """
    table = get_table()
    
    response = table.get_item(Key={'documentId': document_id})
    
    return response.get('Item')


def get_user_documents(user_id: str, limit: int = 50) -> List[dict]:
    """
    Get all documents for a user.
    
    Args:
        user_id: The user ID
        limit: Maximum number of documents to return
        
    Returns:
        List of document records
    """
    table = get_table()
    
    response = table.query(
        IndexName='userId-createdAt-index',
        KeyConditionExpression='userId = :userId',
        ExpressionAttributeValues={':userId': user_id},
        ScanIndexForward=False,  # Most recent first
        Limit=limit
    )
    
    return response.get('Items', [])


def delete_document(document_id: str) -> bool:
    """
    Delete a document record.
    
    Args:
        document_id: The document ID
        
    Returns:
        True if deleted successfully
    """
    table = get_table()
    
    try:
        table.delete_item(Key={'documentId': document_id})
        return True
    except Exception:
        return False


def store_extracted_text(document_id: str, text: str, word_count: int, confidence: float) -> dict:
    """
    Store extracted text for a document.
    
    Args:
        document_id: The document ID
        text: Extracted text content
        word_count: Number of words extracted
        confidence: OCR confidence score
        
    Returns:
        Updated document record
    """
    return update_document_status(
        document_id,
        'EXTRACTED',
        {
            'extractedText': text[:50000],  # Limit text size for DynamoDB
            'wordCount': word_count,
            'ocrConfidence': str(confidence),  # DynamoDB doesn't support float
            'textLength': len(text)
        }
    )


def store_summary(document_id: str, summary: str) -> dict:
    """
    Store AI-generated summary for a document.
    
    Args:
        document_id: The document ID
        summary: The generated summary
        
    Returns:
        Updated document record
    """
    return update_document_status(
        document_id,
        'COMPLETED',
        {'summary': summary}
    )


def add_query_to_history(document_id: str, question: str, answer: str) -> None:
    """
    Add a Q&A interaction to document history.
    
    Args:
        document_id: The document ID
        question: The user's question
        answer: The AI's answer
    """
    table = get_table()
    
    timestamp = datetime.utcnow().isoformat()
    query_item = {
        'question': question,
        'answer': answer,
        'timestamp': timestamp
    }
    
    # Append to query history list
    try:
        table.update_item(
            Key={'documentId': document_id},
            UpdateExpression="SET queryHistory = list_append(if_not_exists(queryHistory, :empty), :query)",
            ExpressionAttributeValues={
                ':query': [query_item],
                ':empty': []
            }
        )
    except Exception:
        # If list_append fails, create new list
        table.update_item(
            Key={'documentId': document_id},
            UpdateExpression="SET queryHistory = :query",
            ExpressionAttributeValues={
                ':query': [query_item]
            }
        )
