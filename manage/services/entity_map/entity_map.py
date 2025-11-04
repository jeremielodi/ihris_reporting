

from manage.models import HippoEntityMap
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user
from sqlalchemy import text


async def getMaxNumber(type: str,  db: AsyncSession):
    result = await db.execute(text(f"""
        SELECT MAX(max_number) as max_number
        FROM hippo_entity_map
        WHERE entity_type='{type}'
    """))
    rows = result.mappings().all()   # returns list of dict-like rows
    if (rows[0].max_number == None):
        return 0
    return rows[0].max_number

