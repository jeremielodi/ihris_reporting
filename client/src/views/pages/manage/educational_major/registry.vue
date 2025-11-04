<script>
import { defineComponent } from 'vue';
import EducationalMajorService from './educational_major.service';
import EDUCATIONAL_MAJORAction from './actions.vue';
import { FilterMatchMode } from '@primevue/core/api';
import ImportModal from './import_modal.vue';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'EDUCATIONAL_MAJORRegistry',
    data() {
        return {
            educationalMajor: [],
            selectedUser: null,
            displayImportModal: false,
            loading: false,
            filters1: { global: { value: null, matchMode: FilterMatchMode.CONTAINS } }
        };
    },
    created() {
        this.loadData();
    },
    components: {
        EDUCATIONAL_MAJORAction,
        ImportModal,
    },
    methods: {
        openImportModal() {
            this.displayImportModal = true;
        },
        closeImportDialog(data) {
            if (data) {
                EducationalMajorService.import(data)
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
        },
        loadData() {
            this.loading = true;
            EducationalMajorService.read()
                .then((educationalMajor) => {
                    this.educationalMajor = educationalMajor;
                })
                .catch((error) => {
                    console.error('Error fetching user data:', error);
                })
                .finally(() => {
                    this.loading = false;
                });
        },
        onRowSelect(event) {
            console.log('Row selected:', event.value);
            this.selectedUser = event.value;
        },
        onFilter(event) {
            this.filters = event.filters;
        }
    }
});
</script>

<template>
    <div class="card manage-container" style="height: 90vh">
        <DataTable
            :value="educationalMajor"
            v-model:selection="selectedUser"
            dataKey="id"
            showGridlines
            stripedRows
            resizableColumns
            columnResizeMode="fit"
            scrollable
            scrollHeight="flex"
            responsiveLayout="scroll"
            :filters="filters1"
            selectionMode="single"
            :loading="loading"
        >
            <template #header>
                <h4>{{ $t('TREE.EDUCATIONAL_MAJOR') }}</h4>
                <div class="flex justify-content-between flex-column sm:flex-row">
                    <span></span>

                    <span>
                        <InputGroup>
                            <InputGroupAddon>
                                <i class="pi pi-search"></i>
                            </InputGroupAddon>
                            <InputText v-model="filters1['global'].value" placeholder="Search" />
                            <Button :label="$t('FORM.BUTTONS.ADD')" @click="this.$router.push('/manage/educational_major_create')" icon="pi pi-plus" />
                            <Button :label="$t('FORM.BUTTONS.IMPORT')" severity="secondary" @click="openImportModal()" icon="pi pi-upload" />
                        </InputGroup>
                    </span>
                </div>
            </template>

            <Column selectionMode="single" style="width: 20px"></Column>
            <Column field="code" :header="$t('FORM.LABELS.CODE')" />
            <Column field="name" :header="$t('FORM.LABELS.NAME')" />
            <Column field="actions" :header="$t('Actions')" style="width: 80px">
                <template #body="{ data }">
                    <EDUCATIONAL_MAJORAction :entity="data" action-id="${data.id}" />
                </template>
            </Column>
        </DataTable>
        <div>
            <b> {{ educationalMajor.length }} {{ $t('TREE.EDUCATIONAL_MAJOR') }} </b>
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
