<script>
import { defineComponent } from 'vue';
import apiService from '../../service/ApiService';
import _AppCache from '../../service/appCache';
import AppMenuItem from '../../layout/AppMenuItem.vue';
import OrgUnitService from '@/views/pages/manage/organization_units/orgUnit.service';
import Tree from '@/service/treeService.js';
import util from '../../service/UtilService';

export default defineComponent({
    number: 'CreateUpdateModal',
    props: {
        BudgetLine: Object,
        close: Function,
        clone: {
            type: Boolean,
            default: false
        },
        display: {
            type: Boolean,
            default: false
        },
        getAllNodes: {
            type: Boolean,
            default: false
        }
    },
    data() {
        return {
            loading: false,
            error: null,
            currentNodeKey: null,
            currentNode: null,
            displayModal: false,
            items: [],
            nodes: [],
            projects: [],
            selectedBudgetLine: {},
            selectedProject: {},
            validationErrors: {},
            enterprise: {},
            submitted: false
        };
    },
    components: {
        AppMenuItem
    },
    watch: {
        display(newVal) {
            if (newVal) {
                this.find();
            }
        }
    },
    methods: {
        closeDialog() {
            this.submitted = false;
            this.selectedBudgetLine = {};
            this.close(null);
        },
        submit() {
            this.close(this.currentNode);
        },
        find() {
            this.getPyramidTarget(100);
        },

        getNodeDetails(id) {
            OrgUnitService.read(id).then((unit) => {
                this.currentNode = { key: id, label: unit.name };
            });
        },

        formateNodes(nodes) {
            for (const node of nodes) {
                console.log(node);
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
        getPyramidTarget(time) {
            util.sleep(time || 0);
            this.loading = true;
            const session = _AppCache.getSession();
            const facilityId = session.access_facility_id;
            const operation = this.getAllNodes ? OrgUnitService.read():
            OrgUnitService.tree(facilityId);
                operation.then((res) => {
                    this.getNodeDetails(facilityId);
                    this.nodes = Tree(res);
                    this.formateNodes(this.nodes);
                    this.error = null;
                })
                .catch((err) => {
                    console.error(err);
                    this.error = err;
                    this.loading = false;
                })
                .finally(() => {
                    this.loading = false;
                });
        },
        onNodeExpand(node) {
            console.log(node);
            this.currentNode = node;
            this.currentNodeKey = node.key;
        }
    }
});
</script>

<template>
    <Dialog v-if="display" :header="$t('FORM.LABELS.ORG_UNITS')" :closable="false" position="top" :style="{ width: '35vw' }" :modal="true" :visible="display" footer="Footer">
        <div class="col-12">
            <div class="text-center">
                <Button label="Pyramide sanitaire" @click="getPyramidTarget()" :loading="loading" icon="pi pi-refresh" text severity="primary" rounded />
            </div>
            <ul class="layout-menu">
                <template v-for="(item, i) in nodes" :key="item.key">
                    <AppMenuItem v-if="!item.separator" :item="item" :index="i" @itemclick="(n) => onNodeExpand(n)" />
                    <li v-if="item.separator" class="menu-separator"></li>
                </template>
            </ul>
        </div>
        <template #footer>
            <div style="float: left; width: 100%" v-if="currentNode">
                <h4 class="text-primary">{{ currentNode.label }}</h4>
            </div>

            <div style="float: right; width: 100%">
                <Button style="float: right" :label="$t('FORM.BUTTONS.CANCEL')" @click="closeDialog" class="p-button-text" />
                <Button style="float: right" v-if="currentNode" type="submit" @click="submit" :label="$t('FORM.LABELS.SELECT')" />
            </div>
        </template>
    </Dialog>
</template>

<style>
.p-dialog-footer {
    padding-top: 10px !important;
    background-color: blue;
}
</style>
