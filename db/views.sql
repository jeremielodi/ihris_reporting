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