# Complete Code Package - All Python Files

## requirements.txt
```
# Core Dependencies
python>=3.8

# PDF Processing
PyPDF2>=3.0.0
pdfplumber>=0.10.0
PyMuPDF>=1.23.0

# LLM APIs
openai>=1.0.0
anthropic>=0.7.0

# Text Processing
nltk>=3.8.0
regex>=2023.10.0

# Data Handling
pandas>=2.0.0
numpy>=1.24.0

# Embedding & Vector Search (Bonus)
sentence-transformers>=2.2.0
faiss-cpu>=1.7.4
chromadb>=0.4.0

# Environment Management
python-dotenv>=1.0.0

# Utilities
tqdm>=4.66.0
requests>=2.31.0
tenacity>=8.2.0

# Jupyter Notebook
jupyter>=1.0.0
ipykernel>=6.25.0
```

## .env.example
```
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
```

## config.py
```python
"""
Configuration file for CUAD Contract Analysis Pipeline
"""
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
LLM_PROVIDER = "openai"  # Options: "openai", "anthropic"
LLM_MODEL = "gpt-4o-mini"  # Cost-effective option
LLM_TEMPERATURE = 0.0  # For consistency in extraction
LLM_MAX_TOKENS = 4096

# Alternative models
MODELS = {
    "openai": {
        "default": "gpt-4o-mini",
        "advanced": "gpt-4o",
    },
    "anthropic": {
        "default": "claude-3-haiku-20240307",
        "advanced": "claude-3-5-sonnet-20241022",
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

# API retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Output configuration
OUTPUT_FORMAT = "csv"  # Options: "csv", "json", "both"
OUTPUT_CSV = OUTPUT_DIR / "results.csv"
OUTPUT_JSON = OUTPUT_DIR / "results.json"
```

## src/__init__.py
```python
"""
CUAD Contract Analysis Pipeline
"""
__version__ = "1.0.0"
__author__ = "Your Name"
```

## GitHub Setup Instructions

### 1. Create .gitignore
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# Environment Variables
.env

# Jupyter Notebook
.ipynb_checkpoints

# Data
data/raw/*.pdf
data/processed/*

# Outputs
outputs/*.csv
outputs/*.json

# Logs
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

### 2. Initialize Git Repository
```bash
cd cuad-contract-analysis
git init
git add .
git commit -m "Initial commit: CUAD contract analysis pipeline"
git branch -M main
git remote add origin <your-repository-url>
git push -u origin main
```

### 3. Repository Structure
Make sure your repository contains:
- All Python files (main.py, src/*.py, config.py)
- requirements.txt
- .env.example (NOT .env with real keys)
- README.md
- .gitignore
- Flow diagram image

### 4. README Badge (Optional)
Add to top of README.md:
```markdown
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
```

## Quick Start Script
Save as `setup.sh`:
```bash
#!/bin/bash

echo "Setting up CUAD Contract Analysis Pipeline..."

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please add your API keys."
fi

# Create necessary directories
mkdir -p data/raw
mkdir -p data/processed
mkdir -p outputs

echo "Setup complete!"
echo "Next steps:"
echo "1. Add your API key to .env file"
echo "2. Download CUAD dataset to data/raw/"
echo "3. Run: python main.py"
```

Make executable:
```bash
chmod +x setup.sh
./setup.sh
```

## Testing the Pipeline

### Test Single Contract
```python
# test_single.py
from pathlib import Path
from src.text_extractor import extract_text_from_pdf
from src.llm_processor import LLMProcessor
from src.utils import normalize_text
import json

# Initialize
llm = LLMProcessor(provider="openai", model="gpt-4o-mini")

# Test file
pdf_path = Path("data/raw/test_contract.pdf")

# Extract
print("Extracting text...")
text = extract_text_from_pdf(pdf_path)
text = normalize_text(text)
print(f"Extracted {len(text)} characters")

# Process
print("\\nProcessing with LLM...")
results = llm.process_contract(text)

# Display
print("\\nResults:")
print(json.dumps(results, indent=2))
```

Run: `python test_single.py`

## Deployment Checklist

Before pushing to GitHub:
- [ ] Remove any API keys from code
- [ ] Add .env to .gitignore
- [ ] Include .env.example with placeholders
- [ ] Test setup.sh script
- [ ] Verify README has all instructions
- [ ] Ensure no large PDF files in repo
- [ ] Add flow diagram image
- [ ] Test installation on fresh machine
- [ ] Add LICENSE file (MIT recommended)
- [ ] Update author information
- [ ] Add contact information to README

## Final Repository Structure
```
cuad-contract-analysis/
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
├── setup.sh
├── config.py
├── .env.example
├── main.py
├── test_single.py
├── notebook.ipynb
├── flow_diagram.png
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── text_extractor.py
│   ├── llm_processor.py
│   ├── embeddings.py
│   └── utils.py
│
├── data/
│   ├── raw/
│   │   └── README.md (instructions to download)
│   └── processed/
│
└── outputs/
    └── README.md (output files will be generated here)
```

## data/raw/README.md
```markdown
# CUAD Dataset

Download the CUAD dataset from:
https://zenodo.org/record/4595826

Extract the PDF files from CUAD_v1.zip to this directory.

Expected structure:
```
data/raw/
├── full_contract_pdf/
│   ├── CONTRACT_001.pdf
│   ├── CONTRACT_002.pdf
│   └── ...
```

The pipeline will automatically detect and process PDF files from this location.
```

## outputs/README.md
```markdown
# Output Files

This directory contains the results from contract analysis.

Files generated:
- `results.csv`: Extracted data in CSV format
- `results.json`: Extracted data in JSON format
- `contract_analysis.log`: Processing logs

These files are automatically generated when you run:
```bash
python main.py
```
```

## Additional Files to Include

### LICENSE (MIT)
```
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### CONTRIBUTING.md
```markdown
# Contributing

Thank you for your interest in contributing!

## How to Contribute

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Code Style

- Follow PEP 8 guidelines
- Add docstrings to all functions
- Use type hints where appropriate
- Keep functions focused and modular

## Testing

Run tests before submitting PR:
```bash
python -m pytest tests/
```

## Questions?

Open an issue or contact [your-email@example.com]
```

## Final Checklist for Submission

✅ All code files created and tested
✅ README.md comprehensive and clear
✅ requirements.txt complete
✅ .env.example provided (no real keys)
✅ Flow diagram included
✅ .gitignore configured
✅ LICENSE file added
✅ Repository is public
✅ No mention of company name in code
✅ All deliverables addressed:
   - Code (main.py + src modules)
   - Output files (CSV/JSON format specification)
   - README with instructions and flow diagram
   - Bonus features implemented

## Submission

1. Push all code to GitHub
2. Verify repository is public
3. Test clone and setup on fresh environment
4. Reply to assessment email with GitHub link
5. Include brief summary of approach and features

**Repository URL**: [Your GitHub URL here]
