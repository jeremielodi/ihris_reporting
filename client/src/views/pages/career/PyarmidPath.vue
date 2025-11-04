<script>
import OrgUnitService from '@/views/pages/manage/organization_units/orgUnit.service';


export default {
    name: 'PyramidPath',
    props: {
        submenu_position: { type: Number, default: 0 },
        reload: {type: Function, default : ()=> {}},
    },
    data() {
        return {
            bItems: [],
            currentNode: null,
        };
    },
    watch: {
        '$store.state.currentNode': function (newVal) {
            this.getPath(newVal);
        }
    },
    created() {
        const id = this.$store.state.currentNode;
        this.getPath(id);
    },
    methods: {
        async getPath(nodeId) {
            const result = await OrgUnitService.path(nodeId);
            this.bItems = result;
            this.reload();
        }
    }
};
</script>

<template>
    <div class="card col-12">
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
                <Button title="Actualiser" @click="reload()" icon="pi pi-refresh" severity="primary" raised />
            </div>
        </div>
    </div>
</template>