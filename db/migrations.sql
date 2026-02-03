alter table public.hippo_employment_status_info ADD job_type character varying(255);

CREATE INDEX ix_employement_status_info_jobtype ON public.hippo_employment_status_info USING btree (job_type);

ALTER TABLE  public.hippo_employment_status_info ADD seniority integer

alter table public.hippo_degree add code varchar(255);

alter table hippo_province add name VARCHAR(255);

ALTER TABLE hippo_employement_status_info RENAME TO hippo_employment_status_info;

ALTER TABLE public.hippo_person ADD recruitment_date date;
ALTER TABLE public.hippo_employment_status_info ADD start_service_date date;

-- le 4 octobre 2025
INSERT INTO public.hippo_module_page (code, label, url, is_tree_item, module_id)  VALUES
('dashboard_registry', 'TREE.METABASE_DASHBOARD', '/manage/dashboard_registry', 1, 4),
('dashboard_create', 'TREE.METABASE_DASHBOARD_NEW', '/manage/dashboard_create', 0, 4);

-- le 
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE norm_requirement (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  organization_unit_type_id VARCHAR(255) NOT NULL,  -- 'HD', 'CS_URBAN', 'CS_RURAL'
  classification_id VARCHAR(255) NOT NULL,          -- ex: 'classification|4'
  required INTEGER NOT NULL,

  CONSTRAINT uq_norm_requirement_type_class
    UNIQUE (organization_unit_type_id, classification_id)
);

