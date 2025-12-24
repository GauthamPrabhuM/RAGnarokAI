"""
Amazon Bedrock utility functions for LLM interactions.
"""
import json
import boto3
from typing import Optional
import os

# Initialize Bedrock client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.environ.get('AWS_REGION', 'us-east-1')
)

# Default model - Claude 3 Haiku (fast and cost-effective)
DEFAULT_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"


def invoke_claude(
    prompt: str,
    system_prompt: Optional[str] = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
    model_id: str = DEFAULT_MODEL_ID
) -> str:
    """
    Invoke Claude model via Amazon Bedrock.
    
    Args:
        prompt: The user prompt to send to the model
        system_prompt: Optional system prompt for context
        max_tokens: Maximum tokens in response
        temperature: Creativity parameter (0-1)
        model_id: The Bedrock model ID to use
        
    Returns:
        The model's response text
    """
    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": messages
    }
    
    if system_prompt:
        body["system"] = system_prompt
    
    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body)
    )
    
    response_body = json.loads(response['body'].read())
    return response_body['content'][0]['text']


def summarize_document(text: str, max_length: int = 500) -> str:
    """
    Generate a summary of the given document text.
    
    Args:
        text: The document text to summarize
        max_length: Approximate maximum length of summary
        
    Returns:
        A concise summary of the document
    """
    system_prompt = """You are an expert document analyst. Your task is to provide 
    clear, concise, and accurate summaries of documents. Focus on the key points, 
    main ideas, and important details. Be objective and maintain the original 
    meaning."""
    
    prompt = f"""Please provide a comprehensive summary of the following document. 
The summary should be approximately {max_length} words and capture the main points.

Document:
---
{text}
---

Summary:"""
    
    return invoke_claude(prompt, system_prompt=system_prompt, temperature=0.3)


def answer_question(document_text: str, question: str) -> dict:
    """
    Answer a question about a document using RAG-style prompting.
    
    Args:
        document_text: The context document text
        question: The user's question
        
    Returns:
        Dictionary with answer and confidence
    """
    system_prompt = """You are a helpful document assistant. Answer questions 
    based ONLY on the provided document context. If the answer cannot be found 
    in the document, say so clearly. Always cite relevant parts of the document 
    when possible."""
    
    prompt = f"""Based on the following document, please answer the question.
If the answer is not found in the document, respond with "I couldn't find this information in the document."

Document:
---
{document_text}
---

Question: {question}

Please provide a clear and concise answer:"""
    
    answer = invoke_claude(prompt, system_prompt=system_prompt, temperature=0.2)
    
    # Determine confidence based on response
    confidence = "high"
    if "couldn't find" in answer.lower() or "not found" in answer.lower():
        confidence = "low"
    elif "may" in answer.lower() or "might" in answer.lower():
        confidence = "medium"
    
    return {
        "answer": answer,
        "confidence": confidence
    }


def extract_key_entities(text: str) -> dict:
    """
    Extract key entities from document text.
    
    Args:
        text: The document text
        
    Returns:
        Dictionary of entity types and their values
    """
    system_prompt = """You are an entity extraction expert. Extract key entities 
    from documents accurately. Return entities in a structured format."""
    
    prompt = f"""Extract key entities from the following document. 
Identify: People, Organizations, Dates, Locations, Monetary Values, and Key Terms.

Document:
---
{text}
---

Return the entities as a JSON object with these keys:
- people: list of person names
- organizations: list of organization names
- dates: list of dates mentioned
- locations: list of locations
- monetary_values: list of monetary amounts
- key_terms: list of important terms or concepts

JSON:"""
    
    response = invoke_claude(prompt, system_prompt=system_prompt, temperature=0.1)
    
    # Try to parse as JSON, fallback to returning raw response
    try:
        # Find JSON in response
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(response[start:end])
    except json.JSONDecodeError:
        pass
    
    return {"raw_response": response}


def generate_document_questions(text: str, num_questions: int = 5) -> list:
    """
    Generate relevant questions that could be asked about the document.
    
    Args:
        text: The document text
        num_questions: Number of questions to generate
        
    Returns:
        List of generated questions
    """
    system_prompt = """You are an educational assistant. Generate insightful 
    questions that help users understand and explore document content."""
    
    prompt = f"""Based on the following document, generate {num_questions} 
thoughtful questions that someone might want to ask about its content.
Focus on important details, key concepts, and practical insights.

Document:
---
{text[:3000]}  # Limit text to avoid token limits
---

Generate exactly {num_questions} questions, one per line, numbered 1-{num_questions}:"""
    
    response = invoke_claude(prompt, system_prompt=system_prompt, temperature=0.7)
    
    # Parse questions from response
    questions = []
    for line in response.strip().split('\n'):
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith('-')):
            # Remove numbering/bullets
            question = line.lstrip('0123456789.-) ').strip()
            if question:
                questions.append(question)
    
    return questions[:num_questions]
