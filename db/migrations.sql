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


--- le jeudi 5/01/2026
INSERT INTO public.hippo_module_page (code, label, url, is_tree_item, module_id)  VALUES
('document_type_registry', 'TREE.DOCUMENT_TYPE', '/manage/document_type_registry', 1, 5),
('document_type_create', 'TREE.DOCUMENT_TYPE_NEW', '/manage/document_type_create', 0, 5);


--- vendredi 6/02/2026
INSERT INTO public.hippo_module_page (code, label, url, is_tree_item, module_id)  VALUES
('identification_type_registry', 'TREE.IDENTIFICATION_TYPE', '/manage/identification_type_registry', 1, 5),
('identification_type_create', 'TREE.IDENTIFICATION_TYPE_NEW', '/manage/identification_type_create', 0, 5);
