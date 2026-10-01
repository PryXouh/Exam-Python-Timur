python -m venv .venv
source .venv/bin/activate  # Sur Windows : .venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload

python -m pytest -q (x2)

