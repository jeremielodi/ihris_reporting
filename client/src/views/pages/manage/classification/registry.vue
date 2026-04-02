<script>
import { defineComponent } from 'vue';
import ClassificationService from './classification.service';
import ClassificationAction from './actions.vue';
import { FilterMatchMode } from '@primevue/core/api';
import ImportModal from './import_modal.vue';
import NotifyService from '@/service/Notify.service';

// ✅ Export libs
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';

export default defineComponent({
    name: 'DegreeRegistry',
    data() {
        return {
            classifications: [],
            selectedUser: null,
            loading: false,
            displayImportModal: false,
            exportOptions: [
                {
                    label: 'Export Excel',
                    icon: 'pi pi-file-excel',
                    command: () => this.exportExcel()
                },
                {
                    label: 'Export CSV',
                    icon: 'pi pi-file',
                    command: () => this.exportCSV()
                }
            ],
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
                .then((classifications) => {
                    this.classifications = classifications;
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
                    .then(() => {
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
         // =========================
        // EXPORT CSV
        // =========================
        exportCSV() {
            const data = this.getExportData();

            const worksheet = XLSX.utils.json_to_sheet(data);
            const csv = XLSX.utils.sheet_to_csv(worksheet);

            const blob = new Blob([csv], {
                type: 'text/csv;charset=utf-8;'
            });

            saveAs(blob, 'classifications.csv');
        },

        // =========================
        // EXPORT HELPERS
        // =========================
        getExportData() {
            const data = this.classifications;

            return data.map((c) => ({
                id: c.id,
                name: c.name,
                code: c.code || '',
                description: c.description || ''
            }));
        },
        // =========================
        // EXPORT EXCEL
        // =========================
        exportExcel() {
            const data = this.getExportData();

            const worksheet = XLSX.utils.json_to_sheet(data);
            const workbook = XLSX.utils.book_new();

            XLSX.utils.book_append_sheet(workbook, worksheet, 'Classifications');

            const excelBuffer = XLSX.write(workbook, {
                bookType: 'xlsx',
                type: 'array'
            });

            const blob = new Blob([excelBuffer], {
                type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8'
            });

            saveAs(blob, 'classifications.xlsx');
        }
    }
});
</script>

<template>
    <div class="card manage-container" style="height: 90vh">
        <DataTable
            :value="classifications"
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
                            <Button data-testid="addButton" :label="$t('FORM.BUTTONS.ADD')" @click="this.$router.push('/manage/classification_create')" icon="pi pi-plus" />
                            <Button data-testid="importButton" :label="$t('FORM.BUTTONS.IMPORT')" severity="secondary" @click="openImportModal()" icon="pi pi-upload" />
                            <SplitButton
                                label="Export"
                                icon="pi pi-download"
                                :model="exportOptions"
                                @click="exportExcel"
                                class="p-button-outlined"
                                severity="info"
                            />

                        </InputGroup>
                    </span>
                </div>
            </template>

            <Column selectionMode="single" style="width: 20px" />

            <Column field="name" :header="$t('FORM.LABELS.NAME')" />

            <Column field="code" :header="$t('FORM.LABELS.CODE')" />
            <Column field="description" :header="$t('FORM.LABELS.DESCRIPTION')" />
            <Column field="actions" :header="$t('Actions')" style="width: 80px">
                <template #body="{ data, index }">
                    <ClassificationAction :entity="data" :action-id="'classifAction' + (index + 1)" />
                </template>
            </Column>
        </DataTable>
        <div>
            <b>{{ classifications.length }} {{ $t('TREE.CLASSIFICATIONS') }} </b>
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
