#!/bin/bash

echo "🚀 Starting Growth Tools API..."

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate and install
source venv/bin/activate
pip install -r requirements.txt

# Set API token
export REPLICATE_API_TOKEN="your_replicate_api_token_here"

# Run the API
python app.py