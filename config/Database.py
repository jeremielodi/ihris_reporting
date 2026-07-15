import os

dbParams = {
    "host": "127.0.0.1",
    "user": "test",
    "passwd": "test",
    "database": 'test'
}

# Credentials for the HTTPBasic guard in main.py (get_current_username).
# Override via DOC_ACCESS_USERNAME / DOC_ACCESS_PASSWORD in .env.
docAccess = {
    'username': os.getenv('DOC_ACCESS_USERNAME', 'docs'),
    'password': os.getenv('DOC_ACCESS_PASSWORD', 'docs'),
}
