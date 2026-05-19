# python-data-extractor-from-pdf
Python Data Extract 


```
sudo apt update && sudo apt upgrade -y && \
sudo apt install python3 python3-pip python3-venv python3-dev libssl-dev libffi-dev poppler-utils -y && \
mkdir -p diploma-result-extractor && cd diploma-result-extractor && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install --upgrade pip && \
pip install pdfplumber pymongo tqdm && \
pip freeze > requirements.txt && \
echo "✅ সব ইনস্টল হয়ে গেছে!"
```
```
source venv/bin/activate
python -c "import pdfplumber; print('pdfplumber OK')"
python -c "import pymongo; print('pymongo OK')"
```