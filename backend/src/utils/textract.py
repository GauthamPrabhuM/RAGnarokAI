"""
Amazon Textract utility functions for document text extraction.
"""
import boto3
import os
from typing import Optional

# Initialize Textract client
textract = boto3.client(
    service_name='textract',
    region_name=os.environ.get('AWS_REGION', 'us-east-1')
)


def extract_text_from_s3(bucket: str, key: str) -> dict:
    """
    Extract text from a document stored in S3 using Amazon Textract.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
        
    Returns:
        Dictionary with extracted text and metadata
    """
    response = textract.detect_document_text(
        Document={
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        }
    )
    
    # Extract all text blocks
    text_blocks = []
    lines = []
    words = []
    
    for block in response.get('Blocks', []):
        if block['BlockType'] == 'LINE':
            lines.append(block['Text'])
        elif block['BlockType'] == 'WORD':
            words.append(block['Text'])
    
    full_text = '\n'.join(lines)
    
    return {
        'text': full_text,
        'line_count': len(lines),
        'word_count': len(words),
        'confidence': _calculate_average_confidence(response.get('Blocks', []))
    }


def extract_text_from_bytes(document_bytes: bytes) -> dict:
    """
    Extract text from document bytes using Amazon Textract.
    
    Args:
        document_bytes: The document content as bytes
        
    Returns:
        Dictionary with extracted text and metadata
    """
    response = textract.detect_document_text(
        Document={
            'Bytes': document_bytes
        }
    )
    
    lines = []
    words = []
    
    for block in response.get('Blocks', []):
        if block['BlockType'] == 'LINE':
            lines.append(block['Text'])
        elif block['BlockType'] == 'WORD':
            words.append(block['Text'])
    
    full_text = '\n'.join(lines)
    
    return {
        'text': full_text,
        'line_count': len(lines),
        'word_count': len(words),
        'confidence': _calculate_average_confidence(response.get('Blocks', []))
    }


def analyze_document_s3(bucket: str, key: str, feature_types: Optional[list] = None) -> dict:
    """
    Perform advanced document analysis including forms and tables.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
        feature_types: List of features to analyze ('TABLES', 'FORMS', 'SIGNATURES')
        
    Returns:
        Dictionary with analysis results
    """
    if feature_types is None:
        feature_types = ['TABLES', 'FORMS']
    
    response = textract.analyze_document(
        Document={
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        },
        FeatureTypes=feature_types
    )
    
    result = {
        'text': '',
        'tables': [],
        'forms': [],
        'signatures': []
    }
    
    lines = []
    key_value_pairs = []
    
    for block in response.get('Blocks', []):
        if block['BlockType'] == 'LINE':
            lines.append(block['Text'])
        elif block['BlockType'] == 'KEY_VALUE_SET':
            if 'KEY' in block.get('EntityTypes', []):
                # This is a key, find its value
                key_text = _get_text_from_block(block, response['Blocks'])
                value_text = _get_value_for_key(block, response['Blocks'])
                if key_text:
                    key_value_pairs.append({
                        'key': key_text,
                        'value': value_text or ''
                    })
    
    result['text'] = '\n'.join(lines)
    result['forms'] = key_value_pairs
    
    return result


def start_async_analysis(bucket: str, key: str, sns_topic_arn: str, role_arn: str) -> str:
    """
    Start asynchronous document analysis for large documents.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
        sns_topic_arn: SNS topic ARN for notifications
        role_arn: IAM role ARN for Textract
        
    Returns:
        Job ID for tracking the analysis
    """
    response = textract.start_document_text_detection(
        DocumentLocation={
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        },
        NotificationChannel={
            'SNSTopicArn': sns_topic_arn,
            'RoleArn': role_arn
        }
    )
    
    return response['JobId']


def get_async_results(job_id: str) -> dict:
    """
    Get results from an asynchronous text detection job.
    
    Args:
        job_id: The job ID from start_async_analysis
        
    Returns:
        Dictionary with job status and results
    """
    response = textract.get_document_text_detection(JobId=job_id)
    
    if response['JobStatus'] != 'SUCCEEDED':
        return {
            'status': response['JobStatus'],
            'text': None
        }
    
    lines = []
    for block in response.get('Blocks', []):
        if block['BlockType'] == 'LINE':
            lines.append(block['Text'])
    
    # Handle pagination
    next_token = response.get('NextToken')
    while next_token:
        response = textract.get_document_text_detection(
            JobId=job_id,
            NextToken=next_token
        )
        for block in response.get('Blocks', []):
            if block['BlockType'] == 'LINE':
                lines.append(block['Text'])
        next_token = response.get('NextToken')
    
    return {
        'status': 'SUCCEEDED',
        'text': '\n'.join(lines),
        'line_count': len(lines)
    }


def _calculate_average_confidence(blocks: list) -> float:
    """Calculate average confidence score from Textract blocks."""
    confidences = [
        block.get('Confidence', 0) 
        for block in blocks 
        if 'Confidence' in block
    ]
    
    if not confidences:
        return 0.0
    
    return sum(confidences) / len(confidences)


def _get_text_from_block(block: dict, all_blocks: list) -> str:
    """Extract text from a block and its relationships."""
    if 'Text' in block:
        return block['Text']
    
    text_parts = []
    if 'Relationships' in block:
        for relationship in block['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    for b in all_blocks:
                        if b['Id'] == child_id and 'Text' in b:
                            text_parts.append(b['Text'])
    
    return ' '.join(text_parts)


def _get_value_for_key(key_block: dict, all_blocks: list) -> Optional[str]:
    """Find the value associated with a key block."""
    if 'Relationships' not in key_block:
        return None
    
    for relationship in key_block['Relationships']:
        if relationship['Type'] == 'VALUE':
            for value_id in relationship['Ids']:
                for block in all_blocks:
                    if block['Id'] == value_id:
                        return _get_text_from_block(block, all_blocks)
    
    return None
