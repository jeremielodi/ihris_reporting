<script>
import { defineComponent, computed } from 'vue';
import AppTopbar from '../../../layout/AppTopbar.vue';
import AppSidebar from '../../../layout/AppSidebar.vue';
import AppFooter from '../../../layout/AppFooter.vue';
import AppMenuItem from '../../../layout/AppMenuItem.vue';
import appsubmenu from '../../../layout/AppSubmenu.vue';
import { useLayout } from '@/layout/composables/layout';
import router from '../../../router';
import RoleService from './role/roleService';

export default defineComponent({
    name: 'iHRISManage',
    components: { AppTopbar, AppSidebar, AppFooter, AppMenuItem, appsubmenu },

    data() {
        return {
            currentPR: null,
            currentTR: null,
            currentHA: null,
            selectedKey: null,
            currentFacility: null,
            submenu_position: 0,
            nodes: []
        };
    },

    created() {
        this.updateMenu();
    },

    setup() {
        // Use composable inside setup to get reactive refs
        const { layoutConfig, layoutState } = useLayout();

        // computed reactive container class
        const containerClass = computed(() => ({
            'layout-theme-light': layoutConfig.darkTheme.value === 'light',
            'layout-theme-dark': layoutConfig.darkTheme.value === 'dark',
            'layout-overlay': layoutConfig.menuMode.value === 'overlay',
            'layout-static': layoutConfig.menuMode.value === 'static',
            'layout-static-inactive': layoutState.staticMenuDesktopInactive.value && layoutConfig.menuMode.value === 'static',
            'layout-overlay-active': layoutState.overlayMenuActive.value,
            'layout-mobile-active': layoutState.staticMenuMobileActive.value,
            'p-input-filled': layoutConfig.inputStyle.value === 'filled',
            'p-ripple-disabled': !layoutConfig.ripple.value
        }));

        return { containerClass };
    },

    computed: {
        bItems() {
            const list = [];
            if (this.currentPR) list.push(this.currentPR);
            if (this.currentTR) list.push(this.currentTR);
            if (this.currentHA) list.push(this.currentHA);
            if (this.currentFacility) list.push(this.currentFacility);
            return list;
        }
    },

    methods: {
        updateMenu() {
            const userId = localStorage.getItem("_ihris_user_id");
            RoleService.loadUserModules(userId).then(modules => {
                const moduleMap = {};
                let moduels = modules.map((m) => {
                    m.key = m.id;
                    m.label = this.$t(m.label);
                    m.items = (m.pages || []).filter((p) => !!p.is_tree_item);
                    for (const item of m.items) {
                        item.key = item.code;
                        item.label = this.$t(item.label);
                    }
                    moduleMap[m.id] = m;
                    return m;
                });
                moduels.forEach((m) => {
                    if (m.parent) {
                        moduleMap[m.parent].items.push(m);
                    }
                });

                this.nodes = modules.filter((m) => !m.parent && m.items.length > 0).sort((a, b) => a.id - b.id);

                this.formateNodes(this.nodes);
            });

        },
        onMenuItemClick(evt) {
            router.push(`/manage/${evt.item.key}`);
        },

        treeUpdated() {
            // Vue 3 refs inside Options API: access via $refs, not this.myRouterView.value
            if (this.$refs.myRouterView && this.$refs.myRouterView.treeUpdated) {
                this.$refs.myRouterView.treeUpdated();
            }
        },
        formateNodes(nodes) {
            for (const node of nodes) {
                node.children = node.items;
                if (node.items && node.items.length !== 0) {
                    node.icon = 'pi pi-folder';
                    this.formateNodes(node.items);
                } else {
                    node.icon = 'pi pi-file';
                }
            }
        },
        nodeSelect(node) {
            if (node.items && node.items.length !== 0) return;
            this.$router.push(`/manage/${node.key}`);
        }
    }
});
</script>

<template>
    <div class="layout-wrapper" :class="containerClass">
        <AppTopbar moduleName="iHRIS Manage" @language-changed="updateMenu" :currentPR="currentPR"
            :currentTR="currentTR" :currentHA="currentHA" :currentFacility="currentFacility" />
        <div class="layout-sidebar">
            <div class="grid">
                <div class="col-12" style="height: calc(100vh - 9rem); overflow: scroll">
                    <Tree v-model:selectionKeys="selectedKey" @nodeSelect="nodeSelect" :value="nodes"
                        style="width: 100%; padding:0px" selectionMode="single" class="w-full md:w-[30rem] myAppMenu">
                    </Tree>

                    <!-- <appsubmenu :items="nodes" class="layout-menu" :root="true" @menuitem-click="onMenuItemClick" />   -->
                </div>
            </div>
        </div>

        <div class="card p-2 pb-1">
            <div class="grid">
                <div class="col-10 pb-0">
                    <Breadcrumb :model="bItems" class="border-0" />
                </div>
                <div class="col-2 pb-0 text-right">
                    <Button v-if="submenu_position === 0" title="Actualiser" @click="treeUpdated" icon="pi pi-refresh"
                        severity="primary" raised />
                </div>
            </div>
        </div>

        <div class="layout-main-container" style="height: 20vh !important">
            <div class="layout-main">
                <RouterView v-slot="{ Component }">
                    <component ref="myRouterView" :is="Component" :submenu_position="submenu_position"
                        :currentPR="currentPR" :currentTR="currentTR" :currentHA="currentHA"
                        :currentFacility="currentFacility" />
                </RouterView>
            </div>
            <AppFooter />
        </div>
    </div>
</template>
<style scoped>
.layout-main {
    min-height: 60vh;
}

.myAppMenu {
    font-size: 14px !important;
}

.myAppMenu :deep(.p-tree-node-content) {
    border-radius: 8px;
    padding: 0.6rem 0.75rem;
    margin-bottom: 2px;
    transition: background-color 0.15s ease;
}

.myAppMenu :deep(.p-tree-node-content:hover) {
    background: var(--surface-hover);
}

.myAppMenu :deep(.p-tree-node-selected) {
    background: var(--primary-50, #eef2ff) !important;
    box-shadow: inset 3px 0 0 0 var(--primary-color, #6366f1);
}

.myAppMenu :deep(.p-tree-node-selected .p-tree-node-label) {
    color: var(--primary-color, #6366f1);
    font-weight: 600;
}

.myAppMenu :deep(.p-tree-root-children > .p-tree-node > .p-tree-node-content .p-tree-node-label) {
    font-weight: 600;
}

.myAppMenu :deep(.p-tree-node-icon.pi-folder) {
    color: var(--primary-color, #6366f1);
}

.myAppMenu :deep(.p-tree-node-icon.pi-file) {
    color: var(--text-color-secondary);
    font-size: 0.85rem;
}

.myAppMenu :deep(.p-tree-node-toggle-button) {
    width: 1.5rem;
    height: 1.5rem;
}

.myAppMenu :deep(.p-tree-node-children) {
    padding-left: 0.75rem;
}

.manage-container {
    margin-top: -65px;
    background: #fff;
    position: relative;
}

.layout-sidebar {
    width: 280px;
    padding-top: 20px;
}

@media screen and (max-width: 950px) {
    .layout-sidebar {
        margin-top: 70px;
        padding-left: 40px !important;
    }
}

@media (min-width: 992px) {
    .layout-wrapper.layout-static .layout-main-container {
        margin-left: 250px;
    }

    /* Collapsed state (toggle button in the topbar): let the page reclaim
       the full width, same as the main app layout does. Needs to be
       re-declared here (not just inherited from _responsive.scss) because
       Vue's scoped-style attribute bumps this rule's specificity above the
       plain margin-left:250px rule above, so without this override toggling
       the menu would leave the content pinned at 250px. */
    .layout-wrapper.layout-static.layout-static-inactive .layout-main-container {
        margin-left: 0;
        padding-left: 2rem;
    }
}
</style>
