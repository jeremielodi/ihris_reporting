import { createRouter, createWebHashHistory } from 'vue-router';
import AppLayout from '@/layout/AppLayout.vue';
import NProgress from 'nprogress';

const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        {
            path: '/',
            name: 'modules',
            component: () => import('@/layout/Modules.vue')
        },
        {
            path: '/app',
            component: AppLayout,
            children: [
                {
                    path: 'career',
                    name: 'career',
                    component: () => import('@/views/pages/career/Career.vue')
                },
                {
                    path: 'training',
                    name: 'training',
                    component: () => import('@/views/pages/training/Training.vue')
                },

                {
                    path: 'metabase_dashboard',
                    name: 'metabase_dashboard',
                    component: () => import('@/views/pages/career/metabase/metabase.vue')
                },
                {
                    path: 'metabase_dashboard_list',
                    name: 'metabase_dashboard_list',
                    component: () => import('@/views/pages/career/metabase/dashboard_list.vue')
                },
                {
                    path: 'dashboard',
                    name: 'dashboard',
                    component: () => import('@/views/pages/career/Dashboard.vue')
                },
                {
                    path: 'comp_interne',
                    name: 'comp_interne',
                    component: () => import('@/views/pages/career/CompInterne.vue')
                },
                {
                    path: 'comp_prestation',
                    name: 'comp_prestation',
                    component: () => import('@/views/pages/career/CompPrestation.vue')
                },
                {
                    path: 'salaire_prime',
                    name: 'salaire_prime',
                    component: () => import('@/views/pages/career/SalairePrime.vue')
                },
                {
                    path: 'revenus',
                    name: 'revenus',
                    component: () => import('@/views/pages/career/Revenus.vue')
                },
                {
                    path: 'people',
                    name: 'people',
                    component: () => import('@/views/pages/career/People.vue')
                },
                {
                    path: 'bonus_prime',
                    name: 'bonus_prime',
                    component: () => import('@/views/pages/career/BonusPrime.vue')
                },
                {
                    path: 'validation',
                    name: 'validation',
                    component: () => import('@/views/pages/career/Validation.vue')
                }
            ]
        },
        {
            path: '/manage',
            name: 'manage',
            component: () => import('@/views/pages/manage/manage.vue'),
            children: [
                {
                    path: 'home',
                    name: 'manage_home',
                    component: () => import('@/views/pages/manage/home.vue')
                },
                {
                    path: 'user_create',
                    name: 'user_create',
                    component: () => import('@/views/pages/manage/user/create.vue')
                },
                {
                    path: 'user_registry',
                    name: 'user_registry',
                    component: () => import('@/views/pages/manage/user/registry.vue')
                },
                {
                    path: 'degree_create',
                    name: 'degree_create',
                    component: () => import('@/views/pages/manage/degree/create.vue')
                },

                {
                    path: 'dashboard_registry',
                    name: 'dashboard_registry',
                    component: () => import('@/views/pages/manage/metabase_dashboard/registry.vue')
                },
                {
                    path: 'dashboard_create',
                    name: 'dashboard_create',
                    component: () => import('@/views/pages/manage/metabase_dashboard/create.vue')
                },
                {
                    path: 'org_unit_standards_create',
                    name: 'org_unit_standards_create',
                    component: () => import('@/views/pages/manage/standard/create.vue')
                },
                {
                    path: 'org_unit_standards_registry',
                    name: 'org_unit_standards_registry',
                    component: () => import('@/views/pages/manage/standard/registry.vue')
                },
                {
                    path: 'degree_registry',
                    name: 'degree_registry',
                    component: () => import('@/views/pages/manage/degree/registry.vue')
                },
                {
                    path: 'classification_registry',
                    name: 'classification_registry',
                    component: () => import('@/views/pages/manage/classification/registry.vue')
                },
                {
                    path: 'classification_create',
                    name: 'classification_create',
                    component: () => import('@/views/pages/manage/classification/create.vue')
                },
                {
                    path: 'grade_registry',
                    name: 'grade_registry',
                    component: () => import('@/views/pages/manage/grade/registry.vue')
                },
                {
                    path: 'grade_create',
                    name: 'grade_create',
                    component: () => import('@/views/pages/manage/grade/create.vue')
                },
                {
                    path: 'region_registry',
                    name: 'region_registry',
                    component: () => import('@/views/pages/manage/region/registry.vue')
                },
                {
                    path: 'region_create',
                    name: 'region_create',
                    component: () => import('@/views/pages/manage/region/create.vue')
                },
                {
                    path: 'district_registry',
                    name: 'district_registry',
                    component: () => import('@/views/pages/manage/district/registry.vue')
                },
                {
                    path: 'district_create',
                    name: 'district_create',
                    component: () => import('@/views/pages/manage/district/create.vue')
                },
                {
                    path: 'org_unit_registry',
                    name: 'org_unit_registry',
                    component: () => import('@/views/pages/manage/organization_units/registry.vue')
                },
                {
                    path: 'org_unit_create',
                    name: 'org_unit_create',
                    component: () => import('@/views/pages/manage/organization_units/create.vue')
                },

                {
                    path: 'county_registry',
                    name: 'county_registry',
                    component: () => import('@/views/pages/manage/county/registry.vue')
                },
                {
                    path: 'county_create',
                    name: 'county_create',
                    component: () => import('@/views/pages/manage/county/create.vue')
                },
                {
                    path: 'facility_registry',
                    name: 'facility_registry',
                    component: () => import('@/views/pages/manage/facility/registry.vue')
                },
                {
                    path: 'facility_create',
                    name: 'facility_create',
                    component: () => import('@/views/pages/manage/facility/create.vue')
                },
                {
                    path: 'health_area_registry',
                    name: 'health_area_registry',
                    component: () => import('@/views/pages/manage/healthArea/registry.vue')
                },
                {
                    path: 'health_area_create',
                    name: 'health_area_create',
                    component: () => import('@/views/pages/manage/healthArea/create.vue')
                },
                {
                    path: 'facility_type_registry',
                    name: 'facility_type_registry',
                    component: () => import('@/views/pages/manage/facility_type/registry.vue')
                },
                {
                    path: 'facility_type_create',
                    name: 'facility_type_create',
                    component: () => import('@/views/pages/manage/facility_type/create.vue')
                },

                {
                    path: 'cadre_registry',
                    name: 'cadre_registry',
                    component: () => import('@/views/pages/manage/cadre/registry.vue')
                },

                {
                    path: 'cadre_create',
                    name: 'cadre_create',
                    component: () => import('@/views/pages/manage/cadre/create.vue')
                },
                {
                    path: 'salary_source_registry',
                    name: 'salary_source_registry',
                    component: () => import('@/views/pages/manage/salary_source/registry.vue')
                },

                {
                    path: 'salary_source_create',
                    name: 'salary_source_create',
                    component: () => import('@/views/pages/manage/salary_source/create.vue')
                },

                {
                    path: 'job_type_create',
                    name: 'job_type_type_create',
                    component: () => import('@/views/pages/manage/job_type/create.vue')
                },
                {
                    path: 'job_type_registry',
                    name: 'job_type_registry',
                    component: () => import('@/views/pages/manage/job_type/registry.vue')
                },
                {
                    path: 'job_title_create',
                    name: 'job_title_create',
                    component: () => import('@/views/pages/manage/job_title/create.vue')
                },
                {
                    path: 'job_title_registry',
                    name: 'job_title_registry',
                    component: () => import('@/views/pages/manage/job_title/registry.vue')
                },
                {
                    path: 'educational_major_create',
                    name: 'educational_major_create',
                    component: () => import('@/views/pages/manage/educational_major/create.vue')
                },
                {
                    path: 'educational_major_registry',
                    name: 'educational_major_registry',
                    component: () => import('@/views/pages/manage/educational_major/registry.vue')
                },
                {
                    path: 'educational_level_create',
                    name: 'educational_level_create',
                    component: () => import('@/views/pages/manage/educational_level/create.vue')
                },
                {
                    path: 'educational_level_registry',
                    name: 'educational_level_registry',
                    component: () => import('@/views/pages/manage/educational_level/registry.vue')
                },
                {
                    path: 'institution_type_create',
                    name: 'institution_type_create',
                    component: () => import('@/views/pages/manage/institution_type/create.vue')
                },
                {
                    path: 'institution_type_registry',
                    name: 'institution_type_registry',
                    component: () => import('@/views/pages/manage/institution_type/registry.vue')
                },
                {
                    path: 'employment_status_create',
                    name: 'employment_status_create',
                    component: () => import('@/views/pages/manage/employment_status/create.vue')
                },
                {
                    path: 'employment_status_registry',
                    name: 'employment_status_registry',
                    component: () => import('@/views/pages/manage/employment_status/registry.vue')
                },
                {
                    path: 'reason_departure_create',
                    name: 'reason_departure_create',
                    component: () => import('@/views/pages/manage/reason_departure/create.vue')
                },
                {
                    path: 'reason_departure_registry',
                    name: 'reason_departure_registry',
                    component: () => import('@/views/pages/manage/reason_departure/registry.vue')
                },
                {
                    path: 'payment_frequency_create',
                    name: 'payment_frequency_create',
                    component: () => import('@/views/pages/manage/payment_frequency/create.vue')
                },
                {
                    path: 'payment_frequency_registry',
                    name: 'payment_frequency_registry',
                    component: () => import('@/views/pages/manage/payment_frequency/registry.vue')
                },
                {
                    path: 'people_registry',
                    name: 'people_registry',
                    component: () => import('@/views/pages/manage/people/registry.vue')
                },
                {
                    path: 'people_create',
                    name: 'people_create',
                    component: () => import('@/views/pages/manage/people/create.vue')
                },
                {
                    path: 'contact_type_registry',
                    name: 'contact_type_registry',
                    component: () => import('@/views/pages/manage/contact_type/registry.vue')
                },
                {
                    path: 'contact_type_create',
                    name: 'contact_type_create',
                    component: () => import('@/views/pages/manage/contact_type/create.vue')
                },

                {
                    path: 'setting_registry',
                    name: 'setting_registry',
                    component: () => import('@/views/pages/manage/setting/registry.vue')
                },
                {
                    path: 'setting_create',
                    name: 'setting_create',
                    component: () => import('@/views/pages/manage/setting/create.vue')
                },
                {
                    path: 'setting_logo',
                    name: 'setting_logo',
                    component: () => import('@/views/pages/manage/setting/logo_upload.vue')
                },
                {
                    path: 'identification_type_registry',
                    name: 'identification_type_registry',
                    component: () => import('@/views/pages/manage/identification_type/registry.vue')
                },
                {
                    path: 'identification_type_create',
                    name: 'identification_type_create',
                    component: () => import('@/views/pages/manage/identification_type/create.vue')
                },
                {
                    path: 'identification_create',
                    name: 'identification_create',
                    component: () => import('@/views/pages/manage/identification/create.vue')
                },
                {
                    path: 'contact_create',
                    name: 'contact_create',
                    component: () => import('@/views/pages/manage/contact/create.vue')
                },
                {
                    path: 'people_record_view',
                    name: 'people_record_view',
                    component: () => import('@/views/pages/manage/people/record_view.vue')
                },
                {
                    path: 'people_employment_status',
                    name: 'people_employment_status',
                    component: () => import('@/views/pages/manage/people/employment_status.vue')
                },
                {
                    path: 'people_passport',
                    name: 'people_passport',
                    component: () => import('@/views/pages/manage/people/people_passport.vue')
                },
                {
                    path: 'employment_staus_report',
                    name: 'employment_staus_report',
                    component: () => import('@/views/pages/manage/reports/employment_staus_report.vue')
                },
                {
                    path: 'timesheet',
                    name: 'timesheet',
                    component: () => import('@/views/pages/manage/timesheet/create.vue')
                },
                {
                    path: 'role_registry',
                    name: 'role_registry',
                    component: () => import('@/views/pages/manage/role/registry.vue')
                }
            ]
        },
        {
            path: '/auth/login',
            name: 'login',
            component: () => import('@/views/pages/auth/Login.vue')
        },
        {
            path: '/auth/access',
            name: 'accessDenied',
            component: () => import('@/views/pages/auth/Access.vue')
        },
        {
            path: '/auth/error',
            name: 'error',
            component: () => import('@/views/pages/auth/Error.vue')
        }
    ]
});

router.beforeEach((to, from, next) => {
    var a = localStorage.getItem('_ihris_token');
    var b = Number(localStorage.getItem('_vlogin'));

    if (b < 1 && to.name !== 'login') {
        router.push('/auth/login');
    }

    if (to.name !== 'login' && a == null) next({ name: 'login' });
    else next();
});

router.beforeResolve((to, from, next) => {
    //  if (to.name) {
    NProgress.start();
    //  }
    next();
});

router.afterEach(() => {
    NProgress.done();
});

export default router;
