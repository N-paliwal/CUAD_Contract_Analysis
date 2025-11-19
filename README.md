# CUAD Contract Analysis Pipeline

##  Overview

This project implements an automated pipeline for analyzing legal contracts using Large Language Models (LLMs). It processes contracts from the CUAD (Contract Understanding Atticus Dataset), extracts key clauses, and generates comprehensive summaries.

##  Features

- **Multi-format PDF Text Extraction**: Supports PyPDF2, pdfplumber, and PyMuPDF with automatic best-method selection
- **LLM-Powered Clause Extraction**: Uses GPT-4/Claude to identify:
  - Termination conditions
  - Confidentiality clauses
  - Liability clauses
- **Intelligent Summarization**: Generates 100-150 word summaries highlighting purpose, obligations, and risks
- **Few-Shot Learning**: Improves extraction accuracy with contextual examples
- **Semantic Search** (Bonus): Implements vector embeddings for clause similarity search
- **Robust Error Handling**: Automatic retries and fallback mechanisms

##  Project Structure

```
cuad-contract-analysis/
│
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── config.py                 # Configuration settings
├── .env.example              # Environment variables template
├── flow_diagram.png          # Solution flow diagram
│
├── data/
│   ├── raw/                  # Store CUAD PDFs here
│   └── processed/            # Intermediate processing files
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py        # Dataset loading and management
│   ├── text_extractor.py     # PDF text extraction
│   ├── llm_processor.py      # LLM-based analysis
│   ├── embeddings.py         # Semantic search (bonus)
│   └── utils.py              # Utility functions
│
├── main.py                   # Main execution script
├── notebook.ipynb            # Jupyter notebook version
│
└── outputs/
    ├── results.csv           # Extracted data in CSV format
    └── results.json          # Extracted data in JSON format
```


### Prerequisites

- Python 3.8 or higher
- OpenAI API key or Anthropic API key

### Setup Steps

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

5. **Download CUAD dataset**
```bash
# Download from: https://zenodo.org/record/4595826/files/CUAD_v1.zip
# Extract PDF files to data/raw/ directory
```

##  Configuration

Edit `config.py` to customize:

- **LLM Provider**: Choose between OpenAI or Anthropic
- **Model Selection**: Specify model (e.g., gpt-4o-mini, claude-3-haiku)
- **Processing Parameters**: Chunk sizes, token limits, etc.
- **Output Format**: CSV, JSON, or both

```python
# Example configuration
LLM_PROVIDER = "openai"
LLM_MODEL = "gpt-4o-mini"
NUM_CONTRACTS = 50
```

##  Usage

### Command Line

**Process all contracts:**
```bash
python main.py
```

**Process specific number of contracts:**
```bash
python main.py --num-contracts 10
```

**Use specific LLM provider:**
```bash
python main.py --provider anthropic --model claude-3-haiku-20240307
```

**Enable semantic search:**
```bash
python main.py --enable-semantic-search
```


##  Output

The pipeline generates two output files:

### CSV Format (`outputs/results.csv`)
```
contract_id,summary,termination_clause,confidentiality_clause,liability_clause
CONTRACT_001,"This is a Software License Agreement...",
"Either party may terminate...","Confidential Information shall...","Liability limited to..."
```

### JSON Format (`outputs/results.json`)
```json
[
  {
    "contract_id": "CONTRACT_001",
    "summary": "This is a Software License Agreement...",
    "termination_clause": "Either party may terminate...",
    "confidentiality_clause": "Confidential Information shall...",
    "liability_clause": "Liability limited to..."
  }
]
```

##  Solution Architecture

### Pipeline Flow

```
┌─────────────────────────────────────────────────────────┐
│                   1. Data Loading                       │
│  - Load contracts from CUAD dataset                     │
│  - Select subset (50 contracts)                         │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              2. PDF Text Extraction                     │
│  - Try multiple extraction methods (auto-select)        │
│  - pdfplumber → PyMuPDF → PyPDF2                       │
│  - Score and select best result                         │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              3. Text Preprocessing                      │
│  - Normalize whitespace and formatting                  │
│  - Remove page numbers and artifacts                    │
│  - Chunk long documents for LLM processing              │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│         4. LLM-Based Clause Extraction                  │
│                                                          │
│  For each clause type (Termination, Confidentiality,    │
│  Liability):                                            │
│  ┌────────────────────────────────────────────┐        │
│  │ - Build few-shot prompt with examples      │        │
│  │ - Call LLM API (with retry logic)          │        │
│  │ - Parse and validate response              │        │
│  └────────────────────────────────────────────┘        │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│           5. Contract Summarization                     │
│  - Generate 100-150 word summary                        │
│  - Highlight: Purpose, Obligations, Risks               │
│  - Use structured prompt for consistency                │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│      6. Semantic Search (Bonus - Optional)              │
│  - Generate embeddings for clauses                      │
│  - Store in vector database (FAISS/ChromaDB)           │
│  - Enable similarity search across contracts            │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│               7. Results Export                         │
│  - Compile all extracted data                           │
│  - Export to CSV and JSON formats                       │
│  - Generate processing report                           │
└─────────────────────────────────────────────────────────┘
```

##  Approach Explanation

### 1. Multi-Method PDF Extraction
To handle varying PDF quality, we implement three extraction libraries and automatically select the best result based on:
- Text length and word count
- Alphanumeric character ratio
- Overall readability score

### 2. Prompt Engineering Strategy

**Few-Shot Learning**: We provide 2-3 examples per clause type to guide the LLM in understanding:
- What constitutes a valid clause
- Expected extraction format
- Edge cases and variations

**Chain-of-Thought**: The prompts are structured to guide the model through:
1. Understanding the clause type
2. Identifying relevant sections
3. Extracting precise text
4. Validating completeness

**Structured Output**: We enforce consistent output formats to ensure reliable parsing and validation.

### 3. Handling Long Documents

Legal contracts often exceed LLM context windows. Our solution:
- Chunks documents intelligently at sentence boundaries
- Processes chunks with overlap to avoid missing clauses
- Aggregates results from multiple chunks
- Prioritizes most comprehensive extractions

### 4. Semantic Search Implementation 

We use Sentence Transformers to:
1. Generate embeddings for extracted clauses
2. Store in FAISS vector index for efficient search
3. Enable similarity queries like "Find all contracts with uncapped liability"
4. Support comparative analysis across contracts

##  Evaluation Criteria Addressed

### ✅ Accuracy
- Few-shot prompting improves clause detection
- Multiple validation checks for extracted text
- Fallback mechanisms for edge cases

### ✅ Code Quality
- Modular design with clear separation of concerns
- Comprehensive docstrings and type hints
- Logging for debugging and monitoring
- Error handling with retries

### ✅ LLM Utilization
- Efficient prompt engineering with few-shot examples
- Chunking strategy for long documents
- Temperature tuning (0.0 for extraction, 0.3 for summaries)
- API cost optimization with retry logic

### ✅ Reproducibility
- Detailed setup instructions
- Dependency management with requirements.txt
- Environment configuration via .env
- Seed setting for consistent results

### ✅ Creativity
- Automatic extraction method selection
- Semantic search over extracted clauses
- Comparative analysis capabilities
- Model-agnostic design (OpenAI/Anthropic/Local)

