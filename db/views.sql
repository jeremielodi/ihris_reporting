CALL public.generate_employment_status_report();

CREATE OR REPLACE VIEW public.liste_declarative AS 

SELECT      t1.id as "IDENTIFIANT",
            t1.matricule as "MATRICULE",
			t1.fullname as "NOMS",
			t1.firstname as "NOM",
			t1.othername as "PRENOM",
			t1.gender as "SEXE",
			t1.birth_date as "DATE_DE_NAISSANCE",
			t1.birth_place as "LIEU_DE_NAISSANCE",
			t1.marital_status as "ETAT_CIVIL",
			t1.classification as "CATEGORIE_PROFESSIONNELLE",
			'' as "SPECIALITE",
			t1.job_type as "STATUT",
			t1.degree as "NIVEAU_D_ETUDE",
			t2.country_name as "PAYS",
			t2.province_name as "PROVINCE",
			t2.district_name as "DISTRICT",
			t2.facility_name as "STRICTURE",
			t1.job as "POSTE_ACTUEL",
			t1.recruitment_date as "DATE_D_INTEGRATION",
			t1.year_of_appointment as "DATE_AFFECTION",
			t1.start_service_date as "DATE_PRISE_SERVICE",
			t1.position as "POSITION_ACTUEL",
            t2.country as country_id,
            t2.district as district_id,
            t2.region as region_id,
            t2.province as province_id,
            t2.county as county_id,
            t2.health_zone as health_zone_id,
            t2.health_area as health_area_id,
            t2.facility as facility_id
        FROM z_employment_status_view t1
        LEFT JOIN (
            SELECT * 
            FROM public.get_all_org_units_table()
        ) AS t2 ON t2.node_id = t1.facility_id
        WHERE t1.facility_id IS NOT NULL;





-- view pour les norms
CREATE OR REPLACE VIEW public.norm_view AS
WITH req AS (
  SELECT
    nr.organization_unit_type_id,
    nr.classification_id,
    nr.required
  FROM public.norm_requirement nr
),
actual AS (
  SELECT
    es.facility_id,
    es.classification_id,
    COUNT(*)::int AS actual
  FROM public.z_employment_status_view es
  WHERE es.classification_id IS NOT NULL
  GROUP BY es.facility_id, es.classification_id
),
units AS (
  SELECT
    ou.id     AS organization_unit_id,
    ou.name   AS organization_unit_name,
    ou.parent AS organization_unit_parent,
    ou.type
  FROM public.organization_unit ou
),
orgtree AS (
  SELECT *
  FROM public.get_all_org_units_table()
)
SELECT
  u.organization_unit_id,
  u.organization_unit_name,
  u.organization_unit_parent,
  u.type,

  -- colonnes issues de l’arbre organisationnel
  t.*,

  r.classification_id,
  hc.name AS classification_name,

  r.required,
  COALESCE(a.actual, 0) AS actual,
  GREATEST(r.required - COALESCE(a.actual, 0), 0) AS missing,
  GREATEST(COALESCE(a.actual, 0) - r.required, 0) AS excess
FROM units u
LEFT JOIN orgtree t
  ON t.node_id = u.organization_unit_id
JOIN req r
  ON r.organization_unit_type_id = u.type
LEFT JOIN actual a
  ON a.facility_id = u.organization_unit_id
 AND a.classification_id = r.classification_id
LEFT JOIN public.hippo_classification hc
  ON hc.id = r.classification_id
ORDER BY
  t.province_name NULLS LAST,
  t.district_name NULLS LAST,
  u.organization_unit_name,
  hc.name NULLS LAST,
  r.classification_id;


-- SELECT 
-- 	province,
-- 	classification_id,
-- 	classification_name,
-- 	SUM(required) as required, 
-- 	SUM(actual) as actual, 
-- 	SUM(missing) as missing, 
-- 	SUM(excess) as excess
-- FROM norm_view
-- WHERE classification_id ='classification|38'
-- GROUP BY province, classification_id, classification_name
