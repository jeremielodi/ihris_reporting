<script>
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import { defineComponent } from 'vue';
import DegreeService from './degreeService';
import DegreeAction from './actions.vue';
import { FilterMatchMode } from '@primevue/core/api';

export default defineComponent({
    name: 'DegreeRegistry',
    data() {
        return {
            degrees: [],
            selectedUser: null,
            loading: false,
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
        this.getDegrees();
    },
    components: {
        DegreeAction
    },
    methods: {
        gotoAdd() {
            this.$router.push('/manage/degree_create');
        },

        // 🔥 Get filtered or full data
        getExportData() {
            const data = this.degrees;

            return data.map((d) => ({
                id: d.id,
                name: d.name
            }));
        },
        getDegrees() {
            this.loading = true;
            DegreeService.read()
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
        onRowSelect(event) {
            console.log('Row selected:', event.value);
            this.selectedUser = event.value;
        },
        onFilter(event) {
            this.filters = event.filters;
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

            saveAs(blob, 'degrees.csv');
        },

        // =========================
        // EXPORT EXCEL
        // =========================
        exportExcel() {
            const data = this.getExportData();

            const worksheet = XLSX.utils.json_to_sheet(data);
            const workbook = XLSX.utils.book_new();

            XLSX.utils.book_append_sheet(workbook, worksheet, 'Degrees');

            const excelBuffer = XLSX.write(workbook, {
                bookType: 'xlsx',
                type: 'array'
            });

            const blob = new Blob([excelBuffer], {
                type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8'
            });

            saveAs(blob, 'degrees.xlsx');
        }
    }
});
</script>

<template>
    <div class="card manage-container" style="height: 90vh">
        <DataTable
            :value="degrees"
            :filter-display="'row'"
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
                <h4>{{ $t('TREE.DEGREE') }}</h4>
                <div class="flex justify-content-between flex-column sm:flex-row">
                    <span></span>

                    <span>
                        <InputGroup>
                            <InputGroupAddon>
                                <i class="pi pi-search"></i>
                            </InputGroupAddon>
                            <InputText v-model="filters1['global'].value" placeholder="Search" />
                            <Button :label="$t('FORM.BUTTONS.ADD')" @click="gotoAdd()" icon="pi pi-plus" />
                            <SplitButton label="Export" icon="pi pi-download" severity="info" :model="exportOptions" />
                        </InputGroup>
                    </span>
                </div>
            </template>

            <Column selectionMode="single" style="width: 20px"></Column>

            <Column field="name" :header="$t('FORM.LABELS.NAME')" />
            <Column field="actions" :header="$t('Actions')" style="width: 80px">
                <template #body="{ data }">
                    <DegreeAction :entity="data" action-id="degreeAction" />
                </template>
            </Column>
        </DataTable>
        <div>
            <b> {{ degrees.length }} {{ $t('TREE.DEGREE') }} </b>
        </div>
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
