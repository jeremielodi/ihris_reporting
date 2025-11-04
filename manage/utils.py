import imghdr
import os
from datetime import datetime
from pathlib import Path
import random
import string

def createUploadDirs(type:str):
    UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR"))
    now = datetime.now()
    datePath = f"{type}/{now.year}/{now.month}/{now.day}"
    new_path = Path(f"{UPLOAD_DIR}/{datePath}")
    os.makedirs(name= new_path, exist_ok=True)
    return datePath, Path(new_path)

def generate_unit_id(prefix: str = "unit", length: int = 10) -> str:
    """
    Generate a unique unit ID string with a 10-character random suffix.

    Example output: 'unit|A7F4XZ9KQ2'

    Args:
        prefix (str): Identifier prefix (default: 'unit').
        length (int): Length of the random part (default: 10).

    Returns:
        str: A unique ID formatted as 'prefix|XXXXXXXXXX'
    """
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}|{random_part}"