<script>
import AppTopbar from './AppTopbar.vue';
import AppFooter from './AppFooter.vue';
import RoleService from '../views/pages/manage/role/roleService';

import { defineComponent } from 'vue';
import AppMenuItem from './AppMenuItem.vue';
import constants from '../service/constants';

export default defineComponent({
    name: 'ModuleList',
    components: { AppTopbar, AppFooter },
    data() {
        return {
            userManageAccess: false,
            reportingAccess: false,
            trainingAccess: false,
        };
    },
    created() {
        this.run();
    },
    methods: {
        async run() {
            const manage = constants.ACTIONS.CAN_ACCESS_MANAGE_MODULE;
            const reporting = constants.ACTIONS.CAN_ACCESS_REPORTING_MODULE;
            try {
                this.userManageAccess = await this.checkPermission(manage);
                this.reportingAccess = await this.checkPermission(reporting);
            } catch (error) {
                constants.log(error);
            }
        },
        checkPermission(id) {
            return RoleService.userHasAction(id);
        }
    }
});
</script>
<template>
    <div class="layout-wrapper">
        <app-topbar :topbar_button="false"></app-topbar>
        <div class="layout-main-container">
            <div class="layout-main">
                <div class="surface-ground module-landing">
                    <div class="module-grid">
                        <router-link v-if="userManageAccess" to="/manage/home" class="module-card">
                            <span class="module-icon bg-green-400">
                                <i class="text-50 pi pi-fw pi-cog text-2xl"></i>
                            </span>
                            <span class="module-text" data-testid="manage">
                                <span class="module-title">iHRIS Manage</span>
                                <span class="module-desc">Enregistrement des agents, configuration du système</span>
                            </span>
                            <i class="pi pi-angle-right module-chevron"></i>
                        </router-link>

                        <router-link v-if="reportingAccess" to="/app/career" class="module-card">
                            <span class="module-icon bg-cyan-400">
                                <i class="text-50 pi pi-fw pi-table text-2xl"></i>
                            </span>
                            <span class="module-text">
                                <span class="module-title">Gestion carrière</span>
                                <span class="module-desc">Visualiser les rapports, complétudes de prestation, Situation salaire & prime, éligibilité à la retraite...</span>
                            </span>
                            <i class="pi pi-angle-right module-chevron"></i>
                        </router-link>

                        <router-link v-if="trainingAccess" to="/app/training" class="module-card">
                            <span class="module-icon bg-orange-400">
                                <i class="pi pi-fw pi-question-circle text-50 text-2xl"></i>
                            </span>
                            <span class="module-text">
                                <span class="module-title">Formation continue</span>
                                <span class="module-desc">Formations programmées, personnel formé par catégorie professionnelle, test ...</span>
                            </span>
                            <i class="pi pi-angle-right module-chevron"></i>
                        </router-link>
                    </div>
                </div>
            </div>
            <app-footer></app-footer>
        </div>

        <div class="layout-mask"></div>
    </div>
</template>

<style scoped>
.module-landing {
    display: flex;
    justify-content: center;
    padding: 3rem 1.5rem;
}

.module-grid {
    width: 100%;
    max-width: 46rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.module-card {
    display: flex;
    align-items: center;
    gap: 1.25rem;
    padding: 1.5rem;
    background: var(--surface-card);
    border-radius: 14px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    border: 1px solid var(--surface-border);
    text-decoration: none;
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}

.module-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.1);
    border-color: var(--primary-color);
}

.module-icon {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 3.5rem;
    width: 3.5rem;
    border-radius: 12px;
}

.module-text {
    display: flex;
    flex-direction: column;
    min-width: 0;
}

.module-title {
    color: var(--text-color);
    font-size: 1.15rem;
    font-weight: 600;
    margin-bottom: 0.2rem;
}

.module-desc {
    color: var(--text-color-secondary);
    font-size: 0.9rem;
    line-height: 1.4;
}

.module-chevron {
    margin-left: auto;
    color: var(--text-color-secondary);
    font-size: 1.1rem;
    flex-shrink: 0;
}
</style>
