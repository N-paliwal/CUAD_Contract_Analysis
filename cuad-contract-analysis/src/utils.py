import re
from pathlib import Path


def normalize_text(text: str) -> str:
    """Normalize contract text by cleaning and formatting"""
    if not text:
        return ''

    text = text.replace('\r', '\n')
    text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Page\s+\d+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\n{2,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)

    return text.strip()


def extract_contract_id(filepath: Path) -> str:
    """Extract contract ID from filename"""
    return filepath.stem if filepath else 'unknown_contract'


def count_words(text: str) -> int:
    """Count words in text"""
    if not text:
        return 0
    return len(text.split())