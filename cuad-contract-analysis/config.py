import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"
SRC_DIR = BASE_DIR / "src"

# Create directories if they don't exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Dataset configuration
CUAD_DATASET_URL = "https://zenodo.org/record/4595826/files/CUAD_v1.zip"
NUM_CONTRACTS = 50  # Use 50 contracts as specified

# LLM Configuration
LLM_PROVIDER = "mistral"  # Change to mistral
LLM_MODEL = "mistral-small-latest"  # Cost-effective model

MODELS = {
    "openai": {
        "default": "gpt-4o-mini",
        "advanced": "gpt-4o",
    },
    "anthropic": {
        "default": "claude-3-haiku-20240307",
        "advanced": "claude-3-5-sonnet-20241022",
    },
    "mistral": {
        "default": "mistral-small-latest",      
        "medium": "mistral-medium-latest",      
        "advanced": "mistral-large-latest",    
    }
}

# Clause types to extract
CLAUSE_TYPES = [
    "termination",
    "confidentiality",
    "liability"
]

# Summary configuration
SUMMARY_MIN_WORDS = 100
SUMMARY_MAX_WORDS = 150

# Text processing
MAX_CHUNK_SIZE = 8000  # Characters per chunk for long documents
CHUNK_OVERLAP = 500

# Embedding configuration (for bonus feature)
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
EMBEDDING_DIM = 768
TOP_K_RESULTS = 5

#API retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Output configuration
OUTPUT_FORMAT = "csv"  # Options: "csv", "json", "both"
OUTPUT_CSV = OUTPUT_DIR / "results.csv"
OUTPUT_JSON = OUTPUT_DIR / "results.json"


print("="*80)
print("CONFIG.PY")