<script>
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import { defineComponent } from 'vue';
import SpecialityService from './specialityService';
import SpecialityAction from './actions.vue';
import { FilterMatchMode } from '@primevue/core/api';

export default defineComponent({
    name: 'SpecialityRegistry',
    data() {
        return {
            specialities: [],
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
        console.log('SpecialityRegistry Component Created');
        this.getSpecialities();
    },
    components: {
        SpecialityAction
    },
    methods: {
        gotoAdd() {
            this.$router.push('/manage/speciality_create');
        },

        // 🔥 Get filtered or full data
        getExportData() {
            const data = this.specialities;

            return data.map((d) => ({
                id: d.id,
                name: d.name
            }));
        },
        getSpecialities() {
            this.loading = true;
            SpecialityService.read()
                .then((specialities) => {
                    this.specialities = specialities;
                })
                .catch((error) => {
                    console.error('Error fetching speciality data:', error);
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

            saveAs(blob, 'specialities.csv');
        },

        // =========================
        // EXPORT EXCEL
        // =========================
        exportExcel() {
            const data = this.getExportData();

            const worksheet = XLSX.utils.json_to_sheet(data);
            const workbook = XLSX.utils.book_new();

            XLSX.utils.book_append_sheet(workbook, worksheet, 'Specialities');

            const excelBuffer = XLSX.write(workbook, {
                bookType: 'xlsx',
                type: 'array'
            });

            const blob = new Blob([excelBuffer], {
                type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8'
            });

            saveAs(blob, 'specialities.xlsx');
        }
    }
});
</script>

<template>
    <div class="card manage-container" style="height: 90vh">
        <DataTable
            :value="specialities"
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
                <h4>{{ $t('TREE.SPECIALITY') }}</h4>
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
             <Column field="code" :header="$t('FORM.LABELS.CODE')" />
            <Column field="name" :header="$t('FORM.LABELS.NAME')" />
            <Column field="actions" :header="$t('Actions')" style="width: 80px">
                <template #body="{ data }">
                    <SpecialityAction :entity="data" action-id="specialityAction" />
                </template>
            </Column>
        </DataTable>
        <div>
            <b> {{ specialities.length }} {{ $t('TREE.SPECIALITY') }} </b>
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