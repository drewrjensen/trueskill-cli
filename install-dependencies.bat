python -m venv venv
call venv\Scripts\activate.bat
py -m pip install --upgrade pip || python -m pip install --upgrade pip || python3 -m pip install --upgrade pip
pip install pyinstaller trueskill