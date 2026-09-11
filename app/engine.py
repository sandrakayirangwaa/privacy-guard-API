import re
import uuid
from typing import Tuple, Dict

PATTERNS = {
    "EMAIL": re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
    "PHONE": re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
    "CREDIT_CARD": re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b')
}

def mask_text(text: str) -> Tuple[str, Dict[str, Tuple[str, str]]]:
    """
    Scans the text, applies regex masks, and generates unique tracking keys.
    Returns: (sanitized_text, dictionary_of_found_tokens)
    """
    sanitized_text = text
    tokens_to_save = {}

    for entity_type, pattern in PATTERNS.items():
        matches = pattern.findall(sanitized_text)
        
        for match in matches:
            unique_suffix = str(uuid.uuid4())[:5]
            token_id = f"[{entity_type}_{unique_suffix}]"
            
            sanitized_text = sanitized_text.replace(match, token_id, 1)
            
            tokens_to_save[token_id] = (match, entity_type)

    return sanitized_text, tokens_to_save
