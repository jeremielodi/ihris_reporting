INSERT INTO public.setting (id, app_name, app_version, responsible_name, responsible_number)
VALUES(1, 'IHRIS Reporting', '1.0.0', 'Admin', '+2350000');

-- Idempotent bootstrap for default admin + superuser permissions
-- Default login: username = 'ihris', password = 'admin'

-- If you use gen_random_uuid() below, make sure pgcrypto is enabled once:
-- CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1) Admin user (keep the bcrypt hash so password stays 'admin')
INSERT INTO public.hippo_user (id, username, firstname, lastname, email, password)
VALUES ('user|admin', 'ihris', 'Admin', NULL, 'admin@test.com',
        '$2b$12$jfGSa9zY2C.LjW2HeYPnY.zig.DzOh1bXE.sjYorbcoFvBQStn6ci')
ON CONFLICT (id) DO NOTHING;

-- 2) Access facility for the admin (adjust location if needed)
INSERT INTO public.hippo_access_facility (id, parent, created, last_modified, location)
VALUES ('access|admin|country|CD', 'user|admin', NOW(), NOW(), 'country|CD')
ON CONFLICT (id) DO NOTHING;

-- 3) Superuser role (assignable = 1)
INSERT INTO public.hippo_role (id, name, created, last_modified, assignable)
VALUES ('role|superuser', 'Super user', NOW(), NOW(), 1)
ON CONFLICT (id) DO NOTHING;

-- 4) Grant ALL module pages to superuser, but avoid duplicates
--    (Assumes hippo_role_page has (uuid, page_code, role_id) and
--     uniqueness on (page_code, role_id) either via constraint or logic below)
INSERT INTO public.hippo_role_page (uuid, page_code, role_id)
SELECT gen_random_uuid(), p.code, 'role|superuser'
FROM public.hippo_module_page p
LEFT JOIN public.hippo_role_page rp
  ON rp.page_code = p.code AND rp.role_id = 'role|superuser'
WHERE rp.page_code IS NULL;

-- 5) Link admin user to superuser role (avoid duplicates)
INSERT INTO public.hippo_user_role (uuid, user_id, role_id)
SELECT gen_random_uuid(), 'user|admin', 'role|superuser'
WHERE NOT EXISTS (
  SELECT 1
  FROM public.hippo_user_role
  WHERE user_id = 'user|admin' AND role_id = 'role|superuser'
);

INSERT INTO public.hippo_role_actions(uuid, role_id, actions_id)
SELECT gen_random_uuid(), 'role|superuser', id
FROM public.hippo_actions;

INSERT INTO public.hippo_gender VALUES 
('gender|F',NULL, NOW(), NOW(),'',0,'Female'),
('gender|M',NULL, NOW(), NOW(),'',0,'Male');

INSERT INTO public.hippo_marital_status VALUES 
('marital_status|1',NULL,'2014-07-12 13:22:58', NOW(),'',0,'CÉLIBATAIRE'),
('marital_status|2',NULL,'2014-07-12 13:23:00',NOW(),'',0,'DIVORCÉ'),
('marital_status|3',NULL,'2014-07-12 13:23:00',NOW(),'',0,'MARIÉ'),
('marital_status|4',NULL,'2014-10-18 09:00:03',NOW(),'',0,'VEUF(VE)');

INSERT INTO public.organization_level (id, name, level) values
('country', 'Pays', 0),
('province', 'Province', 1),
('district', 'District', 2),
('facility', 'Structure', 3);

-- the ids of organisation_level are key word, don't change them:
-- country, province, region, district, health_zone, health_area,county, facility, 

INSERT INTO public.organization_unit_type (id, name, position) values
('ORG_UNIT_TYPE_RURAL', 'Rural', 1),
('ORG_UNIT_TYPE_URBAN', 'Urbain', 2);
