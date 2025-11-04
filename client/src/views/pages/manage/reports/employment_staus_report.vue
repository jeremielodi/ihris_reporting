<script>
import { defineComponent } from 'vue';
import ReportService from './reports.service';
import { FilterMatchMode } from '@primevue/core/api';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'MangeHome',
    data() {
        return {
            loading: false,
            selectedRow: null,
            dataList: [],
            headers: [],
            filters1: { global: { value: null, matchMode: FilterMatchMode.CONTAINS } }
        };
    },
    created() {
        console.log('Manage Home Component Created');
        this.getEmploymentStatusData();
    },
    methods: {
        generate() {
            ReportService.generateEmploymentStatus()
                .then(() => {
                    NotifyService.success(this, '', null);
                    this.getEmploymentStatusData();
                })
                .catch(() => {
                    NotifyService.danger(this, '', null);
                });
        },
        getEmploymentStatusData() {
            if (this.loading) return;
            this.loading = true;
            ReportService.employmentStatus()
                .then((result) => {
                    this.dataList = result;
                    this.headers = Object.keys(this.dataList[0] || {});
                })
                .catch((ex) => {
                    console.log(ex);
                    NotifyService.danger(this, '', null);
                })
                .finally(() => {
                    this.loading = false;
                });
        }
    }
});
</script>
<template>
    <div class="card manage-container" style="height: 90vh">
        <DataTable
            :value="dataList"
            v-model:selection="selectedRow"
            dataKey="id"
            showGridlines
            paginator
            :rows="100"
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
                <h4>{{ $t('TREE.EMPLOYEE_STATUS_REPORT') }}</h4>
                <div class="flex justify-content-between flex-column sm:flex-row">
                    <span></span>

                    <span>
                        <InputGroup>
                            <InputGroupAddon>
                                <i class="pi pi-search"></i>
                            </InputGroupAddon>
                            <InputText v-model="filters1['global'].value" placeholder="Search" />
                            <Button :label="$t('FORM.BUTTONS.GENERATE')" @click="generate()" icon="pi pi-plus" />
                        </InputGroup>
                    </span>
                </div>
            </template>
            <Column selectionMode="single" style="width: 20px"></Column>
            <template v-for="value in headers" :key="value">
                <Column :field="value" :header="value" />
            </template>
        </DataTable>
    </div>
</template>
