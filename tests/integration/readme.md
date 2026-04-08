from root folder (../)
PYTHONPATH=. pytest


python3.10 -m pip install aiosqlite
python3.10 -m pip install trio


pytest -vv -s --tb=long -l