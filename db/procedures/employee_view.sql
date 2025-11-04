-- PROCEDURE: public.generate_employment_status_report()

-- DROP PROCEDURE IF EXISTS public.generate_employment_status_report();


CREATE OR REPLACE PROCEDURE public.generate_employment_status_report()
LANGUAGE 'plpgsql'
AS $BODY$
DECLARE
	rec RECORD;
	_status RECORD;
	v_job_id text;
	v_job text;
	v_job_type_id text;
	v_job_type text;
    v_grade_id      text;
	v_grade      text;
    v_cadre_id      text;
	v_cadre      text;
	v_degree text;
	v_degree_id text;
	v_classification_id      text;
	v_classification      text;
	v_employment_date      TIMESTAMP;
	v_start_service_date  TIMESTAMP;
	v_facility_id      text;
	v_salary    int;
	v_allowance     int;
	v_ref_engagement      text;
	v_position_decision_ref      text;
	v_marital_status      text;
	v_employee_status      text;
	v_employee_status_id text;
	v_identified int;
	v_matricule text;
	v_mobile_phone  text;
	v_address  text;
	
		   
BEGIN
  CREATE TABLE IF NOT EXISTS z_employment_status_view(
  id                      VARCHAR(255) PRIMARY KEY,
  fullname                VARCHAR(150),
  firstname               VARCHAR(50),
  surname                 VARCHAR(50),
  othername               VARCHAR(50),
  residence               text,
  gender                  VARCHAR(50),
  birth_date              date,
  birth_place             VARCHAR(255),
  recruitment_date              date,
  birth_date_y            int,
  dependents              int,
  marital_status          VARCHAR(50),
  mobile_phone            text,
  address                 text,
  ref_on_employment       text,
  year_of_appointment     date,
  start_service_date      date,
  year_of_appointment_y   int,
  matricule               text,
  ref_engagement          text,
  degree                  text,
  degree_id                  text,
  "position"            text, 
  cadre_id                text,
  cadre                   text,
  classification_id       text,
  classification          text,
  job_id                  text,
  job                     text,
  job_type_id             text,
  job_type                text,
  salary_grade_id         text,
  salary_grade            text,
  salaire                 numeric,
  prime                   numeric,
  identifie               text,
  facility_id             text
);

CREATE INDEX IF NOT EXISTS fk_status_view_facility
    ON z_employment_status_view (facility_id);

DELETE FROM z_employment_status_view;

 INSERT INTO z_employment_status_view(id, fullname, firstname, surname, othername, gender, residence, dependents, birth_date, birth_place,  birth_date_y, recruitment_date)
 SELECT 
   id, 
 (COALESCE(lastname, '') || ' ' || COALESCE(firstname, '') || ' ' || COALESCE(middlename, '')) AS fullname,
 lastname,
 middlename, 
 firstname,
 gender, 
 residence,
 dependents,
 birthdate,
 birthplace,
 EXTRACT(YEAR FROM birthdate)::int,
 recruitment_date
 FROM hippo_person;
 
 
 
 FOR rec IN SELECT id, degree, marital_status FROM hippo_person LOOP
        select grade, cadre, classification, job,job_type, employment_date,  start_service_date,
	       facility_id, salary, allowance, ref_engagement, 
	       position_decision_ref, identified, employee_status 
		from hippo_employment_status_info
		INTO v_grade_id, v_cadre_id, v_classification_id, v_job_id, v_job_type_id, v_employment_date, v_start_service_date,
	       v_facility_id, v_salary, v_allowance, v_ref_engagement, 
	       v_position_decision_ref, v_identified, v_employee_status_id
		WHERE person_id=rec.id
		ORDER BY employment_date DESC
		LIMIT 1;
		
		SELECT name 
		FROM hippo_salary_grade 
		INTO v_grade
		WHERE id= v_grade_id;
		
		SELECT title 
		FROM hippo_job
		INTO v_job
		WHERE id= v_job_id;
		
		SELECT name 
		FROM hippo_job_type
		INTO v_job_type
		WHERE id= v_job_type_id;


		SELECT name 
		FROM hippo_classification
		INTO v_classification
		WHERE id= v_classification_id;
		
		SELECT name 
		FROM hippo_cadre
		INTO v_cadre
		WHERE id= v_cadre_id;
		
		SELECT name 
		FROM hippo_degree
		INTO v_degree
		WHERE id= rec.degree;
		
		select name
		FROM  public.hippo_marital_status
		INTO v_marital_status
		WHERE id = rec.marital_status;

		SELECT name 
		FROM hippo_employee_status
		INTO v_employee_status
		WHERE id= v_employee_status_id;
		
		SELECT number 
		FROM hippo_person_identification
		INTO v_matricule
		WHERE person_id = rec.id
		LIMIT 1;
		
		SELECT mobile_phone, address 
		FROM hippo_contact
		INTO v_mobile_phone, v_address
		WHERE person_id = rec.id
		LIMIT 1;
		
		
	
		
		UPDATE z_employment_status_view
		SET  cadre_id = v_cadre_id,
			cadre = v_cadre,
			job = v_job,
			job_id = v_job_id,
			job_type = v_job_type,
			job_type_id = v_job_type_id,

			degree=v_degree,
			degree_id=rec.degree,
			classification_id = v_classification_id,
			classification = v_classification,
			salary_grade_id = v_grade_id,
			salary_grade = v_grade,
			year_of_appointment = v_employment_date,
			start_service_date = v_start_service_date,
			year_of_appointment_y = EXTRACT(YEAR FROM v_employment_date)::int,
			facility_id = v_facility_id,
			salaire = v_salary,
			prime = v_allowance,
			ref_engagement = v_ref_engagement,
			ref_on_employment = v_position_decision_ref,
			marital_status = v_marital_status,
			identifie = v_identified,
			matricule = v_matricule,
			position = v_employee_status,
			mobile_phone = v_mobile_phone,
			address = v_address
		WHERE id = rec.id;
			
 END LOOP;

END
$BODY$;