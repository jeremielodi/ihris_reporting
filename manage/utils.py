import os
from datetime import datetime
from pathlib import Path
import random
import string
import re
import unicodedata

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


def make_id(text: str) -> str:
    """
    Convert a string into a safe identifier:
    - removes accents (é -> e)
    - lowercases
    - replaces spaces with underscores
    - replaces any non [a-z0-9_] with underscores
    - collapses multiple underscores
    - trims leading/trailing underscores
    """
    if text is None:
        return ""

    # 1) trim + lowercase
    s = text.strip().lower()

    # 2) remove accents
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))

    # 3) spaces -> underscores
    s = re.sub(r"\s+", "_", s)

    # 4) keep only a-z, 0-9, underscore (everything else -> underscore)
    s = re.sub(r"[^a-z0-9_]+", "_", s)

    # 5) collapse underscores + trim
    s = re.sub(r"_+", "_", s).strip("_")

    return s