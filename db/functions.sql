
CREATE OR REPLACE FUNCTION public.get_all_org_units_table(
	)
    RETURNS TABLE(
      node_id text, 
      node_level text,
      country_name text,
      country text,
      province_name text,
      province text,
      region_name text,
      region text,
      district_name text,
      district text,
      county_name text,
      county text,
	    health_zone_name text,
      health_zone text,
      health_area_name text,
      health_area text,
      facility_name text,
      facility text
    ) 
    LANGUAGE 'sql'
    COST 100
    STABLE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
WITH RECURSIVE org_hierarchy AS (
  -- Start from ANY node (facility, district, region, province)
  SELECT
    id,
    name,
    parent,
    level,
    id AS node_id,
    name AS node_name,
    level AS node_level,
    CASE WHEN level = 'facility' THEN id ELSE NULL END AS facility_id,
    CASE WHEN level = 'facility' THEN name ELSE NULL END AS facility_name,
	
	  CASE WHEN level = 'county' THEN id ELSE NULL END AS county_id,
    CASE WHEN level = 'county' THEN name ELSE NULL END AS county_name,
	
	
	 CASE WHEN level = 'health_zone' THEN id ELSE NULL END AS health_zone_id,
   CASE WHEN level = 'health_zone' THEN name ELSE NULL END AS health_zone_name,
	
	 CASE WHEN level = 'health_area' THEN id ELSE NULL END AS health_area_id,
   CASE WHEN level = 'health_area' THEN name ELSE NULL END AS health_area_name,
	
    CASE WHEN level = 'district' THEN id ELSE NULL END AS district_id,
    CASE WHEN level = 'district' THEN name ELSE NULL END AS district_name,
    CASE WHEN level = 'region' THEN id ELSE NULL END AS region_id,
    CASE WHEN level = 'region' THEN name ELSE NULL END AS region_name,
    CASE WHEN level = 'province' THEN id ELSE NULL END AS province_id,
    CASE WHEN level = 'province' THEN name ELSE NULL END AS province_name,
	CASE WHEN level = 'country' THEN id ELSE NULL END as country_id,
    CASE WHEN level = 'country' THEN name ELSE NULL END as country_name
  FROM public.organization_unit

  UNION ALL

  -- Walk up via parent to collect hierarchy
  SELECT
    p.id,
    p.name,
    p.parent,
    p.level,
    h.node_id,
    h.node_name,
    h.node_level,
    CASE WHEN p.level = 'facility' THEN p.id ELSE h.facility_id END,
    CASE WHEN p.level = 'facility' THEN p.name ELSE h.facility_name END,
	
	CASE WHEN p.level = 'county' THEN p.id ELSE h.county_id END,
    CASE WHEN p.level = 'county' THEN p.name ELSE h.county_name END,
	

	 CASE WHEN p.level = 'health_zone' THEN p.id ELSE h.health_zone_id END,
    CASE WHEN p.level = 'health_zone' THEN p.name ELSE h.health_zone_name END,
	

	 CASE WHEN p.level = 'health_area' THEN p.id ELSE h.health_area_id END,
    CASE WHEN p.level = 'health_area' THEN p.name ELSE h.health_area_name END,
	
	
    CASE WHEN p.level = 'district' THEN p.id ELSE h.district_id END,
    CASE WHEN p.level = 'district' THEN p.name ELSE h.district_name END,
    CASE WHEN p.level = 'region' THEN p.id ELSE h.region_id END,
    CASE WHEN p.level = 'region' THEN p.name ELSE h.region_name END,
    CASE WHEN p.level = 'province' THEN p.id ELSE h.province_id END,
    CASE WHEN p.level = 'province' THEN p.name ELSE h.province_name END,
	CASE WHEN p.level = 'country' THEN p.id ELSE h.country_id END,
    CASE WHEN p.level = 'country' THEN p.name ELSE h.country_name END
  FROM public.organization_unit p
  JOIN org_hierarchy h ON p.id = h.parent
)

SELECT DISTINCT
  node_id,
  node_level,
  country_name,
  country_id as country,
  province_name,
  province_id as province,
  region_name,
  region_id as region,
  district_name,
  district_id as district,
  county_name,
  county_id as county,
  health_zone_name,
  health_zone_id as health_zone,
  health_area_name,
  health_area_id as health_area,
  facility_name,
  facility_id as facility
FROM org_hierarchy
WHERE country_id  IS NOT NULL
$BODY$;



DROP FUNCTION IF EXISTS public.is_null(text);
CREATE OR REPLACE FUNCTION public.is_null(val text)
RETURNS INTEGER
LANGUAGE sql
IMMUTABLE
PARALLEL SAFE
AS $$
 SELECT CASE WHEN((val IS NULL) OR (btrim(val) = '')) IS  TRUE THEN 1 ELSE 0 END
$$;
