from pydantic import BaseModel
from typing import Optional

class RequestionParamers(BaseModel):
    name: Optional[str] = None  # Use Optional for id, as it may not be set on creation
    value: list | str| int | float = None
