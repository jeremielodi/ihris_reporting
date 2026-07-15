from sqlalchemy import text

async def get_OrganisationUnit(id:str,db):
    result = await db.execute(text("""
        SELECT *
        FROM organization_unit
        WHERE id= :id
    """), { "id": id})
    rows = result.mappings().all()
    if len(rows) == 0:
        return None
    return rows[0]


# get all organization_units tree from parent id
async def get_OrganisationUnitTree(parentId:str,db):
    
    result = await db.execute(text("""
        WITH RECURSIVE tree AS (

            SELECT
                id,
                name,
                parent,
                1 AS level,
                ARRAY[id::text] AS path_ids,
                name::text AS path_text
            FROM organization_unit
            WHERE id= :parentId

            UNION ALL

            SELECT 
                c.id,
                c.name,
                c.parent,
                t.level + 1,
                t.path_ids || c.id,
                t.path_text || ' / ' || c.name
            FROM organization_unit c
            JOIN tree t ON c.parent = t.id
            WHERE c.id <> ALL(t.path_ids)
        )
        SELECT id, name, parent, level, path_text
        FROM tree
        ORDER BY path_ids;
    """), {"parentId": parentId})
    return result.mappings().all()
