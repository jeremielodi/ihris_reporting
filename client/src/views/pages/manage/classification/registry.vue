<script>
import { defineComponent } from 'vue';
import ClassificationService from './classification.service';
import ClassificationAction from './actions.vue';
import { FilterMatchMode } from '@primevue/core/api';
import ImportModal from './import_modal.vue';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'DegreeRegistry',
    data() {
        return {
            degrees: [],
            selectedUser: null,
            loading: false,
            displayImportModal: false,
            filters1: { global: { value: null, matchMode: FilterMatchMode.CONTAINS } }
        };
    },
    created() {
        console.log('UserRegistry Component Created');
        this.loadData();
    },
    components: {
        ClassificationAction,
        ImportModal
    },
    methods: {
        loadData() {
            this.loading = true;
            ClassificationService.read()
                .then((degrees) => {
                    this.degrees = degrees;
                })
                .catch((error) => {
                    console.error('Error fetching user data:', error);
                })
                .finally(() => {
                    this.loading = false;
                });
        },
        openImportModal() {
            this.displayImportModal = true;
        },
        onRowSelect(event) {
            console.log('Row selected:', event.value);
            this.selectedUser = event.value;
        },
        onFilter(event) {
            this.filters = event.filters;
        },
        closeImportDialog(data) {
            if (data) {
                ClassificationService.import(data)
                    .then((res) => {
                        this.displayImportModal = false;
                        NotifyService.success(this, '', null);
                        this.loadData();
                    })
                    .catch(() => {
                        NotifyService.danger(this, '', null);
                    });
            } else {
                this.displayImportModal = false;
            }
        }
    }
});
</script>

<template>
    <div class="card manage-container" style="height: 90vh">
        <DataTable
            :value="degrees"
            v-model:filters="filters1"
            v-model:selection="selectedUser"
            dataKey="id"
            showGridlines
            stripedRows
            resizableColumns
            columnResizeMode="fit"
            scrollable
            scrollHeight="flex"
            responsiveLayout="scroll"
            selectionMode="single"
            :loading="loading"
        >
            <template #header>
                <h4>{{ $t('TREE.CLASSIFICATIONS') }}</h4>
                <div class="flex justify-content-between flex-column sm:flex-row">
                    <span></span>

                    <span>
                        <InputGroup>
                            <InputGroupAddon>
                                <i class="pi pi-search"></i>
                            </InputGroupAddon>
                            <InputText v-model="filters1['global'].value" placeholder="Search" />
                            <Button :label="$t('FORM.BUTTONS.ADD')" @click="this.$router.push('/manage/classification_create')" icon="pi pi-plus" />
                            <Button :label="$t('FORM.BUTTONS.IMPORT')" severity="secondary" @click="openImportModal()" icon="pi pi-upload" />
                        </InputGroup>
                    </span>
                </div>
            </template>

            <Column selectionMode="single" style="width: 20px" />

            <Column field="name" :header="$t('FORM.LABELS.NAME')" />

            <Column field="code" :header="$t('FORM.LABELS.CODE')" />
            <Column field="description" :header="$t('FORM.LABELS.DESCRIPTION')" />
            <Column field="actions" :header="$t('Actions')" style="width: 80px">
                <template #body="{ data }">
                    <ClassificationAction :entity="data" action-id="classifAction" />
                </template>
            </Column>
        </DataTable>
        <div>
            <b>{{ degrees.length }} {{ $t('TREE.CLASSIFICATIONS') }} </b>
        </div>

        <ImportModal ref="importModal" :close="closeImportDialog" :display="displayImportModal" />
    </div>
</template>
<style scoped>
.p-datatable.p-datatable-gridlines .p-datatable-tbody > tr > td {
    border-width: 1px;
    font-size: 12px;
    padding: 1px;
    padding-left: 2px;
}
.p-column-title {
    font-size: 14px;
}

.p-filter-column {
    padding: 2px !important;
    font-size: 10px;
}
.p-filter-column .p-inputtext {
    height: 30px;
}
.p-filter-column .p-column-filter-menu-button,
.p-filter-column .p-column-filter-clear-button {
    display: none !important;
}
</style>
