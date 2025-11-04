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
    app_name character varying(255),
    app_version character varying(255),
    responsible_name character varying(255),
    responsible_number character varying(255),
    logo character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now()
);



CREATE TABLE public.organization_unit_type (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    position integer default 0,
    created timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE public.organization_unit (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    name VARCHAR(255),
    code VARCHAR(255),
    parent VARCHAR(255),
    type character varying(50),
    level character varying(50),
    org_unit_type_id character varying(255),
    facility_type character varying(50),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    created_by character varying(255),
    last_modified_by character varying(255),
    i2ce_hidden integer,
    FOREIGN KEY (parent) REFERENCES public.organization_unit (id) ON UPDATE CASCADE
);

ALTER TABLE  public.organization_unit
ADD CONSTRAINT org_unit_uniq UNIQUE NULLS NOT DISTINCT (name, parent);

CREATE TABLE public.organization_unit_standards (
    uuid uuid NOT NULL PRIMARY KEY,
    classification_id VARCHAR(255),
    org_unit_type_id character varying(255),
    number_of_positions integer,
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    created_by character varying(255),
    last_modified_by character varying(255),
    i2ce_hidden integer DEFAULT 0
);

ALTER TABLE  public.organization_unit_standards
ADD CONSTRAINT org_unit_standard_uniq UNIQUE NULLS NOT DISTINCT (classification_id, org_unit_type_id);

CREATE TABLE public.organization_level (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    name VARCHAR(255) UNIQUE,
    level integer,
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    created_by character varying(255),
    last_modified_by character varying(255)
);

CREATE TABLE public.audit_log (
    id uuid NOT NULL PRIMARY KEY,
    created timestamptz NOT NULL DEFAULT now(),
    user_id varchar(255) NOT NULL,
    operation text
);


CREATE TABLE public.hippo_access_facility (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    location character varying(255)
);



CREATE TABLE public.hippo_application (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    desired_wage character varying(255),
    felony integer,
    felony_circumstance character varying(255),
    full_time integer,
    hear character varying(255),
    hours character varying(255),
    other_info character varying(255),
    "position" character varying(255),
    start_date timestamptz NOT NULL DEFAULT now()
);


CREATE TABLE public.hippo_cadre (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255),
    translate_key character varying(255),
    code character varying(50),
    description character varying(255)
);



CREATE TABLE public.hippo_classification (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    code character varying(255),
    description character varying(255),
    name character varying(255) UNIQUE
);


CREATE TABLE public.hippo_contact (
    id uuid NOT NULL,
    person_id character varying(255),
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    created_by character varying(255),
    last_modified_by character varying(255),
    i2ce_hidden integer,
    address character varying(255),
    alt_telephone character varying(255),
    contact_group character varying(255),
    contact_type character varying(255),
    email character varying(255),
    fax character varying(255),
    mobile_phone character varying(255),
    notes character varying(255),
    telephone character varying(255)
);

 
CREATE TABLE public.hippo_contact_group (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);



CREATE TABLE public.hippo_contact_type (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    i2ce_hidden integer,
    name character varying(255),
    code character varying(255)
);



CREATE TABLE public.hippo_country (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    alpha_two character varying(255),
    code integer,
    csd_uuid character varying(255),
    location integer,
    name character varying(255),
    "primary" integer
);




CREATE TABLE public.hippo_currency (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    code character varying(255),
    country character varying(255),
    name character varying(255),
    symbol character varying(255)
);

CREATE TABLE public.hippo_degree (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255),
    code character varying(255)
);


CREATE TABLE public.hippo_department (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);


CREATE TABLE public.hippo_district (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    code character varying(255),
    csd_uuid character varying(255),
    name character varying(255),
    region character varying(255)
);


CREATE TABLE public.hippo_education (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    description character varying(255),
    level character varying(255)
);


CREATE TABLE public.hippo_educational_level (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255) NOT NULL,
    code character varying(255)
);


CREATE TABLE public.hippo_educational_major (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255) UNIQUE,
    code character varying(255)
);


CREATE TABLE public.hippo_employee_status (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255),
    translate_key character varying(255)
);


CREATE TABLE public.hippo_employment_status_info (
    id character varying(255) NOT NULL,
    person_id character varying(255) NOT NULL,
    grade character varying(255),
    cadre character varying(255),
    classification character varying(255),
    employment_date timestamptz NULL,
    start_service_date date,
    facility_id character varying(255),
    ref_engagement text,
    salary integer,
    allowance integer,
    created_by character varying(255),
    last_modified_by character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    i2ce_hidden integer,
    created timestamptz NOT NULL DEFAULT now(),
    position_decision_ref text,
    employee_status character varying(255),
    job_type character varying(255),
    salary_source character varying(255),
    seniority integer,
    job character varying(255),
    identified integer DEFAULT 0
);

ALTER TABLE ONLY public.hippo_employment_status_info
    ADD CONSTRAINT hippo_employment_status_info_pkey PRIMARY KEY (id);

CREATE INDEX ix_employement_status_info_jobtype ON public.hippo_employment_status_info USING btree (job_type);

CREATE TABLE public.hippo_employer (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);

CREATE TABLE public.hippo_employment_status (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255) UNIQUE,
    code character varying(255)
);

ALTER TABLE ONLY public.hippo_employment_status
    ADD CONSTRAINT hippo_employment_status_pkey PRIMARY KEY (id);

CREATE TABLE public.hippo_entity_map (
    id character varying(255) NOT NULL,
    entity_type character varying(50) NOT NULL,
    max_number integer NOT NULL
);



CREATE TABLE public.hippo_facility (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    location character varying(255),
    name character varying(255),
    code character varying(255),
    csd_uuid character varying(255),
    facility_type character varying(255),
    latitude character varying(255),
    longitude character varying(255)
);



CREATE TABLE public.hippo_facility_type (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    code character varying(255),
    name character varying(255)  UNIQUE
);


CREATE TABLE public.hippo_gender (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)  UNIQUE
);


CREATE TABLE public.hippo_grade (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    code character varying(255),
    description character varying(255),
    name character varying(255)  UNIQUE,
    rank integer
);




CREATE TABLE public.hippo_holiday (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    description character varying(255),
    i2ce_hidden integer,
    name character varying(255),
    type character varying(255)
);



CREATE TABLE public.hippo_hours_of_work (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    code character varying(255),
    description character varying(255),
    name character varying(255)
);



CREATE TABLE public.hippo_identification_type (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255) NOT NULL,
    code character varying(255)
);

CREATE TABLE public.hippo_institution_type (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255),
    code character varying(255)
);


CREATE TABLE public.hippo_job (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    cadre character varying(255),
    classification character varying(255),
    code character varying(255),
    description character varying(255),
    title character varying(255),
    salary_grade character varying(255)
);



CREATE TABLE public.hippo_job_description (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    i2ce_hidden integer,
    job_description character varying(255),
    name character varying(255),
    "position" character varying(255)
);



CREATE TABLE public.hippo_job_history (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    end_date timestamptz NOT NULL DEFAULT now(),
    facility_id character varying(255),
    job_title character varying(255),
    start_date timestamptz NOT NULL DEFAULT now()
);



CREATE TABLE public.hippo_job_title (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255),
    cadre character varying(255),
    classification character varying(255),
    description character varying(255)
);



CREATE TABLE public.hippo_job_type (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255),
    code character varying(255),
    description character varying(255)
);


CREATE TABLE public.hippo_level (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    description character varying(255)
);



CREATE TABLE public.hippo_level_title (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255),
    rank integer
);


CREATE TABLE public.hippo_location (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    location character varying(255),
    district_id character varying(255)
);



CREATE TABLE public.hippo_marital_status (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);

CREATE TABLE public.hippo_medical_leave (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    end_date timestamptz NOT NULL DEFAULT now(),
    medical_leave_reason character varying(255),
    medical_leave_type character varying(255),
    notes character varying(255),
    start_date timestamptz NOT NULL DEFAULT now()
);


CREATE TABLE public.hippo_medical_leave_reason (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);


CREATE TABLE public.hippo_medical_leave_type (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);


CREATE TABLE public.hippo_membership (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    end_date timestamptz NOT NULL DEFAULT now(),
    name character varying(255),
    notes character varying(255),
    start_date timestamptz NOT NULL DEFAULT now(),
    type character varying(255)
);



CREATE TABLE public.hippo_membership_type (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);


CREATE TABLE public.hippo_module (
    id integer NOT NULL,
    label character varying(255),
    description character varying(255),
    icon character varying(50),
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
    code character varying(255) NOT NULL,
    label character varying(255),
    url character varying(255),
    is_tree_item integer,
    module_id integer NOT NULL,
    application_id character varying(255)
);



CREATE TABLE public.hippo_nationality (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);



CREATE TABLE public.hippo_note (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    note character varying(255),
    note_type character varying(255),
    notes character varying(255),
    "timestamp" timestamptz NOT NULL DEFAULT now()
);



CREATE TABLE public.hippo_note_type (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);


CREATE TABLE public.hippo_object_type (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);


CREATE TABLE public.hippo_organisation (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);




CREATE TABLE public.hippo_organisation_level (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);


CREATE TABLE public.hippo_organisation_type (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);



CREATE TABLE public.hippo_overtime_rule (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    description character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);




CREATE TABLE public.hippo_payment_frequency (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255) NOT NULL,
    code character varying(255)
);


CREATE TABLE public.hippo_payroll_period (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    end_date timestamptz NOT NULL DEFAULT now(),
    name character varying(255),
    start_date timestamptz NOT NULL DEFAULT now()
);



CREATE TABLE public.hippo_permission (
    id character varying(255) NOT NULL,
    name character varying(255)
);



CREATE TABLE public.hippo_person (
    id character varying(255) NOT NULL,
    firstname character varying(255),
    middlename character varying(255),
    lastname character varying(255),
    gender character varying(255),
    address character varying(255),
    birthplace character varying,
    birthdate date,
    recruitment_date date,
    email character varying(255),
    marital_status character varying(255),
    nationality character varying(255),
    residence character varying(255),
    telephone character varying(255),
    title character varying(255),
    user_id character varying(255),
    degree character varying(255),
    created_by character varying(255),
    last_modified_by character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    i2ce_hidden integer,
    created timestamptz NOT NULL DEFAULT now(),
    csd_uuid uuid,
    dependents integer
);


CREATE TABLE public.hippo_person_identification (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    created_by character varying(255),
    last_modified_by character varying(255),
    remap character varying(255),
    i2ce_hidden integer,
    number character varying(255) NOT NULL,
    expiration_date date,
    acquisition_date date,
    type_id character varying(255),
    person_id character varying(255),
    country character varying(255)
);



CREATE TABLE public.hippo_person_photo_passport (
    id character varying(255) NOT NULL,
    path character varying(255) NOT NULL,
    person_id character varying(255),
    created_by character varying(255),
    i2ce_hidden integer,
    created timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE public.hippo_person_timesheet (
    id character varying(255) NOT NULL,
    person_id character varying(255) NOT NULL,
    created timestamptz NOT NULL DEFAULT now(),
    created_by character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    last_modified_by character varying(255),
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
    project character varying(255),
    salary_received numeric(12,2)
);



CREATE TABLE public.hippo_personnel_position (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    "position" character varying(255),
    personnel character varying(255)
);


CREATE TABLE public.hippo_personnel_position_type (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);



CREATE TABLE public.hippo_personnel_status (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);


CREATE TABLE public.hippo_personnel_type (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);



CREATE TABLE public.hippo_personnel_type_type (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);


CREATE TABLE public.hippo_phone (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    number character varying(255),
    type character varying(255)
);


CREATE TABLE public.hippo_position (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    name character varying(255),
    position_type character varying(255)
);


CREATE TABLE public.hippo_position_type (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    name character varying(255)
);


CREATE TABLE public.hippo_province (
    id character varying(255) NOT NULL,
    parent character varying(255),
    name VARCHAR(255) UNIQUE,
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE public.hippo_qualification (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);



CREATE TABLE public.hippo_qualification_level (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);


CREATE TABLE public.hippo_race (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);



CREATE TABLE public.hippo_reason_departure (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255) NOT NULL,
    code character varying(255)
);



CREATE TABLE public.hippo_religion (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);


CREATE TABLE public.hippo_role (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    assignable integer,
    is_default integer,
    homepage character varying(255),
    name character varying(255),
    created_by character varying(255),
    trickle_up character varying(255)
);


CREATE TABLE public.hippo_role_page (
    uuid uuid NOT NULL,
    role_id character varying(255) NOT NULL,
    page_code character varying(255) NOT NULL
);

CREATE TABLE public.hippo_dashboard (
    uuid uuid NOT NULL PRIMARY KEY,
    mb_dashboard_id INTEGER NOT NULL,
    label character varying(255) NOT NULL UNIQUE,
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    created_by character varying(255),
    last_modified_by character varying(255)
);

CREATE TABLE public.hippo_role_dashboard (
    uuid uuid NOT NULL  PRIMARY KEY,
    role_id character varying(255) NOT NULL,
    dashboard_uuid uuid NOT NULL,
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    created_by character varying(255),
    last_modified_by character varying(255)
);


CREATE TABLE public.hippo_actions (
  id INT NOT NULL PRIMARY KEY,
  description VARCHAR(100) NOT NULL
);

CREATE TABLE public.hippo_role_actions (
  uuid uuid NOT NULL PRIMARY KEY,
  role_id character varying(255) NOT NULL,
  actions_id INT NOT NULL
);


CREATE TABLE public.hippo_salary_grade (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    notes character varying(255),
    midpoint character varying(255),
    start character varying(255),
    "end" character varying(255),
    description character varying(255),
    name character varying(255)
);


CREATE TABLE public.hippo_salary_scale (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    code character varying(255),
    description character varying(255),
    name character varying(255),
    rank integer
);


CREATE TABLE public.hippo_salary_source (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    code character varying(255),
    description character varying(255),
    name character varying(255)
);



CREATE TABLE public.hippo_sector (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);


CREATE TABLE public.hippo_sector_type (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);



CREATE TABLE public.hippo_sex (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    description character varying(255)
);


CREATE TABLE public.hippo_speciality (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    description character varying(255)
);


CREATE TABLE public.hippo_speciality_person (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    speciality_id character varying(255),
    person_id character varying(255)
);


CREATE TABLE public.hippo_speciality_type (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);



CREATE TABLE public.hippo_status (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);



CREATE TABLE public.hippo_strike_type (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);


CREATE TABLE public.hippo_training (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    course character varying(255),
    end_date timestamptz NOT NULL DEFAULT now(),
    name character varying(255),
    notes character varying(255),
    start_date timestamptz NOT NULL DEFAULT now(),
    training_type character varying(255)
);



CREATE TABLE public.hippo_training_type (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    name character varying(255)
);



CREATE TABLE public.hippo_union (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    name character varying(255)
);



CREATE TABLE public.hippo_user (
    id character varying(255) NOT NULL,
    parent character varying(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    remap character varying(255),
    i2ce_hidden integer,
    password character varying(255),
    role character varying(255),
    username character varying(255),
    firstname character varying(255),
    lastname character varying(255),
    email character varying(255),
    creator character varying(255)
);



CREATE TABLE public.hippo_user_role (
    uuid uuid NOT NULL,
    user_id character varying(255) NOT NULL,
    role_id character varying(255) NOT NULL
);


CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    email character varying(120) NOT NULL
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
-- Name: hippo_access_facility hippo_access_facility_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_access_facility
    ADD CONSTRAINT hippo_access_facility_pkey PRIMARY KEY (id);


--
-- Name: hippo_application hippo_application_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_application
    ADD CONSTRAINT hippo_application_pkey PRIMARY KEY (id);


--
-- Name: hippo_cadre hippo_cadre_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_cadre
    ADD CONSTRAINT hippo_cadre_pkey PRIMARY KEY (id);


--
-- Name: hippo_classification hippo_classification_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_classification
    ADD CONSTRAINT hippo_classification_pkey PRIMARY KEY (id);


--
-- Name: hippo_contact_group hippo_contact_group_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_contact_group
    ADD CONSTRAINT hippo_contact_group_pkey PRIMARY KEY (id);


--
-- Name: hippo_contact hippo_contact_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_contact
    ADD CONSTRAINT hippo_contact_pkey PRIMARY KEY (id);


--
-- Name: hippo_contact_type hippo_contact_type_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_contact_type
    ADD CONSTRAINT hippo_contact_type_pkey PRIMARY KEY (id);


--
-- Name: hippo_country hippo_country_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_country
    ADD CONSTRAINT hippo_country_pkey PRIMARY KEY (id);



--
-- Name: hippo_currency hippo_currency_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_currency
    ADD CONSTRAINT hippo_currency_pkey PRIMARY KEY (id);


--
-- Name: hippo_degree hippo_degree_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_degree
    ADD CONSTRAINT hippo_degree_pkey PRIMARY KEY (id);


--
-- Name: hippo_department hippo_department_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_department
    ADD CONSTRAINT hippo_department_pkey PRIMARY KEY (id);


--
-- Name: hippo_district hippo_district_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_district
    ADD CONSTRAINT hippo_district_pkey PRIMARY KEY (id);


--
-- Name: hippo_education hippo_education_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_education
    ADD CONSTRAINT hippo_education_pkey PRIMARY KEY (id);


--
-- Name: hippo_educational_level hippo_educational_level_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_educational_level
    ADD CONSTRAINT hippo_educational_level_pkey PRIMARY KEY (id);


--
-- Name: hippo_educational_major hippo_educational_major_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_educational_major
    ADD CONSTRAINT hippo_educational_major_pkey PRIMARY KEY (id);


--
-- Name: hippo_employee_status hippo_employee_status_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_employee_status
    ADD CONSTRAINT hippo_employee_status_pkey PRIMARY KEY (id);




--
-- Name: hippo_employer hippo_employer_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_employer
    ADD CONSTRAINT hippo_employer_pkey PRIMARY KEY (id);




--
-- Name: hippo_entity_map hippo_entity_map_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_entity_map
    ADD CONSTRAINT hippo_entity_map_pkey PRIMARY KEY (id);


--
-- Name: hippo_facility hippo_facility_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_facility
    ADD CONSTRAINT hippo_facility_pkey PRIMARY KEY (id);


--
-- Name: hippo_facility_type hippo_facility_type_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_facility_type
    ADD CONSTRAINT hippo_facility_type_pkey PRIMARY KEY (id);


--
-- Name: hippo_gender hippo_gender_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_gender
    ADD CONSTRAINT hippo_gender_pkey PRIMARY KEY (id);


--
-- Name: hippo_grade hippo_grade_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_grade
    ADD CONSTRAINT hippo_grade_pkey PRIMARY KEY (id);


--
-- Name: hippo_holiday hippo_holiday_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_holiday
    ADD CONSTRAINT hippo_holiday_pkey PRIMARY KEY (id);


--
-- Name: hippo_hours_of_work hippo_hours_of_work_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_hours_of_work
    ADD CONSTRAINT hippo_hours_of_work_pkey PRIMARY KEY (id);


--
-- Name: hippo_identification_type hippo_identification_type_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_identification_type
    ADD CONSTRAINT hippo_identification_type_pkey PRIMARY KEY (id);


--
-- Name: hippo_institution_type hippo_institution_type_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_institution_type
    ADD CONSTRAINT hippo_institution_type_pkey PRIMARY KEY (id);


--
-- Name: hippo_job_description hippo_job_description_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_job_description
    ADD CONSTRAINT hippo_job_description_pkey PRIMARY KEY (id);


--
-- Name: hippo_job_history hippo_job_history_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_job_history
    ADD CONSTRAINT hippo_job_history_pkey PRIMARY KEY (id);


--
-- Name: hippo_job hippo_job_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_job
    ADD CONSTRAINT hippo_job_pkey PRIMARY KEY (id);


--
-- Name: hippo_job_title hippo_job_title_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_job_title
    ADD CONSTRAINT hippo_job_title_pkey PRIMARY KEY (id);


--
-- Name: hippo_job_type hippo_job_type_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_job_type
    ADD CONSTRAINT hippo_job_type_pkey PRIMARY KEY (id);


--
-- Name: hippo_level hippo_level_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_level
    ADD CONSTRAINT hippo_level_pkey PRIMARY KEY (id);


--
-- Name: hippo_level_title hippo_level_title_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_level_title
    ADD CONSTRAINT hippo_level_title_pkey PRIMARY KEY (id);


--
-- Name: hippo_location hippo_location_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_location
    ADD CONSTRAINT hippo_location_pkey PRIMARY KEY (id);


--
-- Name: hippo_marital_status hippo_marital_status_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_marital_status
    ADD CONSTRAINT hippo_marital_status_pkey PRIMARY KEY (id);


--
-- Name: hippo_medical_leave hippo_medical_leave_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_medical_leave
    ADD CONSTRAINT hippo_medical_leave_pkey PRIMARY KEY (id);


--
-- Name: hippo_medical_leave_reason hippo_medical_leave_reason_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_medical_leave_reason
    ADD CONSTRAINT hippo_medical_leave_reason_pkey PRIMARY KEY (id);


--
-- Name: hippo_medical_leave_type hippo_medical_leave_type_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_medical_leave_type
    ADD CONSTRAINT hippo_medical_leave_type_pkey PRIMARY KEY (id);


--
-- Name: hippo_membership hippo_membership_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_membership
    ADD CONSTRAINT hippo_membership_pkey PRIMARY KEY (id);


--
-- Name: hippo_membership_type hippo_membership_type_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_membership_type
    ADD CONSTRAINT hippo_membership_type_pkey PRIMARY KEY (id);


--
-- Name: hippo_module_page hippo_module_page_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_module_page
    ADD CONSTRAINT hippo_module_page_pkey PRIMARY KEY (code);


--
-- Name: hippo_module hippo_module_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_module
    ADD CONSTRAINT hippo_module_pkey PRIMARY KEY (id);


--
-- Name: hippo_nationality hippo_nationality_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_nationality
    ADD CONSTRAINT hippo_nationality_pkey PRIMARY KEY (id);


--
-- Name: hippo_note hippo_note_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_note
    ADD CONSTRAINT hippo_note_pkey PRIMARY KEY (id);


--
-- Name: hippo_note_type hippo_note_type_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_note_type
    ADD CONSTRAINT hippo_note_type_pkey PRIMARY KEY (id);


--
-- Name: hippo_object_type hippo_object_type_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_object_type
    ADD CONSTRAINT hippo_object_type_pkey PRIMARY KEY (id);


--
-- Name: hippo_organisation_level hippo_organisation_level_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_organisation_level
    ADD CONSTRAINT hippo_organisation_level_pkey PRIMARY KEY (id);


--
-- Name: hippo_organisation hippo_organisation_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_organisation
    ADD CONSTRAINT hippo_organisation_pkey PRIMARY KEY (id);


--
-- Name: hippo_organisation_type hippo_organisation_type_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_organisation_type
    ADD CONSTRAINT hippo_organisation_type_pkey PRIMARY KEY (id);


--
-- Name: hippo_overtime_rule hippo_overtime_rule_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_overtime_rule
    ADD CONSTRAINT hippo_overtime_rule_pkey PRIMARY KEY (id);


--
-- Name: hippo_payment_frequency hippo_payment_frequency_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_payment_frequency
    ADD CONSTRAINT hippo_payment_frequency_pkey PRIMARY KEY (id);


--
-- Name: hippo_payroll_period hippo_payroll_period_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_payroll_period
    ADD CONSTRAINT hippo_payroll_period_pkey PRIMARY KEY (id);


--
-- Name: hippo_permission hippo_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_permission
    ADD CONSTRAINT hippo_permission_pkey PRIMARY KEY (id);


--
-- Name: hippo_person_identification hippo_person_identification_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_person_identification
    ADD CONSTRAINT hippo_person_identification_pkey PRIMARY KEY (id);


--
-- Name: hippo_person_photo_passport hippo_person_photo_passport_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_person_photo_passport
    ADD CONSTRAINT hippo_person_photo_passport_pkey PRIMARY KEY (id);


--
-- Name: hippo_person hippo_person_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_person
    ADD CONSTRAINT hippo_person_pkey PRIMARY KEY (id);


--
-- Name: hippo_person_timesheet hippo_person_timesheet_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_person_timesheet
    ADD CONSTRAINT hippo_person_timesheet_pkey PRIMARY KEY (id);


--
-- Name: hippo_personnel_position hippo_personnel_position_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_personnel_position
    ADD CONSTRAINT hippo_personnel_position_pkey PRIMARY KEY (id);


--
-- Name: hippo_personnel_position_type hippo_personnel_position_type_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_personnel_position_type
    ADD CONSTRAINT hippo_personnel_position_type_pkey PRIMARY KEY (id);


--
-- Name: hippo_personnel_status hippo_personnel_status_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_personnel_status
    ADD CONSTRAINT hippo_personnel_status_pkey PRIMARY KEY (id);


--
-- Name: hippo_personnel_type hippo_personnel_type_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_personnel_type
    ADD CONSTRAINT hippo_personnel_type_pkey PRIMARY KEY (id);


--
-- Name: hippo_personnel_type_type hippo_personnel_type_type_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_personnel_type_type
    ADD CONSTRAINT hippo_personnel_type_type_pkey PRIMARY KEY (id);


--
-- Name: hippo_phone hippo_phone_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_phone
    ADD CONSTRAINT hippo_phone_pkey PRIMARY KEY (id);


--
-- Name: hippo_position hippo_position_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_position
    ADD CONSTRAINT hippo_position_pkey PRIMARY KEY (id);


--
-- Name: hippo_position_type hippo_position_type_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_position_type
    ADD CONSTRAINT hippo_position_type_pkey PRIMARY KEY (id);


--
-- Name: hippo_province hippo_province_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_province
    ADD CONSTRAINT hippo_province_pkey PRIMARY KEY (id);


--
-- Name: hippo_qualification_level hippo_qualification_level_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_qualification_level
    ADD CONSTRAINT hippo_qualification_level_pkey PRIMARY KEY (id);


--
-- Name: hippo_qualification hippo_qualification_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_qualification
    ADD CONSTRAINT hippo_qualification_pkey PRIMARY KEY (id);


--
-- Name: hippo_race hippo_race_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_race
    ADD CONSTRAINT hippo_race_pkey PRIMARY KEY (id);


--
-- Name: hippo_reason_departure hippo_reason_departure_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_reason_departure
    ADD CONSTRAINT hippo_reason_departure_pkey PRIMARY KEY (id);



--
-- Name: hippo_religion hippo_religion_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_religion
    ADD CONSTRAINT hippo_religion_pkey PRIMARY KEY (id);


--
-- Name: hippo_role hippo_role_name_key; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_role
    ADD CONSTRAINT hippo_role_name_key UNIQUE (name);


--
-- Name: hippo_role_page hippo_role_page_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_role_page
    ADD CONSTRAINT hippo_role_page_pkey PRIMARY KEY (uuid);


--
-- Name: hippo_role hippo_role_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_role
    ADD CONSTRAINT hippo_role_pkey PRIMARY KEY (id);


--
-- Name: hippo_salary_grade hippo_salary_grade_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_salary_grade
    ADD CONSTRAINT hippo_salary_grade_pkey PRIMARY KEY (id);


--
-- Name: hippo_salary_scale hippo_salary_scale_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_salary_scale
    ADD CONSTRAINT hippo_salary_scale_pkey PRIMARY KEY (id);


--
-- Name: hippo_salary_source hippo_salary_source_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_salary_source
    ADD CONSTRAINT hippo_salary_source_pkey PRIMARY KEY (id);


--
-- Name: hippo_sector hippo_sector_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_sector
    ADD CONSTRAINT hippo_sector_pkey PRIMARY KEY (id);


--
-- Name: hippo_sector_type hippo_sector_type_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_sector_type
    ADD CONSTRAINT hippo_sector_type_pkey PRIMARY KEY (id);


--
-- Name: hippo_sex hippo_sex_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_sex
    ADD CONSTRAINT hippo_sex_pkey PRIMARY KEY (id);


--
-- Name: hippo_speciality_person hippo_speciality_person_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_speciality_person
    ADD CONSTRAINT hippo_speciality_person_pkey PRIMARY KEY (id);


--
-- Name: hippo_speciality hippo_speciality_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_speciality
    ADD CONSTRAINT hippo_speciality_pkey PRIMARY KEY (id);


--
-- Name: hippo_speciality_type hippo_speciality_type_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_speciality_type
    ADD CONSTRAINT hippo_speciality_type_pkey PRIMARY KEY (id);


--
-- Name: hippo_status hippo_status_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_status
    ADD CONSTRAINT hippo_status_pkey PRIMARY KEY (id);


--
-- Name: hippo_strike_type hippo_strike_type_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_strike_type
    ADD CONSTRAINT hippo_strike_type_pkey PRIMARY KEY (id);


--
-- Name: hippo_training hippo_training_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_training
    ADD CONSTRAINT hippo_training_pkey PRIMARY KEY (id);


--
-- Name: hippo_training_type hippo_training_type_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_training_type
    ADD CONSTRAINT hippo_training_type_pkey PRIMARY KEY (id);


--
-- Name: hippo_union hippo_union_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_union
    ADD CONSTRAINT hippo_union_pkey PRIMARY KEY (id);


--
-- Name: hippo_user hippo_user_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_user
    ADD CONSTRAINT hippo_user_pkey PRIMARY KEY (id);


--
-- Name: hippo_user_role hippo_user_role_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.hippo_user_role
    ADD CONSTRAINT hippo_user_role_pkey PRIMARY KEY (uuid);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: ima2
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


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
-- Name: ix_health_are__county; Type: INDEX; Schema: public; Owner: ima2
--



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


