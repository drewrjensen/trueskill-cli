echo -n "Activating virtual environment..."
python -m venv venv
source venv/bin/activate
echo "done"

echo -n "Installing dependencies..."
venv/bin/pip install pyinstaller trueskill
echo "done"