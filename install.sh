# 1. Install dependencies
pip install -r requirements.txt

# 2. Create directories
mkdir -p data models

# 3. Fetch EU policies
python src/main.py --fetch

# 4. Scan a website
python src/main.py --scan-web https://example.com

# 5. Scan a GitHub repo
python src/main.py --scan-github openai/gpt-3

# 6. Generate report
python src/main.py --report