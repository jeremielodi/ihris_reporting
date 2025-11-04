<script>
import OrgUnitService from '@/views/pages/manage/organization_units/orgUnit.service';
import _AppCache from '../../../service/appCache';

export default {
    name: 'ReportsContainer',
    props: {
        submenu_position: { type: Number, default: 0 }
    },
    emits: ['currentNode', 'treeUpdated'],
    data() {
        return {
            bItems: [],
            blocked: true,
            currentNode: null,
        };
    },
    watch: {
        '$store.state.currentNode': function (newVal) {
            console.log('changed', newVal);
            this.blocked = true;
            this.$store.commit('updateblockReportPreview', true);
        }
    },
    computed: {
        // Remove activeComp computation since RouterView handles this
    },
    mounted() {
        if (this.$route.name == 'career') {
            this.$router.push('/app/metabase_dashboard_list');
        }
    },
    methods: {
        async treeUpdatedAndLoadData() {
            this.$store.commit('updateblockReportPreview', false);
            const id = this.$store.state.currentNode;
            if (!id) return false;
            this.$emit('currentNode', id);
            this.$emit('treeUpdated', { id });
            this.blocked = false;
        },

        async treeUpdated(node) {
            if (node && node.id) {
                this.$store.commit('updateCurrentNode', node.id);
            }
            this.$store.commit('updateblockReportPreview', true);
            const id = this.$store.state.currentNode;
            if (!id) return;
            this.currentNode = id;
            _AppCache.setCurrentNode(this.currentNode);
            try {
                const result = await OrgUnitService.path(id);
                this.bItems = result;
                // Refresh current component when node changes
               // this.refreshCurrentComponent();
            } catch (e) {
                console.error(e);
            }
        },
        
    }
};
</script>

<template>
    <div class="card p-2 pb-1">
        <div class="grid">
            <div class="col-10 pb-0">
                <Breadcrumb :model="bItems" class="border-0">
                    <template #item="{ item }">
                        <span>
                            {{ item.name }}
                        </span>
                    </template>
                    <template #separator> / </template>
                </Breadcrumb>
            </div>
            <div class="col-2 pb-0 text-right">
                <Button title="Actualiser" @click="treeUpdatedAndLoadData()" icon="pi pi-refresh" severity="primary" raised />
            </div>
        </div>
    </div>

    <div class="pt-0">
        <RouterView ref="routerView" />
    </div>
</template>