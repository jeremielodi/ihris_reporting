<script>
import { defineComponent } from 'vue';
import AppMenuItem from './AppMenuItem.vue';
import router from '../router';
import OrgUnitService from '@/views/pages/manage/organization_units/orgUnit.service';
import Tree from '@/service/treeService.js';
import _AppCache from '../service/appCache';

export default defineComponent({
    name: 'PyramidMenu',
    components: { AppMenuItem },
    emits: ['treeUpdated', 'currentNode', 'loadingData'],

    data() {
        return {
            error: null,
            loading: false,
            nodes: [],
            access_facility_id: null,
            access_facility_name: null,
            access_facility_type: null,
            access_facility_target: 0,
            facility_parents: [],

            currentNodeKey: null
        };
    },

    mounted() {
        this.getAccessFacilityData();
    },

    methods: {
        getAccessFacilityData() {
            this.access_facility_id = _AppCache.getSession().access_facility_id;
            this.access_facility_name = localStorage.getItem('_access_facility_name');
            this.access_facility_type = localStorage.getItem('_access_facility_type');
            this.access_facility_target = Number(localStorage.getItem('_access_facility_target'));

            const jsonString = localStorage.getItem('_access_facility_parents');
            this.facility_parents = jsonString ? JSON.parse(jsonString) : [];
            this.getPyramidTarget();

            const node = {
                id: this.access_facility_id,
                key: this.access_facility_id,
                label: this.access_facility_name,
                type: this.access_facility_target
            };

            this.$emit('currentNode', node.id);
            this.$emit('treeUpdated');
        },
        formateNodes(nodes) {
            for (const node of nodes) {
                node.children = node.items;
                if (node.items && node.items.length !== 0) {
                    node.icon = 'pi pi-folder';
                    node.expandable = true;
                    this.formateNodes(node.items);
                } else {
                    node.icon = 'pi pi-file';
                    node.expandable = false;
                }
            }
        },
        getPyramidTarget() {
            this.loading = true;
            this.error = null;
            this.$emit('loadingData', this.loading);
            const facilityId = this.access_facility_id;
            this.currentNodeKey = facilityId;
            this.$store.commit('updateCurrentNode', facilityId);

            OrgUnitService.tree(facilityId)
                .then((res) => {
                    this.nodes = Tree(res);
                    this.formateNodes(this.nodes);
                    this.error = null;
                    this.$emit('currentNode', facilityId);
                    this.$emit('treeUpdated');
                })
                .catch((err) => {
                    this.error = err;
                })
                .finally(() => {
                    this.loading = false;
                    this.$emit('loadingData', this.loading);
                });
        },

        onNodeExpand(node) {
            if (this.currentNodeKey == null || this.currentNodeKey !== node.key) {
                this.$store.commit('updateCurrentNode', node.key);
                setTimeout(() => {
                    this.$emit('currentNode', node.key);
                    this.$emit('treeUpdated', node);
                }, 200);
            }
            this.currentNodeKey = node.key;
        }
    }
});
</script>

<template>
    <div class="text-center">
        <Button label="Pyramide sanitaire" @click="getAccessFacilityData()" :loading="loading" icon="pi pi-refresh" text severity="primary" rounded />
    </div>

    <ul class="layout-menu">
        <template v-for="(item, i) in nodes" :key="item.key || i">
            <app-menu-item v-if="!item.separator" :item="item" :index="i" @itemclick="onNodeExpand" />
            <li v-else class="menu-separator"></li>
        </template>
    </ul>
</template>

<style lang="scss" scoped></style>
