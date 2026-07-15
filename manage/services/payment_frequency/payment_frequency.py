# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# ORM model
from manage.models import HippoPaymentFrequency

# Pydantic schemas (validation + serialization)
from manage.services.payment_frequency.schemas import (
    HippoPaymentFrequencyRead,
    HippoPaymentFrequencyCreate,
    HippoPaymentFrequencyUpdate
)

# Async DB session
from sqlalchemy.ext.asyncio import AsyncSession

# FastAPI utilities
from fastapi import APIRouter, Depends, HTTPException

# SQLAlchemy ORM query builder
from sqlalchemy.future import select

# Database session factory
from manage.database import SessionLocal, engine

# Authentication dependency
from endpoints.user_api import get_current_active_user


# Create API router
apiRouter = APIRouter()


# ---------------------------------------------------------
# Dependency: Get Async Database Session
# ---------------------------------------------------------
async def get_session() -> AsyncSession:
    """
    Provides an async database session.
    Ensures proper open/close lifecycle handling.
    """
    async with SessionLocal() as session:
        yield session


# =========================================================
# GET ALL PAYMENT FREQUENCIES
# =========================================================

@apiRouter.get(
    "/payment_frequencies/",
    response_model=list[HippoPaymentFrequencyRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_payment_frequencies(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all payment frequencies ordered alphabetically by name.

    Example:
    - Monthly
    - Weekly
    - Biweekly
    - Quarterly
    """
    result = await session.execute(
        select(HippoPaymentFrequency).order_by(HippoPaymentFrequency.name)
    )

    payment_frequencies = result.scalars().all()
    return payment_frequencies


# =========================================================
# GET PAYMENT FREQUENCY BY ID
# =========================================================

@apiRouter.get(
    "/payment_frequencies/{payment_frequency_id}",
    response_model=HippoPaymentFrequencyRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_payment_frequency(
    payment_frequency_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a specific payment frequency by ID.
    Returns 404 if not found.
    """

    result = await session.execute(
        select(HippoPaymentFrequency).where(
            HippoPaymentFrequency.id == payment_frequency_id
        )
    )

    payment_frequency = result.scalar_one_or_none()

    if not payment_frequency:
        raise HTTPException(status_code=404, detail="Payment frequency not found")

    return payment_frequency


# =========================================================
# CREATE PAYMENT FREQUENCY
# =========================================================

@apiRouter.post(
    "/payment_frequencies/",
    response_model=HippoPaymentFrequencyRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_payment_frequency(
    payment_frequency: HippoPaymentFrequencyCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new payment frequency.

    ID format:
        payment_frequency|<name>

    NOTE:
    Consider adding uniqueness validation for name.
    """

    # Convert Pydantic model to dictionary
    payment_frequency_data = payment_frequency.model_dump()

    # Generate ID
    payment_frequency_data['id'] = f"payment_frequency|{payment_frequency.name}"

    # Create ORM instance
    new_payment_frequency = HippoPaymentFrequency(**payment_frequency_data)

    session.add(new_payment_frequency)
    await session.commit()
    await session.refresh(new_payment_frequency)

    return new_payment_frequency


# =========================================================
# UPDATE PAYMENT FREQUENCY
# =========================================================

@apiRouter.put(
    "/payment_frequencies/{payment_frequency_id}",
    response_model=HippoPaymentFrequencyRead
)
async def update_payment_frequency(
    payment_frequency_id: str,
    payment_frequency: HippoPaymentFrequencyUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing payment frequency.

    - Only non-null fields are updated.
    - Returns 404 if not found.
    """

    result = await session.execute(
        select(HippoPaymentFrequency).where(
            HippoPaymentFrequency.id == payment_frequency_id
        )
    )

    existing_payment_frequency = result.scalar_one_or_none()

    if not existing_payment_frequency:
        raise HTTPException(status_code=404, detail="Payment frequency not found")

    for key, value in payment_frequency.model_dump().items():
        if value is not None:
            setattr(existing_payment_frequency, key, value)

    await session.commit()
    await session.refresh(existing_payment_frequency)

    return existing_payment_frequency


# =========================================================
# DELETE PAYMENT FREQUENCY
# =========================================================

@apiRouter.delete("/payment_frequencies/{payment_frequency_id}")
async def delete_payment_frequency(
    payment_frequency_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a payment frequency by ID.

    WARNING:
    If referenced in salary or contract records,
    deletion should be prevented or replaced by soft delete.
    """

    result = await session.execute(
        select(HippoPaymentFrequency).where(
            HippoPaymentFrequency.id == payment_frequency_id
        )
    )

    existing_payment_frequency = result.scalar_one_or_none()

    if not existing_payment_frequency:
        raise HTTPException(status_code=404, detail="Payment frequency not found")

    await session.delete(existing_payment_frequency)
    await session.commit()

    return {"detail": "Payment frequency deleted successfully"}