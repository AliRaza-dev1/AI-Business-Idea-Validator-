"""
Security Utilities — Validates input bounds, sanitizes characters, and detects prompt injection attempts.
"""
import re
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

# List of typical prompt injection keywords/patterns
INJECTION_KEYWORDS = [
    r"ignore\s+(?:all\s+)?previous\s+instructions",
    r"ignore\s+(?:all\s+)?prior\s+guidelines",
    r"system\s+prompt",
    r"you\s+are\s+now\s+a",
    r"override\s+rules",
    r"forget\s+(?:all\s+)?instructions",
    r"translate\s+the\s+(?:system\s+)?instructions",
    r"new\s+instructions\s+follow",
    r"bypass\s+restrictions"
]

def sanitize_input_text(text: str) -> str:
    """Removes HTML/XML tags and other potentially harmful markup symbols"""
    if not text:
        return ""
    # Strip HTML tags
    clean = re.sub(r"<[^>]*>", "", text)
    # Remove control characters
    clean = "".join(ch for ch in clean if ord(ch) >= 32 or ch in "\n\r\t")
    return clean.strip()

def check_prompt_injection(text: str):
    """Scans text for common prompt injection patterns and raises exception if detected"""
    if not text:
        return
        
    lower_text = text.lower()
    for pattern in INJECTION_KEYWORDS:
        if re.search(pattern, lower_text):
            logger.warning(f"Prompt injection attempt detected: Matching pattern '{pattern}'")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security validation failed: Potential prompt injection attempt detected."
            )

def validate_payload_sizes(idea_data: dict):
    """Asserts that fields stay within reasonable size constraints to prevent abuse"""
    # Max title length: 150 chars
    title = idea_data.get("title", "")
    if len(title) > 150:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Validation error: Title cannot exceed 150 characters."
        )
        
    # Max description and text fields lengths: 4000 characters
    for key in ["description", "problem_statement", "target_market", "proposed_solution", "value_proposition", "business_model"]:
        val = idea_data.get(key, "")
        if val and len(val) > 4000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation error: Field '{key}' exceeds maximum allowed size of 4000 characters."
            )
