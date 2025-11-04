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
                <div class="surface-ground">
                    <div class="flex flex-column align-items-center justify-content-center">
                        <div style="border-radius: 56px; padding: 0.3rem">
                            <div class="w-full surface-card pb-4 sm:px-8 flex flex-column align-items-center">
                                <br /><br />
                                <router-link v-if="userManageAccess" to="/manage/home" class="w-full flex align-items-center py-5 border-300 border-bottom-1">
                                    <span class="flex justify-content-center align-items-center bg-green-400 border-round" style="height: 3.5rem; width: 3.5rem">
                                        <i class="text-50 pi pi-fw pi-cog text-2xl"></i>
                                    </span>
                                    <span class="ml-4 flex flex-column">
                                        <span class="text-900 lg:text-xl font-medium mb-0 block">iHRIS Manage</span>
                                        <span class="text-600 lg:text-xl">Enregistrement des agents, configuration du système</span>
                                    </span>
                                </router-link>

                                <router-link v-if="reportingAccess" to="/app/career" class="w-full flex align-items-center py-5 border-300 border-bottom-1">
                                    <span class="flex justify-content-center align-items-center bg-cyan-400 border-round" style="height: 3.5rem; width: 3.5rem">
                                        <i class="text-50 pi pi-fw pi-table text-2xl"></i>
                                    </span>
                                    <span class="ml-4 flex flex-column">
                                        <span class="text-900 lg:text-xl font-medium mb-0 block">Gestion carrière</span>
                                        <span class="text-600 lg:text-xl">Visualiser les rapports, complétudes de prestation, Situation salaire & prime, éligibilité à la retraite...</span>
                                    </span>
                                </router-link>

                                <router-link v-if="trainingAccess" to="/app/training" class="w-full flex align-items-center py-5 border-300">
                                    <span class="flex justify-content-center align-items-center bg-orange-400 border-round" style="height: 3.5rem; width: 3.5rem">
                                        <i class="pi pi-fw pi-question-circle text-50 text-2xl"></i>
                                    </span>
                                    <span class="ml-4 flex flex-column">
                                        <span class="text-900 lg:text-xl font-medium mb-0">Formation continue</span>
                                        <span class="text-600 lg:text-xl">Formations programmées, personnel formé par catégorie professionnelle, test ...</span>
                                    </span>
                                </router-link>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <app-footer></app-footer>
        </div>

        <div class="layout-mask"></div>
    </div>
</template>
