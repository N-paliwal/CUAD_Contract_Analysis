#!/bin/bash
echo "Setting up CUAD Contract Analysis Pipeline..."

# Create virtual environment
python -m venv venv

# Activate virtual environment
echo "To activate the virtual environment run:"
echo "  source venv/bin/activate  # On Windows: venv\\Scripts\\activate"

# Upgrade pip
venv/bin/pip install --upgrade pip || pip install --upgrade pip

# Install dependencies
if [ -f requirements.txt ]; then
  echo "Installing dependencies from requirements.txt..."
  venv/bin/pip install -r requirements.txt || pip install -r requirements.txt
else
  echo "requirements.txt not found."
fi

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
