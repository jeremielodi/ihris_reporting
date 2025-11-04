<script>
import { defineComponent } from 'vue';
import Person_TimesheetService from './person_timesheet.service';
import Person_TimesheetAction from './actions.vue';
import { FilterMatchMode } from '@primevue/core/api';

export default defineComponent({
    name: 'Person_TimesheetRegistry',
    data() {
        return {
            person_timesheets: [],
            selectedUser: null,
            loading: false,
            filters1: { global: { value: null, matchMode: FilterMatchMode.CONTAINS } }
        };
    },
    created() {
        this.getPerson_Timesheets();
    },
    components: {
        Person_TimesheetAction
    },
    methods: {
        getPerson_Timesheets() {
            this.loading = true;
            Person_TimesheetService.read()
                .then((person_timesheets) => {
                    this.person_timesheets = person_timesheets;
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
            :value="person_timesheets"
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
                <h4>{{ $t('TREE.PERSON_TIMESHEET') }}</h4>
                <div class="flex justify-content-between flex-column sm:flex-row">
                    <span></span>

                    <span>
                        <InputGroup>
                            <InputGroupAddon>
                                <i class="pi pi-search"></i>
                            </InputGroupAddon>
                            <InputText v-model="filters1['global'].value" placeholder="Search" />
                            <Button :label="$t('FORM.BUTTONS.ADD')" @click="this.$router.push('/manage/person_timesheet_create')" icon="pi pi-plus" />
                        </InputGroup>
                    </span>
                </div>
            </template>

            <Column selectionMode="single" style="width: 20px"></Column>
            <Column field="id" :header="$t('FORM.LABELS.ID')" />
            <Column field="parent" :header="$t('FORM.LABELS.PARENT')" />
            <Column field="last_modified" :header="$t('FORM.LABELS.LAST_MODIFIED')" />
            <Column field="created" :header="$t('FORM.LABELS.CREATED')" />
            <Column field="days_absence_justified" :header="$t('FORM.LABELS.DAYS_ABSENCE_JUSTIFIED')" />
            <Column field="days_absence_unjustified" :header="$t('FORM.LABELS.DAYS_ABSENCE_UNJUSTIFIED')" />
            <Column field="days_leave" :header="$t('FORM.LABELS.DAYS_LEAVE')" />
            <Column field="days_holiday" :header="$t('FORM.LABELS.DAYS_HOLIDAY')" />
            <Column field="days_sick" :header="$t('FORM.LABELS.DAYS_SICK')" />
            <Column field="days_mission" :header="$t('FORM.LABELS.DAYS_MISSION')" />
            <Column field="days_worked" :header="$t('FORM.LABELS.DAYS_WORKED')" />
            <Column field="days_planned" :header="$t('FORM.LABELS.DAYS_PLANNED')" />
            <Column field="month_year" :header="$t('FORM.LABELS.MONTH_YEAR')" />
            <Column field="bonus_local" :header="$t('FORM.LABELS.BONUS_LOCAL')" />
            <Column field="bonus_pepfar" :header="$t('FORM.LABELS.BONUS_PEPFAR')" />
            <Column field="bonus_partner" :header="$t('FORM.LABELS.BONUS_PARTNER')" />
            <Column field="bonus_risk" :header="$t('FORM.LABELS.BONUS_RISK')" />
            <Column field="project" :header="$t('FORM.LABELS.PROJECT')" />
            <Column field="salary_received" :header="$t('FORM.LABELS.SALARY_RECEIVED')" />
            <Column field="actions" :header="$t('Actions')" style="width: 80px">
                <template #body="{ data }">
                    <Person_TimesheetAction :entity="data" action-id="${data.id}" />
                </template>
            </Column>
        </DataTable>
        <div>
            <b> {{ person_timesheets.length }} {{ $t('TREE.PERSON_TIMESHEET') }} </b>
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
