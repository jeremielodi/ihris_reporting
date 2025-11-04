 
from typing import Optional, List
from pydantic import BaseModel

class Person(BaseModel):
    id: str
    

class PaginatedPerson(BaseModel):
    limit: int
    offset: int
    data: List[Person]