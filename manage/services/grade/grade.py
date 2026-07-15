"""
Salary Grade API Endpoints
--------------------------

This module exposes CRUD and BULK IMPORT operations for HippoSalaryGrade.

Salary grades typically represent structured compensation levels
within the HR system.

Includes:
- Standard CRUD operations
- High-performance bulk import (PostgreSQL ON CONFLICT DO NOTHING)
- Entity map tracking for incremental ID generation

All endpoints require authenticated active users.
"""

from manage.models import HippoSalaryGrade, HippoEntityMap
from manage.services.grade.schemas import (
    HippoGradeRead,
    HippoGradeCreate,
    HippoGradeUpdate
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user

from sqlalchemy.dialects.postgresql import insert as pg_insert
from manage.services.entity_map import entity_map


# Initialize router for salary grade endpoints
apiRouter = APIRouter()


async def get_session() -> AsyncSession:
    """
    Provides an asynchronous database session.

    - Opens a new AsyncSession
    - Yields it during request lifecycle
    - Automatically closes it after completion
    """
    async with SessionLocal() as session:
        yield session


# -------------------------------------------------------------------
# GET ALL SALARY GRADES
# -------------------------------------------------------------------
@apiRouter.get(
    "/grades/",
    response_model=list[HippoGradeRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_grades(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all salary grades ordered alphabetically by name.

    Returns:
        List[HippoGradeRead]
    """
    result = await session.execute(
        select(HippoSalaryGrade).order_by(HippoSalaryGrade.name)
    )
    grades = result.scalars().all()
    return grades


# -------------------------------------------------------------------
# GET SALARY GRADE BY ID
# -------------------------------------------------------------------
@apiRouter.get(
    "/grades/{grade_id}",
    response_model=HippoGradeRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_Grade(grade_id: str, session: AsyncSession = Depends(get_session)):
    """
    Retrieve a specific salary grade by ID.

    Raises:
        HTTPException(404) if not found.
    """
    result = await session.execute(
        select(HippoSalaryGrade)
        .where(HippoSalaryGrade.id == grade_id)
    )
    Grade = result.scalar_one_or_none()

    if not Grade:
        raise HTTPException(status_code=404, detail="Grade not found")

    return Grade


# -------------------------------------------------------------------
# CREATE SINGLE SALARY GRADE
# -------------------------------------------------------------------
@apiRouter.post(
    "/grades/",
    response_model=HippoGradeRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_Grade(
    Grade: HippoGradeCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new salary grade.

    Process:
        1. Convert Pydantic model to dict.
        2. Generate deterministic ID: salary_grade|<name>.
        3. Insert into database.
        4. Commit and refresh.

    Returns:
        HippoGradeRead
    """
    Grade_data = Grade.model_dump()
    Grade_data['id'] = f"salary_grade|{Grade.name}"

    new_Grade = HippoSalaryGrade(**Grade_data)

    session.add(new_Grade)
    await session.commit()
    await session.refresh(new_Grade)

    return new_Grade


# -------------------------------------------------------------------
# BULK IMPORT SALARY GRADES
# -------------------------------------------------------------------
@apiRouter.post(
    "/grades/import",
    response_model=list[HippoGradeRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)]
)
async def bulk_create_classifications(
    grades: list[HippoGradeCreate],
    session: AsyncSession = Depends(get_session),
):
    """
    Bulk insert salary grades using PostgreSQL native INSERT.

    Features:
        - Efficient batch insert
        - ON CONFLICT DO NOTHING (avoids duplicates)
        - RETURNING inserted rows only
        - Maintains entity_map max_number tracking

    Raises:
        HTTPException(400) if payload is empty.

    Returns:
        List[HippoGradeRead] (only newly inserted records)
    """

    # Validate input payload
    if not grades:
        raise HTTPException(status_code=400, detail="Empty payload.")

    # Retrieve current max_number for salary_grade
    maxNumber = await entity_map.getMaxNumber("salary_grade", session)
    maxNumber = maxNumber + 1

    rows = []
    gradeId = None

    # Normalize input into list of dictionaries
    for item in grades:
        data = item.model_dump()

        # Generate sequential ID
        gradeId = f"salary_grade|{maxNumber}"
        data["id"] = gradeId

        rows.append(data)
        maxNumber += 1

    # PostgreSQL bulk insert with ON CONFLICT DO NOTHING
    stmt = (
        pg_insert(HippoSalaryGrade.__table__)
        .values(rows)
        .on_conflict_do_nothing(index_elements=["id"])
        .returning(*HippoSalaryGrade.__table__.c)
    )

    result = await session.execute(stmt)

    # Only inserted rows are returned
    inserted = result.mappings().all()

    # Update entity_map with new max number
    new_entity_map = HippoEntityMap(
        id=gradeId,
        entity_type="salary_grade",
        max_number=maxNumber
    )
    session.add(new_entity_map)

    # Single commit for entire batch
    await session.commit()

    # Convert MappingRow to dict for Pydantic response
    return [dict(row) for row in inserted]


# -------------------------------------------------------------------
# UPDATE SALARY GRADE
# -------------------------------------------------------------------
@apiRouter.put("/grades/{grade_id}", response_model=HippoGradeRead)
async def update_Grade(
    grade_id: str,
    Grade: HippoGradeUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing salary grade.

    - Updates only provided (non-null) fields.
    - Returns updated object.
    """
    result = await session.execute(
        select(HippoSalaryGrade)
        .where(HippoSalaryGrade.id == grade_id)
    )
    existing_Grade = result.scalar_one_or_none()

    if not existing_Grade:
        raise HTTPException(status_code=404, detail="Grade not found")

    # Apply partial update
    for key, value in Grade.model_dump().items():
        if value is not None:
            setattr(existing_Grade, key, value)

    await session.commit()
    await session.refresh(existing_Grade)

    return existing_Grade


# -------------------------------------------------------------------
# DELETE SALARY GRADE
# -------------------------------------------------------------------
@apiRouter.delete("/grades/{grade_id}")
async def delete_Grade(
    grade_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a salary grade by ID.

    Raises:
        HTTPException(404) if not found.

    Returns:
        Success confirmation message.
    """
    result = await session.execute(
        select(HippoSalaryGrade)
        .where(HippoSalaryGrade.id == grade_id)
    )
    existing_Grade = result.scalar_one_or_none()

    if not existing_Grade:
        raise HTTPException(status_code=404, detail="Grade not found")

    await session.delete(existing_Grade)
    await session.commit()

    return {"detail": "Grade deleted successfully"}