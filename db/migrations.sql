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




INSERT INTO public.hippo_module_page (code, label, url, is_tree_item, module_id)  VALUES

('employee_status_registry', 'TREE.EMPLOYEE_STATUS', '/manage/employee_status_registry', 1, 5),
('employee_status_create', 'TREE.EMPLOYEE_STATUS_NEW', '/manage/employee_status_create', 0, 5);

ALTER TABLE public.hippo_person ADD recruitment_doc_ref VARCHAR(255);


-- speciality

DROP TABLE IF EXISTS public.hippo_speciality;
CREATE TABLE public.hippo_speciality (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    parent VARCHAR(255),
    last_modified timestamptz NOT NULL DEFAULT now(),
    created timestamptz NOT NULL DEFAULT now(),
    name VARCHAR(255),
    code VARCHAR(255)
);


-- Insérer les spécialités avec l'ID au format speciality|code
INSERT INTO public.hippo_speciality (id, name, code, parent, created, last_modified) 
VALUES 
('speciality|ANEST', 'Anesthésiologie', 'ANEST', '|', NOW(), NOW()),
('speciality|CARDI', 'Cardiologie', 'CARDI', '|', NOW(), NOW()),
('speciality|CHIRG', 'Chirurgie générale', 'CHIRG', '|', NOW(), NOW()),
('speciality|CHIRP', 'Chirurgie plastique', 'CHIRP', '|', NOW(), NOW()),
('speciality|CHIRV', 'Chirurgie vasculaire', 'CHIRV', '|', NOW(), NOW()),
('speciality|DERMA', 'Dermatologie', 'DERMA', '|', NOW(), NOW()),
('speciality|ENDOC', 'Endocrinologie', 'ENDOC', '|', NOW(), NOW()),
('speciality|GASTRO', 'Gastro-entérologie', 'GASTRO', '|', NOW(), NOW()),
('speciality|GERIA', 'Gériatrie', 'GERIA', '|', NOW(), NOW()),
('speciality|GYNEC', 'Gynécologie-obstétrique', 'GYNEC', '|', NOW(), NOW()),
('speciality|HEMTO', 'Hématologie', 'HEMTO', '|', NOW(), NOW()),
('speciality|HEPGA', 'Hépato-gastro-entérologie', 'HEPGA', '|', NOW(), NOW()),
('speciality|INFEC', 'Infectiologie', 'INFEC', '|', NOW(), NOW()),
('speciality|MEDIN', 'Médecine interne', 'MEDIN', '|', NOW(), NOW()),
('speciality|NEPHR', 'Néphrologie', 'NEPHR', '|', NOW(), NOW()),
('speciality|NEURO', 'Neurologie', 'NEURO', '|', NOW(), NOW()),
('speciality|NEUCH', 'Neurochirurgie', 'NEUCH', '|', NOW(), NOW()),
('speciality|ONCOL', 'Oncologie', 'ONCOL', '|', NOW(), NOW()),
('speciality|OPHTA', 'Ophtalmologie', 'OPHTA', '|', NOW(), NOW()),
('speciality|ORTHO', 'Orthopédie', 'ORTHO', '|', NOW(), NOW()),
('speciality|ORL', 'Oto-rhino-laryngologie', 'ORL', '|', NOW(), NOW()),
('speciality|PEDIA', 'Pédiatrie', 'PEDIA', '|', NOW(), NOW()),
('speciality|PNEUM', 'Pneumologie', 'PNEUM', '|', NOW(), NOW()),
('speciality|PSYCH', 'Psychiatrie', 'PSYCH', '|', NOW(), NOW()),
('speciality|RADIO', 'Radiologie', 'RADIO', '|', NOW(), NOW()),
('speciality|RADOT', 'Radiothérapie', 'RADOT', '|', NOW(), NOW()),
('speciality|RHEUM', 'Rhumatologie', 'RHEUM', '|', NOW(), NOW()),
('speciality|UROLO', 'Urologie', 'UROLO', '|', NOW(), NOW()),
('speciality|MEDUR', 'Médecine d''urgence', 'MEDUR', '|', NOW(), NOW()),
('speciality|MEDTR', 'Médecine du travail', 'MEDTR', '|', NOW(), NOW()),
('speciality|MEDSP', 'Médecine sportive', 'MEDSP', '|', NOW(), NOW()),
('speciality|MEDNU', 'Médecine nucléaire', 'MEDNU', '|', NOW(), NOW()),
('speciality|ANATP', 'Anatomie pathologique', 'ANATP', '|', NOW(), NOW()),
('speciality|BIOLM', 'Biologie médicale', 'BIOLM', '|', NOW(), NOW()),
('speciality|BIOCH', 'Biochimie', 'BIOCH', '|', NOW(), NOW()),
('speciality|IMMUN', 'Immunologie', 'IMMUN', '|', NOW(), NOW()),
('speciality|MICRO', 'Microbiologie', 'MICRO', '|', NOW(), NOW()),
('speciality|PARAS', 'Parasitologie', 'PARAS', '|', NOW(), NOW()),
('speciality|PHARM', 'Pharmacologie', 'PHARM', '|', NOW(), NOW()),
('speciality|TOXIC', 'Toxicologie', 'TOXIC', '|', NOW(), NOW()),
('speciality|SANTE', 'Santé publique', 'SANTE', '|', NOW(), NOW()),
('speciality|EPIDE', 'Épidémiologie', 'EPIDE', '|', NOW(), NOW()),
('speciality|GENET', 'Génétique médicale', 'GENET', '|', NOW(), NOW()),
('speciality|NEONA', 'Néonatologie', 'NEONA', '|', NOW(), NOW()),
('speciality|PERIN', 'Périnatalogie', 'PERIN', '|', NOW(), NOW()),
('speciality|REANI', 'Réanimation', 'REANI', '|', NOW(), NOW()),
('speciality|ANGRY', 'Angiologie', 'ANGRY', '|', NOW(), NOW()),
('speciality|PHLEB', 'Phlébologie', 'PHLEB', '|', NOW(), NOW()),
('speciality|PROCT', 'Proctologie', 'PROCT', '|', NOW(), NOW()),
('speciality|STOMA', 'Stomatologie', 'STOMA', '|', NOW(), NOW()),
('speciality|ALLER', 'Allergologie', 'ALLER', '|', NOW(), NOW()),
('speciality|AUDIO', 'Audiologie', 'AUDIO', '|', NOW(), NOW()),
('speciality|OPTOM', 'Optométrie', 'OPTOM', '|', NOW(), NOW()),
('speciality|PSYEN', 'Psychologie', 'PSYEN', '|', NOW(), NOW()),
('speciality|PSYCHT', 'Psychothérapie', 'PSYCHT', '|', NOW(), NOW()),
('speciality|ERGOT', 'Ergothérapie', 'ERGOT', '|', NOW(), NOW()),
('speciality|KINES', 'Kinésithérapie', 'KINES', '|', NOW(), NOW()),
('speciality|ORTHP', 'Orthophonie', 'ORTHP', '|', NOW(), NOW()),
('speciality|DIETE', 'Diététique', 'DIETE', '|', NOW(), NOW()),
('speciality|NUTR', 'Nutrition', 'NUTR', '|', NOW(), NOW()),
('speciality|SAGE', 'Sage-femme', 'SAGE', '|', NOW(), NOW()),
('speciality|INFPE', 'Infirmier en pratique avancée', 'INFPE', '|', NOW(), NOW()),
('speciality|INFCL', 'Infirmier clinicien', 'INFCL', '|', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;


-- refresh tokens for the /users/reporting/login flow (rotating, revocable)
CREATE TABLE public.hippo_refresh_token (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL REFERENCES public.hippo_user(id),
    token_hash VARCHAR(64) NOT NULL UNIQUE,
    created timestamptz NOT NULL DEFAULT now(),
    expires timestamptz NOT NULL,
    revoked boolean NOT NULL DEFAULT false
);

CREATE INDEX ix_hippo_refresh_token_user_id ON public.hippo_refresh_token USING btree (user_id);
