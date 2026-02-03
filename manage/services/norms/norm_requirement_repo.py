# manage/repositories/norm_requirement_repo.py
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from manage.models import NormRequirement
from sqlalchemy import text

class NormRequirementRepository:

    @staticmethod
    async def create(db: AsyncSession, org_type: str, classification_id: str, required: int):
        result = await db.execute(text("""
            INSERT INTO norm_requirement (organization_unit_type_id, classification_id, required)
            VALUES (:t, :c, :r)
            RETURNING id, organization_unit_type_id, classification_id, required
        """), {"t": org_type, "c": classification_id, "r": required})
        await db.commit()
        return result.mappings().first()

    @staticmethod
    async def get(db: AsyncSession, org_type: str, classification_id: str):
        stmt = select(NormRequirement).where(
            NormRequirement.organization_unit_type_id == org_type,
            NormRequirement.classification_id == classification_id
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    @staticmethod
    async def find_by_id(db: AsyncSession, id: str):
        result = await db.execute(text("""
            SELECT
              id::text AS id,
              organization_unit_type_id,
              classification_id,
              required
            FROM norm_requirement
            WHERE id = :id
        """), {"id": id})

        return result.mappings().first()

    @staticmethod
    async def list_all(db):
        result = await db.execute(text("""
            SELECT 
                nr.id,  
                nr.organization_unit_type_id, 
                nr.classification_id,
                cl.name as classification_name,
                ot.name as organization_unit_type_name,
                nr.required
            FROM norm_requirement nr
            JOIN hippo_classification cl ON cl.id = nr.classification_id
            JOIN organization_unit_type ot ON ot.id = nr.organization_unit_type_id
            ORDER BY nr.organization_unit_type_id, nr.classification_id
        """))
        return result.mappings().all() 

    @staticmethod
    async def update(db: AsyncSession, id:str, org_type: str, classification_id: str, required: int):
        result = await db.execute(text("""
            UPDATE norm_requirement
            SET required = :r,
                organization_unit_type_id= :t,
                classification_id=:c
            WHERE id = :id
            RETURNING id, organization_unit_type_id, classification_id, required
        """), {"id": id, "t": org_type, "c": classification_id, "r": required})
        await db.commit()
        return result.mappings().first()


    @staticmethod
    async def delete(db: AsyncSession, org_type: str, classification_id: str):
        stmt = delete(NormRequirement).where(
            NormRequirement.organization_unit_type_id == org_type,
            NormRequirement.classification_id == classification_id
        )
        await db.execute(stmt)
        await db.commit()
