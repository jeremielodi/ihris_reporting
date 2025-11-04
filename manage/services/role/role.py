from manage.models import Base, HippoRole,  HippoEntityMap, HippoUser
from manage.services.role.schemas import AssignRolesPayload, HippoRoleRead, HippoRoleCreate, HippoRoleUpdate, HippoRoleActionCreate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.future import select
from sqlalchemy import  text
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user
import  models.usercrud as user_crud
from manage.services.entity_map import entity_map
from typing import Any, Dict, List, Annotated
import uuid
from fastapi.responses import JSONResponse

apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@apiRouter.get('/testing')
def testing():
    return JSONResponse({"description": "tesing route"})

# Get all roles
@apiRouter.get("/roles/", response_model=list[HippoRoleRead], 
                    dependencies=[Depends(get_current_active_user)],)
async def get_roles(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoRole))
    roles = result.scalars().all()
    return roles


# find a role by id
@apiRouter.get("/roles/{role_id}", response_model=HippoRoleRead,  dependencies=[Depends(get_current_active_user)],)
async def get_role(role_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoRole).where(HippoRole.id == role_id).order_by(HippoRole.name))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="role not found")
    return role



@apiRouter.post(
    "/roles/assignRoles",
    dependencies=[Depends(get_current_active_user)],
)
async def assignRoles(
    data: AssignRolesPayload,
    session: AsyncSession = Depends(get_session),
):
    # 1) Ensure user exists (adjust table name if yours differs)
    exists = await session.execute(
        text("SELECT 1 FROM hippo_user WHERE id = :id"),
        {"id": data.user_id},
    )
    if exists.scalar() is None:
        raise HTTPException(status_code=404, detail="User not found")

    # 2) Normalize role_ids: drop empties & duplicates (preserve order)
    role_ids = [rid for rid in data.role_ids if rid]
    role_ids = list(dict.fromkeys(role_ids))

    # 3) Transaction: delete old, insert new

        # delete current assignments
    await session.execute(
        text("DELETE FROM public.hippo_user_role WHERE user_id = :user_id"), {"user_id": data.user_id},
    )

        # bulk insert new ones (if any)
    if role_ids:
        rows = [
            {"uuid": str(uuid.uuid4()), "user_id": data.user_id, "role_id": rid}
        for rid in role_ids
        ]
        await session.execute(
                text("""
                    INSERT INTO public.hippo_user_role (uuid, user_id, role_id)
                    VALUES (:uuid, :user_id, :role_id)
                """),
                rows,  # executemany
        )

    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    return {"user_id": data.user_id, "roles_assigned": role_ids}

    
@apiRouter.get("/roles/userRoles/{user_id}", response_model=List, dependencies=[Depends(get_current_active_user)],)
async def getUserRoles(user_id:str, session: AsyncSession = Depends(get_session)):
    Sql = """

    SELECT q.* FROM (
        SELECT r.id, r.name , 1 as affected
        FROM hippo_role r
        JOIN hippo_user_role as usr ON usr.role_id = r.id
        WHERE usr.user_id =:user_id
        
        UNION ALL

        SELECT r.id , r.name , 0 as affected
        FROM hippo_role r WHERE r.id NOT IN (
          SELECT role_id
          FROM   hippo_user_role
          WHERE  user_id =:user_id
        )
      )as q
      ORDER BY q.name

    """
    query = await session.execute(text(Sql), {'user_id': user_id})
    # RowMapping -> make them mutable dicts
    return query.mappings().all()


# use hippo_user_role table to insert data
@apiRouter.post("/roles/modulesForUser/{user_id}")
async def assign_role_to_user(
    user_id: str,
    role_ids: List[str],
    session: AsyncSession = Depends(get_session),
):
    # 1) Validate user exists
    result = await session.execute(select(HippoUser).where(HippoUser.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    # 2) Delete existing mappings
    await session.execute(
        text("DELETE FROM hippo_user_role WHERE user_id = :user_id"),
        {"user_id": user_id},
    )

    # 3) Insert new mappings
    if role_ids:
        insert_values = [{'uuid': uuid.uuid4(), "user_id": user_id, "role_id": role_id} for role_id in role_ids]
        await session.execute(
            text("""
                INSERT INTO hippo_user_role (uuid, user_id, role_id)
                VALUES (:uuid, :user_id, :role_id)
            """),
            insert_values,
        )

    await session.commit()
    return {"detail": "roles assigned to user successfully"}



# get modules and pages for a user by user id
@apiRouter.get("/roles/userModules/{user_id}")
async def get_modules_for_user(
    user_id: str,
    session: AsyncSession = Depends(get_session),
):
    # 1) Load modules
    mod_res = await session.execute(text("""
        SELECT *
        FROM public.hippo_module
        ORDER BY label
    """))
    # RowMapping -> make them mutable dicts
    modules: List[Dict[str, Any]] = [dict(r) for r in mod_res.mappings().all()]

    # 2) Per-module pages with affected flag, use hippo_user_role to know user's roles and modules
    page_sql = text("""
        SELECT
            p.code,
            p.label,
            p.url,
            p.is_tree_item,
            p.module_id,
            CASE WHEN rp.role_id IS NULL THEN 0 ELSE 1 END AS affected
        FROM public.hippo_module_page AS p
        JOIN public.hippo_role_page AS rp
          ON rp.page_code = p.code
         AND rp.role_id IN (
             SELECT ur.role_id
             FROM public.hippo_user_role AS ur
             WHERE ur.user_id = :user_id
         )
        WHERE p.module_id = :module_id
        ORDER BY p.label
    """)
   
    for m in modules:
        pages_res = await session.execute(page_sql, {"user_id": user_id, "module_id": m["id"]})
        m["pages"] = pages_res.mappings().all()  # list[RowMapping], fine for JSON response 
    return modules


@apiRouter.get("/roles/actions/{role_id}")
async def get_role_actions(
    role_id: str,
    session: AsyncSession = Depends(get_session),
):
    
    page_sql = text("""
        SELECT a.id, a.description, CASE WHEN (s.affected IS NULL) THEN 0 ELSE s.affected END As affected
        FROM public.hippo_actions a
        LEFT JOIN (
            SELECT  actions_id , 1 as affected
            FROM public.hippo_role_actions ra
            JOIN public.hippo_role ro ON ra.role_id = ro.id
            WHERE ra.role_id =:role_id
        )s ON s.actions_id = a.id
    """)

    pages_res = await session.execute(page_sql, {"role_id": role_id})
    return pages_res.mappings().all() 




@apiRouter.post("/roles/actions")
async def get_role_actions(
    data: HippoRoleActionCreate,
    session: AsyncSession = Depends(get_session),
):
    
    page_sql = text("DELETE FROM  public.hippo_role_actions  WHERE role_id =:role_id ")

    pages_res = await session.execute(page_sql, {"role_id": data.role_id})
    for action_id in data.action_ids:
        sql= """
            INSERT INTO  public.hippo_role_actions(uuid, role_id, actions_id)
            values(:uuid, :role_id, :action_id)
        """
        await session.execute(sql, {"uuid": uuid.uuid4(), "role_id": data.role_id, 'action_id': action_id})

    await session.commit()
    return True

@apiRouter.get("/roles/actions/user/{action_id}")
async def has_action(
    action_id: int,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user)
):
    
    page_sql = text("""
        SELECT count(ra.uuid) as nbr
        FROM public.hippo_role_actions ra
        JOIN public.hippo_user_role as ur ON ur.role_id = ra.role_id
        WHERE actions_id =:action_id AND ur.user_id = :user_id
    """)

    pages_res = await session.execute(page_sql, {"action_id":action_id, "user_id": current_user_id})
    
    result = pages_res.mappings().all()
    return result[0]['nbr'] > 0


@apiRouter.get("/roles/modulesForRole/{role_id}")
async def get_modules_for_role(
    role_id: str,
    session: AsyncSession = Depends(get_session),
):
    # 1) Load modules
    mod_res = await session.execute(text("""
        SELECT *
        FROM public.hippo_module
        ORDER BY label
    """))
    # RowMapping -> make them mutable dicts
    modules: List[Dict[str, Any]] = [dict(r) for r in mod_res.mappings().all()]

    # 2) Per-module pages with affected flag (LEFT JOIN is faster than UNION/NOT IN)
    page_sql = text("""
        SELECT
            p.code,
            p.label,
            p.url,
            p.module_id,
            CASE WHEN rp.role_id IS NULL THEN 0 ELSE 1 END AS affected
        FROM public.hippo_module_page AS p
        LEFT JOIN public.hippo_role_page AS rp
          ON rp.page_code = p.code
         AND rp.role_id   = :role_id
        WHERE p.module_id = :module_id
        ORDER BY p.label
    """)

    for m in modules:
        pages_res = await session.execute(page_sql, {"role_id": role_id, "module_id": m["id"]})
        m["pages"] = pages_res.mappings().all()  # list[RowMapping], fine for JSON response

    return modules


@apiRouter.post("/roles/affectPages")
async def affect_pages_to_role(
    data: Dict[str, Any],
    session: AsyncSession = Depends(get_session),
):
    role_id = data.get("role_id")
    page_codes = data.get("pageCodes", [])
    if not role_id:
        raise HTTPException(status_code=400, detail="role_id is required")

    # 1) Validate role exists
    result = await session.execute(select(HippoRole).where(HippoRole.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="role not found")

    # 2) Delete existing mappings
    await session.execute(
        text("DELETE FROM public.hippo_role_page WHERE role_id = :role_id"),
        {"role_id": role_id},
    )

    # 3) Insert new mappings
    if page_codes:
        insert_values = [{'uuid': uuid.uuid4(), "role_id": role_id, "page_code": code} for code in page_codes]
        await session.execute(
            text("""
                INSERT INTO public.hippo_role_page (uuid, role_id, page_code)
                VALUES (:uuid, :role_id, :page_code)
            """),
            insert_values,
        )

    await session.commit()
    return {"detail": "pages affected to role successfully"}

# create a new role
@apiRouter.post("/roles/", response_model=HippoRoleRead,  dependencies=[Depends(get_current_active_user)],)
async def create_role(
    role: HippoRoleCreate, 
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),):

    result = await session.execute(select(HippoRole).where(HippoRole.name == role.name))
    existing_role = result.scalar_one_or_none()
    if existing_role:
        raise HTTPException(status_code=409, detail="role alread exists")
    

    maxNumber = await entity_map.getMaxNumber("role", session)
    maxNumber = maxNumber + 1
    role_data = role.dict()  # get dict from pydantic model
    role_data['id'] = f"role|{maxNumber}"
    role_data['created_by'] = current_user_id
    new_role = HippoRole(**role_data)
    session.add(new_role)

    new_entity_map = HippoEntityMap(id=  role_data['id'], entity_type="role", max_number=maxNumber)
    session.add(new_entity_map)
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    await session.refresh(new_role)
    return new_role

# update an existing role
@apiRouter.put("/roles/{role_id}", response_model=HippoRoleRead,  dependencies=[Depends(get_current_active_user)],)
async def update_role(role_id: str, role: HippoRoleUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoRole).where(HippoRole.id == role_id))
    existing_role = result.scalar_one_or_none()
    if not existing_role:
        raise HTTPException(status_code=404, detail="role not found")
    
    for key, value in role.dict().items():
        if value is not None and key != 'created':
            setattr(existing_role, key, value)
    
    await session.commit()
    await session.refresh(existing_role)
    return existing_role  

# delete a role
@apiRouter.delete("/roles/{role_id}",  dependencies=[Depends(get_current_active_user)],)
async def delete_role(role_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoRole).where(HippoRole.id == role_id))
    existing_role = result.scalar_one_or_none()
    if not existing_role:
        raise HTTPException(status_code=404, detail="role not found")
    
    await session.delete(existing_role)
    await session.commit()
    return {"detail": "role deleted successfully"}