"""
Entity Map Utility Functions
----------------------------

This module provides helper functions related to HippoEntityMap.

HippoEntityMap is used to:
- Track incremental numeric identifiers per entity type
- Maintain sequential ID generation logic
- Support bulk import operations with controlled numbering
"""

from manage.models import HippoEntityMap
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user
from sqlalchemy import text


async def getMaxNumber(type: str, db: AsyncSession):
    """
    Retrieve the current maximum number for a given entity type.

    This function is typically used before generating new sequential IDs
    (e.g., salary_grade|1, salary_grade|2, etc.).

    Process:
        1. Query hippo_entity_map table.
        2. Get MAX(max_number) for the specified entity_type.
        3. If no record exists, return 0.
        4. Otherwise return the maximum number found.

    Args:
        type (str): Entity type identifier (e.g., "salary_grade").
        db (AsyncSession): Active database session.

    Returns:
        int: Current maximum number for that entity type.
             Returns 0 if no entry exists.
    """

    result = await db.execute(
        text("""
            SELECT MAX(max_number) as max_number
            FROM hippo_entity_map
            WHERE entity_type = :type
        """),
        {"type": type})

    # Convert result into mapping-style rows (dict-like objects)
    rows = result.mappings().all()

    # If no records found or max_number is NULL → return 0
    if rows[0].max_number is None:
        return 0

    return rows[0].max_number