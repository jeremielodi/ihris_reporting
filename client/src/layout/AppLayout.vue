<script setup>
import { computed, watch, ref, onMounted } from 'vue';
import AppTopbar from './AppTopbar.vue';
import AppFooter from './AppFooter.vue';
import AppSidebar from './AppSidebar.vue';
import { useLayout } from '@/layout/composables/layout';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const { layoutConfig, layoutState, isSidebarActive, onMenuToggle } = useLayout();

const outsideClickListener = ref(null);
const validator = ref(0);
watch(isSidebarActive, (newVal) => {
    if (newVal) {
        bindOutsideClickListener();
    } else {
        unbindOutsideClickListener();
    }
});
onMounted(() => {
    validator.value = localStorage.getItem('validator');
    if (validator.value == 0) {
        careerItems.value.splice(careerItems.value.length - 2, 1);
    }
});

const containerClass = computed(() => {
    return {
        'layout-theme-light': layoutConfig.darkTheme.value === 'light',
        'layout-theme-dark': layoutConfig.darkTheme.value === 'dark',
        'layout-overlay': layoutConfig.menuMode.value === 'overlay',
        'layout-static': layoutConfig.menuMode.value === 'static',
        'layout-static-inactive': layoutState.staticMenuDesktopInactive.value && layoutConfig.menuMode.value === 'static',
        'layout-overlay-active': layoutState.overlayMenuActive.value,
        'layout-mobile-active': layoutState.staticMenuMobileActive.value,
        'p-input-filled': layoutConfig.inputStyle.value === 'filled',
        'p-ripple-disabled': !layoutConfig.ripple.value
    };
});
const bindOutsideClickListener = () => {
    if (!outsideClickListener.value) {
        outsideClickListener.value = (event) => {
            if (isOutsideClicked(event)) {
                layoutState.overlayMenuActive.value = false;
                layoutState.staticMenuMobileActive.value = false;
                layoutState.menuHoverActive.value = false;
            }
        };
        document.addEventListener('click', outsideClickListener.value);
    }
};
const unbindOutsideClickListener = () => {
    if (outsideClickListener.value) {
        document.removeEventListener('click', outsideClickListener);
        outsideClickListener.value = null;
    }
};
const isOutsideClicked = (event) => {
    const sidebarEl = document.querySelector('.layout-sidebar');
    const topbarEl = document.querySelector('.layout-menu-button');

    return !(sidebarEl.isSameNode(event.target) || sidebarEl.contains(event.target) || topbarEl.isSameNode(event.target) || topbarEl.contains(event.target));
};
const submenu_position = ref(0);
let elements = [
    {
        separator: true
    },
    {
        label: 'Tableau de bord 1',
        route: 'metabase_dashboard_list',
        icon: 'pi pi-chart-line',
        index: 0,
        command: () => {
            treeUpdated();
        }
    },
    {
        label: 'Tableau de bord 2',
        route: 'dashboard',
        icon: 'pi pi-chart-line',
        index: 0,
        command: () => {
            treeUpdated();
        }
    },
    {
        separator: true
    },
    {
        label: 'Complétudes',
        items: [
            {
                label: 'Interne',
                route: 'comp_interne',
                icon: 'pi pi-database',
                index: 1,
                command: () => {
                    treeUpdated();
                }
            },
            {
                label: 'Prestation',
                icon: 'pi pi-calendar',
                route: 'comp_prestation',
                index: 2,
                command: () => {
                    treeUpdated();
                }
            }
        ]
    },
    {
        separator: true
    },
    {
        label: 'Motivation',
        items: [
            {
                label: 'Salaire & Prime',
                icon: 'pi pi-money-bill',
                route: 'salaire_prime',
                index: 3,
                command: () => {
                    treeUpdated();
                }
            },
            {
                label: 'Revenus',
                icon: 'pi pi-dollar',
                route: 'revenus',
                index: 4,
                command: () => {
                    treeUpdated();
                }
            }
        ]
    },
    {
        separator: true
    },
    {
        label: 'Liste du personnel',
        icon: 'pi pi-list',
        route: 'people',
        index: 5,
        command: () => {
            treeUpdated();
        }
    },
    {
        label: 'Validations',
        icon: 'pi pi-check-circle',
        route: 'validation',
        index: 7,
        command: () => {
            treeUpdated();
        }
    }
];
let index = 0;
for (const el of elements) {
    if (el.label && !el.separator) {
        if (el.items && el.items.length > 0) {
            for (const elJ of el.items) {
                elJ.index = index;
                index++;
            }
        } else {
            el.index = index;
            index++;
        }
    }
}
const careerItems = ref(elements);

function getCareerRoute() {
    const sub = elements.filter((elt) => {
        if (elt.items && elt.items.length > 0) {
            const item1 = elt.items.filter((e) => {
                return route.path.indexOf(`${e.route}`) != -1;
            });
            return item1.length > 0;
        }
        return route.path.indexOf(`${elt.route}`) != -1;
    });
    return route.path.startsWith('/app/career') || sub.length > 0;
}

const trainingItems = ref([
    {
        separator: true
    },
    {
        label: 'Tableau de bord',
        icon: 'pi pi-chart-line',
        index: 0
    },
    {
        separator: true
    },
    {
        label: 'Formations organisées',
        icon: 'pi pi-table',
        index: 1
    },
    {
        label: 'Thématiques',
        icon: 'pi pi-list',
        index: 2
    }
]);

const onClickMenuItem = (item) => {
    submenu_position.value = item.index;
    const { overlayMenuActive, staticMenuMobileActive } = layoutState;
    if (staticMenuMobileActive.value || overlayMenuActive.value) {
        onMenuToggle();
    }
    gotoCareerSection(item);
};
const currentPR = ref(null);
const currentNode = ref(null);
const currentTR = ref(null);
const currentHA = ref(null);
const currentFacility = ref(null);
const myRouterView = ref(null);

const treeUpdated = () => {
    setTimeout(() => {
        if (myRouterView.value) myRouterView.value.treeUpdated(currentNode);
    }, 100);
};
function gotoCareerSection(item) {
    router.push(`/app/${item.route}`);
}
</script>

<template>
    <div class="layout-wrapper" :class="containerClass">
        <app-topbar :currentPR="currentPR" :currentTR="currentTR" :currentHA="currentHA" :currentFacility="currentFacility"></app-topbar>
        <div class="layout-sidebar">
            <div class="grid">
                <div class="col-7" style="height: calc(120vh - 9rem); overflow: scroll">
                    <app-sidebar
                        @treeUpdated="treeUpdated()"
                        @currentNode="currentNode = $event"
                        @currentPR="currentPR = $event"
                        @currentTR="currentTR = $event"
                        @currentHA="currentHA = $event"
                        @currentFacility="currentFacility = $event"
                    ></app-sidebar>
                </div>
                <div class="col-5 pl-0 border-left-1 border-200">
                    <div class="fixed" style="height: calc(120vh - 9rem); overflow: auto">
                        <Menu v-if="getCareerRoute()" :model="careerItems" class="w-full md:w-15rem border-0">
                            <template #start>
                                <Button icon="pi pi-caret-left" @click="$router.push('/')" severity="secondary" text rounded aria-label="" />
                                <span class="inline-flex align-items-center gap-1 px-3 pb-3">
                                    <span class="font-medium text-xl font-semibold">CARRIERE</span>
                                </span>
                            </template>
                            <template #submenuheader="{ item }">
                                <span class="text-primary font-bold">{{ item.label }}</span>
                            </template>
                            <template #item="{ item, props }">
                                <a v-ripple class="flex align-items-center" @click="onClickMenuItem(item)" :class="submenu_position == item.index ? 'surface-100 text-primary' : ''" v-bind="props.action">
                                    <span :class="item.icon" />
                                    <span class="ml-2">{{ item.label }}</span>
                                    <Badge v-if="item.badge" class="ml-auto" :value="item.badge" />
                                    <span v-if="item.shortcut" class="ml-auto border-1 surface-border border-round surface-100 text-xs p-1">{{ item.shortcut }}</span>
                                </a>
                            </template>
                        </Menu>

                        <Menu v-if="route.name == 'training'" :model="trainingItems" class="w-full md:w-15rem border-0">
                            <template #start>
                                <Button icon="pi pi-caret-left" @click="$router.push('/')" severity="secondary" text rounded aria-label="" />
                                <span class="inline-flex align-items-center gap-1 px-3 pb-3">
                                    <span class="font-medium text-xl font-semibold">FORMATIONS</span>
                                </span>
                            </template>
                            <template #submenuheader="{ item }">
                                <span class="text-primary font-bold">{{ item.label }}</span>
                            </template>
                            <template #item="{ item, props }">
                                <a v-ripple class="flex align-items-center" @click="onClickMenuItem(item.index)" :class="submenu_position == item.index ? 'surface-100 text-primary' : ''" v-bind="props.action">
                                    <span :class="item.icon" />
                                    <span class="ml-2">{{ item.label }}</span>
                                    <Badge v-if="item.badge" class="ml-auto" :value="item.badge" />
                                    <span v-if="item.shortcut" class="ml-auto border-1 surface-border border-round surface-100 text-xs p-1">{{ item.shortcut }}</span>
                                </a>
                            </template>
                        </Menu>
                    </div>
                </div>
            </div>
        </div>
        <div class="layout-main-container">
            <div class="layout-main">
                <RouterView v-slot="{ Component }">
                    <component ref="myRouterView" :is="Component" :submenu_position="submenu_position" :currentPR="currentPR" :currentTR="currentTR" :currentHA="currentHA" :currentFacility="currentFacility" />
                </RouterView>
            </div>
            <app-footer></app-footer>
        </div>
        <!--app-config></!--app-config -->
        <div class="layout-mask"></div>
    </div>
    <Toast />
</template>

<style lang="scss" scoped></style>
