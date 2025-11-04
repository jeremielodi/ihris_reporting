

from manage.models import HippoPaymentFrequency
from manage.services.payment_frequency.schemas import HippoPaymentFrequencyRead, HippoPaymentFrequencyCreate, HippoPaymentFrequencyUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user


apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all payment_frequencys
@apiRouter.get("/payment_frequencies/", response_model=list[HippoPaymentFrequencyRead], dependencies=[Depends(get_current_active_user)],)
async def get_payment_frequencys(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoPaymentFrequency).order_by(HippoPaymentFrequency.name))
    payment_frequencys = result.scalars().all()
    return payment_frequencys


# find a Payment_frequency by id
@apiRouter.get("/payment_frequencies/{payment_frequency_id}", response_model=HippoPaymentFrequencyRead, dependencies=[Depends(get_current_active_user)],)
async def get_Payment_frequency(payment_frequency_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoPaymentFrequency).where(HippoPaymentFrequency.id == payment_frequency_id))
    Payment_frequency = result.scalar_one_or_none()
    if not Payment_frequency:
        raise HTTPException(status_code=404, detail="Payment_frequency not found")
    return Payment_frequency

@apiRouter.post("/payment_frequencies/", response_model=HippoPaymentFrequencyRead, dependencies=[Depends(get_current_active_user)])
async def create_Payment_frequency(
    Payment_frequency:HippoPaymentFrequencyCreate,
    session: AsyncSession = Depends(get_session),
):
    Payment_frequency_data = Payment_frequency.dict()  # get dict from pydantic model
    Payment_frequency_data['id'] = f"payment_frequency|{Payment_frequency.name}"
    
    new_Payment_frequency = HippoPaymentFrequency(**Payment_frequency_data)
    session.add(new_Payment_frequency)
    await session.commit()
    await session.refresh(new_Payment_frequency)
    return new_Payment_frequency

# update an existing Payment_frequency
@apiRouter.put("/payment_frequencies/{payment_frequency_id}", response_model=HippoPaymentFrequencyRead)
async def update_Payment_frequency(payment_frequency_id: str, Payment_frequency:HippoPaymentFrequencyUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoPaymentFrequency).where(HippoPaymentFrequency.id == payment_frequency_id))
    existing_Payment_frequency = result.scalar_one_or_none()
    if not existing_Payment_frequency:
        raise HTTPException(status_code=404, detail="Payment_frequency not found")
    
    for key, value in Payment_frequency.dict().items():
        if value is not None:
            setattr(existing_Payment_frequency, key, value)
    
    await session.commit()
    await session.refresh(existing_Payment_frequency)
    return existing_Payment_frequency  

# delete a Payment_frequency
@apiRouter.delete("/payment_frequencies/{payment_frequency_id}")
async def delete_Payment_frequency(payment_frequency_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoPaymentFrequency).where(HippoPaymentFrequency.id == payment_frequency_id))
    existing_Payment_frequency = result.scalar_one_or_none()
    if not existing_Payment_frequency:
        raise HTTPException(status_code=404, detail="Payment_frequency not found")
    
    await session.delete(existing_Payment_frequency)
    await session.commit()
    return {"detail": "Payment_frequency deleted successfully"}


