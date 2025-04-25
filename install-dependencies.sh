echo -n "Activating virtual environment..."
python -m venv venv
source venv/bin/activate
venv/bin/pip install -r requirements.txt