<script>
import { defineComponent } from 'vue';
import { FilterMatchMode } from '@primevue/core/api';
import OrgUnitService from './orgUnit.service';
import Tree from '@/service/treeService.js';
import ImportModal from './import_modal.vue';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'Payment_frequencyRegistry',
    data() {
        return {
            orgUnits: null,
            payment_frequencys: [],
            selectedUser: null,
            displayImportModal: false,
            loading: false,
            filters1: { global: { value: null, matchMode: FilterMatchMode.CONTAINS } }
        };
    },
    components:{
        ImportModal,
    },
    created() {
        this.load();
    },
    methods: {
        openImportModal() {
            this.displayImportModal = true;
        },
        closeImportDialog(data) {
            if (data) {
                OrgUnitService.import(data)
                    .then(() => {
                        this.displayImportModal = false;
                        NotifyService.success(this, '', null);
                        this.load();
                    })
                    .catch(() => {
                        NotifyService.danger(this, '', null);
                    });
            } else {
                this.displayImportModal = false;
            }
        },
        formateNodes(nodes) {
            for (const node of nodes) {
                node.children = node.items;
                node.key = node.key || node.id;
                node.data = {
                    name: node.name || node.label,
                    type: node.type
                };
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
        editItem(node) {
            this.$router.push(`/manage/org_unit_create?id=${node.id}`);
        },
        addChild(node) {
            this.$router.push(`/manage/org_unit_create?parent=${node.id}`);
        },
        load() {
            OrgUnitService.read().then((orgs) => {
                this.orgUnits = Tree(orgs);
                this.formateNodes(this.orgUnits);
                console.log(this.orgUnits);
            });
        },
        downloadAsXLSX() {
            OrgUnitService.downloadAsXLSX().then((blob) => {
                const a = document.createElement('a');
                const href = URL.createObjectURL(blob);
                a.href = href;
                a.download = 'organisations.xlsx';
                document.body.appendChild(a);
                a.click();
                a.remove();
                URL.revokeObjectURL(href);
            });
        }
    }
});
</script>
<template>
    <div class="card manage-container" style="height: 90vh">
        <TreeTable :value="orgUnits">
            <template #header>
                <h4>{{ $t('TREE.ORG_UNIT') }}</h4>
                <div class="flex justify-content-between flex-column sm:flex-row">
                    <span></span>

                    <span>
                        <InputGroup>
                            <InputGroupAddon>
                                <i class="pi pi-search"></i>
                            </InputGroupAddon>
                            <InputText v-model="filters1['global'].value" placeholder="Search" />
                            <Button :label="$t('FORM.BUTTONS.ADD')" @click="this.$router.push('/manage/org_unit_create')" icon="pi pi-plus" />
                             <Button :label="$t('FORM.BUTTONS.DOWNLOAD')" severity="secondary" @click="downloadAsXLSX()" icon="pi pi-download" />
                             <Button :label="$t('FORM.BUTTONS.IMPORT')" severity="warn" @click="openImportModal()" icon="pi pi-upload" />
                        </InputGroup>
                    </span>
                </div>
            </template>

            <Column field="name" header="Name" expander> </Column>
            <Column field="type" header="Type"></Column>
            <Column header="Actions" style="width: 20%">
                <template #body="slotProps">
                    <Button icon="pi pi-pencil" label="Fils" class="p-button-rounded p-button-success p-mr-2" @click="addChild(slotProps.node)" />
                    <Button icon="pi pi-pencil" label="Edit"  class="p-button-rounded p-button-secondary p-mr-2" @click="editItem(slotProps.node)" />
                </template>
            </Column>
        </TreeTable>
        <ImportModal ref="importModal" :close="closeImportDialog" :display="displayImportModal" />
    </div>
</template>
