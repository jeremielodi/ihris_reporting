--
-- PostgreSQL database dump
--

-- Dumped from database version 15.1
-- Dumped by pg_dump version 15.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


SET default_tablespace = '';

SET default_table_access_method = heap;


CREATE TABLE public.setting (
    id  integer NOT NULL PRIMARY KEY,
    app_name VARCHAR(255),
    app_version VARCHAR(255),
    responsible_name VARCHAR(255),
    responsible_number VARCHAR(255),
    logo VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now()
);



CREATE TABLE public.organization_unit_type (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    position integer DEFAULT 0,
    created timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE public.organization_unit (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    name VARCHAR(255),
    code VARCHAR(255),
    parent VARCHAR(255),
    type VARCHAR(50),
    level VARCHAR(50),
    org_unit_type_id VARCHAR(255),
    facility_type VARCHAR(50),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    created_by VARCHAR(255),
    last_modified_by VARCHAR(255),
    i2ce_hidden integer,
    FOREIGN KEY (parent) REFERENCES public.organization_unit (id) ON UPDATE CASCADE
);

ALTER TABLE public.organization_unit
ADD CONSTRAINT org_unit_uniq UNIQUE (name, parent);

CREATE TABLE public.organization_unit_standards (
    uuid uuid NOT NULL PRIMARY KEY,
    classification_id VARCHAR(255),
    org_unit_type_id VARCHAR(255),
    number_of_positions integer,
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    created_by VARCHAR(255),
    last_modified_by VARCHAR(255),
    i2ce_hidden integer DEFAULT 0
);

ALTER TABLE public.organization_unit_standards
ADD CONSTRAINT org_unit_standard_uniq UNIQUE (classification_id, org_unit_type_id);

CREATE TABLE public.organization_level (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    name VARCHAR(255) UNIQUE,
    level integer,
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    created_by VARCHAR(255),
    last_modified_by VARCHAR(255)
);

CREATE TABLE public.audit_log (
    id uuid NOT NULL PRIMARY KEY,
    created timestamptz NOT NULL DEFAULT now(),
    user_id VARCHAR(255) NOT NULL,
    operation text
);


CREATE TABLE public.hippo_access_facility (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    location VARCHAR(255)
);



CREATE TABLE public.hippo_application (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    desired_wage VARCHAR(255),
    felony integer,
    felony_circumstance VARCHAR(255),
    full_time integer,
    hear VARCHAR(255),
    hours VARCHAR(255),
    other_info VARCHAR(255),
    "position" VARCHAR(255),
    start_date timestamptz NOT NULL DEFAULT now()
);


CREATE TABLE public.hippo_cadre (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255),
    translate_key VARCHAR(255),
    code VARCHAR(50),
    description VARCHAR(255)
);



CREATE TABLE public.hippo_classification (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    code VARCHAR(255),
    description VARCHAR(255),
    name VARCHAR(255) UNIQUE
);


CREATE TABLE public.hippo_contact (
    id uuid NOT NULL PRIMARY KEY,
    person_id VARCHAR(255),
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    created_by VARCHAR(255),
    last_modified_by VARCHAR(255),
    i2ce_hidden integer,
    address VARCHAR(255),
    alt_telephone VARCHAR(255),
    contact_group VARCHAR(255),
    contact_type VARCHAR(255),
    email VARCHAR(255),
    fax VARCHAR(255),
    mobile_phone VARCHAR(255),
    notes VARCHAR(255),
    telephone VARCHAR(255)
);

 
CREATE TABLE public.hippo_contact_group (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);



CREATE TABLE public.hippo_contact_type (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    i2ce_hidden integer,
    name VARCHAR(255),
    code VARCHAR(255)
);



CREATE TABLE public.hippo_country (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    alpha_two VARCHAR(255),
    code integer,
    csd_uuid VARCHAR(255),
    location integer,
    name VARCHAR(255),
    "primary" integer
);




CREATE TABLE public.hippo_currency (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    code VARCHAR(255),
    country VARCHAR(255),
    name VARCHAR(255),
    symbol VARCHAR(255)
);

CREATE TABLE public.hippo_degree (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255),
    code VARCHAR(255)
);


CREATE TABLE public.hippo_department (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);


CREATE TABLE public.hippo_district (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    code VARCHAR(255),
    csd_uuid VARCHAR(255),
    name VARCHAR(255),
    region VARCHAR(255)
);


CREATE TABLE public.hippo_education (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    description VARCHAR(255),
    level VARCHAR(255)
);


CREATE TABLE public.hippo_educational_level (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(255)
);


CREATE TABLE public.hippo_educational_major (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255) UNIQUE,
    code VARCHAR(255)
);


CREATE TABLE public.hippo_employee_status (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255),
    translate_key VARCHAR(255)
);


CREATE TABLE public.hippo_employment_status_info (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    person_id VARCHAR(255) NOT NULL,
    grade VARCHAR(255),
    cadre VARCHAR(255),
    classification VARCHAR(255),
    employment_date timestamptz NULL,
    start_service_date date,
    facility_id VARCHAR(255),
    ref_engagement text,
    salary integer,
    allowance integer,
    created_by VARCHAR(255),
    last_modified_by VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    i2ce_hidden integer,
    created timestamptz NOT NULL DEFAULT now(),
    position_decision_ref text,
    employee_status VARCHAR(255),
    job_type VARCHAR(255),
    salary_source VARCHAR(255),
    seniority integer,
    job VARCHAR(255),
    identified integer DEFAULT 0
);

CREATE INDEX ix_employement_status_info_jobtype ON public.hippo_employment_status_info USING btree (job_type);

CREATE TABLE public.hippo_employer (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);

CREATE TABLE public.hippo_employment_status (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255) UNIQUE,
    code VARCHAR(255)
);

CREATE TABLE public.hippo_entity_map (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    max_number integer NOT NULL
);



CREATE TABLE public.hippo_facility (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    location VARCHAR(255),
    name VARCHAR(255),
    code VARCHAR(255),
    csd_uuid VARCHAR(255),
    facility_type VARCHAR(255),
    latitude VARCHAR(255),
    longitude VARCHAR(255)
);



CREATE TABLE public.hippo_facility_type (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    code VARCHAR(255),
    name VARCHAR(255)  UNIQUE
);


CREATE TABLE public.hippo_gender (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)  UNIQUE
);


CREATE TABLE public.hippo_grade (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    code VARCHAR(255),
    description VARCHAR(255),
    name VARCHAR(255)  UNIQUE,
    rank integer
);




CREATE TABLE public.hippo_holiday (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    description VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255),
    type VARCHAR(255)
);



CREATE TABLE public.hippo_hours_of_work (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    code VARCHAR(255),
    description VARCHAR(255),
    name VARCHAR(255)
);



CREATE TABLE public.hippo_identification_type (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(255)
);

CREATE TABLE public.hippo_institution_type (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255),
    code VARCHAR(255)
);


CREATE TABLE public.hippo_job (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    cadre VARCHAR(255),
    classification VARCHAR(255),
    code VARCHAR(255),
    description VARCHAR(255),
    title VARCHAR(255),
    salary_grade VARCHAR(255)
);



CREATE TABLE public.hippo_job_description (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    i2ce_hidden integer,
    job_description VARCHAR(255),
    name VARCHAR(255),
    "position" VARCHAR(255)
);



CREATE TABLE public.hippo_job_history (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    end_date timestamptz NOT NULL DEFAULT now(),
    facility_id VARCHAR(255),
    job_title VARCHAR(255),
    start_date timestamptz NOT NULL DEFAULT now()
);



CREATE TABLE public.hippo_job_title (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255),
    cadre VARCHAR(255),
    classification VARCHAR(255),
    description VARCHAR(255)
);



CREATE TABLE public.hippo_job_type (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255),
    code VARCHAR(255),
    description VARCHAR(255)
);


CREATE TABLE public.hippo_level (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    description VARCHAR(255)
);



CREATE TABLE public.hippo_level_title (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255),
    rank integer
);


CREATE TABLE public.hippo_location (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    location VARCHAR(255),
    district_id VARCHAR(255)
);



CREATE TABLE public.hippo_marital_status (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);

CREATE TABLE public.hippo_medical_leave (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    end_date timestamptz NOT NULL DEFAULT now(),
    medical_leave_reason VARCHAR(255),
    medical_leave_type VARCHAR(255),
    notes VARCHAR(255),
    start_date timestamptz NOT NULL DEFAULT now()
);


CREATE TABLE public.hippo_medical_leave_reason (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);


CREATE TABLE public.hippo_medical_leave_type (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);


CREATE TABLE public.hippo_membership (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    end_date timestamptz NOT NULL DEFAULT now(),
    name VARCHAR(255),
    notes VARCHAR(255),
    start_date timestamptz NOT NULL DEFAULT now(),
    type VARCHAR(255)
);



CREATE TABLE public.hippo_membership_type (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);


CREATE TABLE public.hippo_module (
    id integer NOT NULL PRIMARY KEY,
    label VARCHAR(255),
    description VARCHAR(255),
    icon VARCHAR(50),
    parent integer
);


CREATE SEQUENCE public.hippo_module_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.hippo_module_id_seq OWNED BY public.hippo_module.id;


--
-- Name: hippo_module_page; Type: TABLE; Schema: public; Owner: ima2
--

CREATE TABLE public.hippo_module_page (
    code VARCHAR(255) NOT NULL PRIMARY KEY,
    label VARCHAR(255),
    url VARCHAR(255),
    is_tree_item integer,
    module_id integer NOT NULL,
    application_id VARCHAR(255)
);



CREATE TABLE public.hippo_nationality (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);



CREATE TABLE public.hippo_note (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    note VARCHAR(255),
    note_type VARCHAR(255),
    notes VARCHAR(255),
    "timestamp" timestamptz NOT NULL DEFAULT now()
);



CREATE TABLE public.hippo_note_type (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);


CREATE TABLE public.hippo_object_type (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);


CREATE TABLE public.hippo_organisation (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);




CREATE TABLE public.hippo_organisation_level (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);


CREATE TABLE public.hippo_organisation_type (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);



CREATE TABLE public.hippo_overtime_rule (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    description VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);




CREATE TABLE public.hippo_payment_frequency (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(255)
);


CREATE TABLE public.hippo_payroll_period (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    end_date timestamptz NOT NULL DEFAULT now(),
    name VARCHAR(255),
    start_date timestamptz NOT NULL DEFAULT now()
);



CREATE TABLE public.hippo_permission (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    name VARCHAR(255)
);


-- Table: public.document_type

-- DROP TABLE IF EXISTS public.document_type;

CREATE TABLE IF NOT EXISTS public.document_type
(
    id VARCHAR(255)  NOT NULL PRIMARY KEY,
    name VARCHAR(255)  NOT NULL,
    i2ce_hidden integer,
    created timestamptz NOT NULL DEFAULT now(),
    created_by VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    last_modified_by VARCHAR(255)
);

CREATE TABLE public.hippo_person (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    firstname VARCHAR(255),
    middlename VARCHAR(255),
    lastname VARCHAR(255),
    gender VARCHAR(255),
    address VARCHAR(255),
    birthplace text,
    birthdate date,
    recruitment_date date,
    email VARCHAR(255),
    marital_status VARCHAR(255),
    nationality VARCHAR(255),
    residence VARCHAR(255),
    telephone VARCHAR(255),
    title VARCHAR(255),
    user_id VARCHAR(255),
    degree VARCHAR(255),
    created_by VARCHAR(255),
    last_modified_by VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    i2ce_hidden integer,
    created timestamptz NOT NULL DEFAULT now(),
    csd_uuid uuid,
    dependents integer
);


CREATE TABLE IF NOT EXISTS public.hippo_person_document
(
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    path VARCHAR(255) NOT NULL,
    type_id VARCHAR(255),
    description VARCHAR(255),
    person_id VARCHAR(255),
    i2ce_hidden integer,
    created timestamptz,
    created_by VARCHAR(255),
    last_modified timestamptz,
    last_modified_by VARCHAR(255)
);

CREATE TABLE public.hippo_person_identification (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    created_by VARCHAR(255),
    last_modified_by VARCHAR(255),
    remap VARCHAR(255),
    i2ce_hidden integer,
    number VARCHAR(255) NOT NULL,
    expiration_date date,
    acquisition_date date,
    type_id VARCHAR(255),
    person_id VARCHAR(255),
    country VARCHAR(255)
);



CREATE TABLE public.hippo_person_photo_passport (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    path VARCHAR(255) NOT NULL,
    person_id VARCHAR(255),
    created_by VARCHAR(255),
    i2ce_hidden integer,
    created timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE public.hippo_person_timesheet (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    person_id VARCHAR(255) NOT NULL,
    created timestamptz NOT NULL DEFAULT now(),
    created_by VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    last_modified_by VARCHAR(255),
    i2ce_hidden integer,
    days_absence_justified integer,
    days_absence_unjustified integer,
    days_leave integer,
    days_holiday integer,
    days_sick integer,
    days_mission integer,
    days_worked integer,
    days_planned integer,
    month_year date,
    bonus_local numeric(12,2),
    bonus_pepfar numeric(12,2),
    bonus_partner numeric(12,2),
    bonus_risk numeric(12,2),
    project VARCHAR(255),
    salary_received numeric(12,2)
);



CREATE TABLE public.hippo_personnel_position (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    "position" VARCHAR(255),
    personnel VARCHAR(255)
);


CREATE TABLE public.hippo_personnel_position_type (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);



CREATE TABLE public.hippo_personnel_status (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);


CREATE TABLE public.hippo_personnel_type (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);



CREATE TABLE public.hippo_personnel_type_type (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);


CREATE TABLE public.hippo_phone (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    number VARCHAR(255),
    type VARCHAR(255)
);


CREATE TABLE public.hippo_position (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    name VARCHAR(255),
    position_type VARCHAR(255)
);


CREATE TABLE public.hippo_position_type (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    name VARCHAR(255)
);


CREATE TABLE public.hippo_province (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    name VARCHAR(255) UNIQUE,
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE public.hippo_qualification (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);



CREATE TABLE public.hippo_qualification_level (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);


CREATE TABLE public.hippo_race (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);



CREATE TABLE public.hippo_reason_departure (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(255)
);



CREATE TABLE public.hippo_religion (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);


CREATE TABLE public.hippo_role (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    assignable integer,
    is_default integer,
    homepage VARCHAR(255),
    name VARCHAR(255),
    created_by VARCHAR(255),
    trickle_up VARCHAR(255)
);


CREATE TABLE public.hippo_role_page (
    uuid uuid NOT NULL PRIMARY KEY,
    role_id VARCHAR(255) NOT NULL,
    page_code VARCHAR(255) NOT NULL
);

CREATE TABLE public.hippo_dashboard (
    uuid uuid NOT NULL PRIMARY KEY,
    mb_dashboard_id INTEGER NOT NULL,
    label VARCHAR(255) NOT NULL UNIQUE,
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    created_by VARCHAR(255),
    last_modified_by VARCHAR(255)
);

CREATE TABLE public.hippo_role_dashboard (
    uuid uuid NOT NULL PRIMARY KEY,
    role_id VARCHAR(255) NOT NULL,
    dashboard_uuid uuid NOT NULL,
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    created_by VARCHAR(255),
    last_modified_by VARCHAR(255)
);


CREATE TABLE public.hippo_actions (
  id INT NOT NULL PRIMARY KEY,
  description VARCHAR(100) NOT NULL
);

CREATE TABLE public.hippo_role_actions (
  uuid uuid NOT NULL PRIMARY KEY,
  role_id VARCHAR(255) NOT NULL,
  actions_id INT NOT NULL
);


CREATE TABLE public.hippo_salary_grade (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    notes VARCHAR(255),
    midpoint VARCHAR(255),
    start VARCHAR(255),
    "end" VARCHAR(255),
    description VARCHAR(255),
    name VARCHAR(255)
);


CREATE TABLE public.hippo_salary_scale (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    code VARCHAR(255),
    description VARCHAR(255),
    name VARCHAR(255),
    rank integer
);


CREATE TABLE public.hippo_salary_source (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    code VARCHAR(255),
    description VARCHAR(255),
    name VARCHAR(255)
);



CREATE TABLE public.hippo_sector (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);


CREATE TABLE public.hippo_sector_type (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);



CREATE TABLE public.hippo_sex (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    description VARCHAR(255)
);


CREATE TABLE public.hippo_speciality (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    description VARCHAR(255)
);


CREATE TABLE public.hippo_speciality_person (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    speciality_id VARCHAR(255),
    person_id VARCHAR(255)
);


CREATE TABLE public.hippo_speciality_type (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);



CREATE TABLE public.hippo_status (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);



CREATE TABLE public.hippo_strike_type (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);


CREATE TABLE public.hippo_training (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    course VARCHAR(255),
    end_date timestamptz NOT NULL DEFAULT now(),
    name VARCHAR(255),
    notes VARCHAR(255),
    start_date timestamptz NOT NULL DEFAULT now(),
    training_type VARCHAR(255)
);



CREATE TABLE public.hippo_training_type (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    name VARCHAR(255)
);



CREATE TABLE public.hippo_union (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    name VARCHAR(255)
);



CREATE TABLE public.hippo_user (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap VARCHAR(255),
    i2ce_hidden integer,
    password VARCHAR(255),
    role VARCHAR(255),
    username VARCHAR(255),
    firstname VARCHAR(255),
    lastname VARCHAR(255),
    email VARCHAR(255),
    creator VARCHAR(255)
);



CREATE TABLE public.hippo_user_role (
    uuid uuid NOT NULL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    role_id VARCHAR(255) NOT NULL
);


CREATE TABLE public.users (
    id integer NOT NULL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(120) NOT NULL
);


CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;

ALTER TABLE ONLY public.hippo_module ALTER COLUMN id SET DEFAULT nextval('public.hippo_module_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);

--
-- Indexes
--

CREATE INDEX hippo_esi_facility_idx ON public.hippo_employment_status_info USING btree (facility_id);


--
-- Name: hippo_esi_person_employment_date_idx; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX hippo_esi_person_employment_date_idx ON public.hippo_employment_status_info USING btree (person_id, employment_date DESC);


--
-- Name: hippo_person_identification_person_idx; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX hippo_person_identification_person_idx ON public.hippo_person_identification USING btree (person_id);


--
-- Name: ix_district__region; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_district__region ON public.hippo_district USING btree (region);


--
-- Name: ix_hippo_contact_contact_type; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_contact_contact_type ON public.hippo_contact USING btree (contact_type);


--
-- Name: ix_hippo_contact_created_by; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_contact_created_by ON public.hippo_contact USING btree (created_by);


--
-- Name: ix_hippo_contact_last_modified_by; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_contact_last_modified_by ON public.hippo_contact USING btree (last_modified_by);


--
-- Name: ix_hippo_contact_person_id; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_contact_person_id ON public.hippo_contact USING btree (person_id);


--
-- Name: ix_hippo_employment_status_info_cadre; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_employment_status_info_cadre ON public.hippo_employment_status_info USING btree (cadre);


--
-- Name: ix_hippo_employment_status_info_classification; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_employment_status_info_classification ON public.hippo_employment_status_info USING btree (classification);


--
-- Name: ix_hippo_employment_status_info_created_by; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_employment_status_info_created_by ON public.hippo_employment_status_info USING btree (created_by);


--
-- Name: ix_hippo_employment_status_info_facility_id; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_employment_status_info_facility_id ON public.hippo_employment_status_info USING btree (facility_id);


--
-- Name: ix_hippo_employment_status_info_grade; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_employment_status_info_grade ON public.hippo_employment_status_info USING btree (grade);


--
-- Name: ix_hippo_employment_status_info_i2ce_hidden; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_employment_status_info_i2ce_hidden ON public.hippo_employment_status_info USING btree (i2ce_hidden);


--
-- Name: ix_hippo_employment_status_info_last_modified_by; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_employment_status_info_last_modified_by ON public.hippo_employment_status_info USING btree (last_modified_by);


--
-- Name: ix_hippo_employment_status_info_person_id; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_employment_status_info_person_id ON public.hippo_employment_status_info USING btree (person_id);


--
-- Name: ix_hippo_entity_map_entity_type; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_entity_map_entity_type ON public.hippo_entity_map USING btree (entity_type);


--
-- Name: ix_hippo_job_title_cadre; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_job_title_cadre ON public.hippo_job_title USING btree (cadre);


--
-- Name: ix_hippo_job_title_classification; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_job_title_classification ON public.hippo_job_title USING btree (classification);


--
-- Name: ix_hippo_person_created_by; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_person_created_by ON public.hippo_person USING btree (created_by);


--
-- Name: ix_hippo_person_degree; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_person_degree ON public.hippo_person USING btree (degree);


--
-- Name: ix_hippo_person_gender; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_person_gender ON public.hippo_person USING btree (gender);


--
-- Name: ix_hippo_person_i2ce_hidden; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_person_i2ce_hidden ON public.hippo_person USING btree (i2ce_hidden);


--
-- Name: ix_hippo_person_identification_created_by; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_person_identification_created_by ON public.hippo_person_identification USING btree (created_by);


--
-- Name: ix_hippo_person_identification_last_modified_by; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_person_identification_last_modified_by ON public.hippo_person_identification USING btree (last_modified_by);


--
-- Name: ix_hippo_person_identification_person_id; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_person_identification_person_id ON public.hippo_person_identification USING btree (person_id);


--
-- Name: ix_hippo_person_identification_type_id; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_person_identification_type_id ON public.hippo_person_identification USING btree (type_id);


--
-- Name: ix_hippo_person_last_modified_by; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_person_last_modified_by ON public.hippo_person USING btree (last_modified_by);


--
-- Name: ix_hippo_person_nationality; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_person_nationality ON public.hippo_person USING btree (nationality);


--
-- Name: ix_hippo_person_photo_passport_created_by; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_person_photo_passport_created_by ON public.hippo_person_photo_passport USING btree (created_by);


--
-- Name: ix_hippo_person_photo_passport_i2ce_hidden; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_person_photo_passport_i2ce_hidden ON public.hippo_person_photo_passport USING btree (i2ce_hidden);


--
-- Name: ix_hippo_person_photo_passport_person_id; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_person_photo_passport_person_id ON public.hippo_person_photo_passport USING btree (person_id);


--
-- Name: ix_hippo_person_residence; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_person_residence ON public.hippo_person USING btree (residence);


--
-- Name: ix_hippo_person_timesheet_person_id; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_person_timesheet_person_id ON public.hippo_person_timesheet USING btree (person_id);


--
-- Name: ix_hippo_person_user_id; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_hippo_person_user_id ON public.hippo_person USING btree (user_id);


--
-- Name: ix_salary_source; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_salary_source ON public.hippo_employment_status_info USING btree (salary_source);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: ima2
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: ima2
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


-- Index: ix_document_type_created_by

CREATE INDEX IF NOT EXISTS ix_document_type_created_by
    ON public.document_type USING btree (created_by);

-- Index: ix_document_type_i2ce_hidden

CREATE INDEX IF NOT EXISTS ix_document_type_i2ce_hidden
    ON public.document_type USING btree (i2ce_hidden);

-- Index: ix_document_type_last_modified_by

CREATE INDEX IF NOT EXISTS ix_document_type_last_modified_by
    ON public.document_type USING btree (last_modified_by);
    


CREATE INDEX IF NOT EXISTS ix_hippo_person_document_created_by
    ON public.hippo_person_document USING btree (created_by);

-- Index: ix_hippo_person_document_description

CREATE INDEX IF NOT EXISTS ix_hippo_person_document_description
    ON public.hippo_person_document USING btree (description);

-- Index: ix_hippo_person_document_i2ce_hidden

CREATE INDEX IF NOT EXISTS ix_hippo_person_document_i2ce_hidden
    ON public.hippo_person_document USING btree (i2ce_hidden);

-- Index: ix_hippo_person_document_last_modified_by

CREATE INDEX IF NOT EXISTS ix_hippo_person_document_last_modified_by
    ON public.hippo_person_document USING btree (last_modified_by);

-- Index: ix_hippo_person_document_person_id

CREATE INDEX IF NOT EXISTS ix_hippo_person_document_person_id
    ON public.hippo_person_document USING btree (person_id);

-- Index: ix_hippo_person_document_type_id

CREATE INDEX IF NOT EXISTS ix_hippo_person_document_type_id
    ON public.hippo_person_document USING btree (type_id);