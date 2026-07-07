<script>
import { defineComponent } from 'vue';
import employee_statusService from './employee_status.service';
import employee_statusAction from './actions.vue';
import { FilterMatchMode } from '@primevue/core/api';

export default defineComponent({
    name: 'employee_statusRegistry',
    data() {
        return {
            employee_status: [],
            selectedStatus: null,
            loading: false,
            filters1: {
                global: {
                    value: null,
                    matchMode: FilterMatchMode.CONTAINS
                }
            }
        };
    },
    created() {
        this.getemployee_status();
    },
    components: {
        employee_statusAction
    },
    methods: {
        getemployee_status() {
            this.loading = true;
            employee_statusService.read()
                .then((employee_status) => {
                    this.employee_status = employee_status;
                })
                .catch((error) => {
                    console.error('Error fetching employee status data:', error);
                    // NotifyService.danger(this, 'EMPLOYEE_STATUS.LOAD_ERROR', null);
                })
                .finally(() => {
                    this.loading = false;
                });
        },

        reloademployee_statusList() {
            this.getemployee_status();
        },

        onRowSelect(event) {
            console.log('Row selected:', event.value);
            this.selectedStatus = event.value;
        },

        onFilter(event) {
            this.filters = event.filters;
        }
    }
});
</script>

<template>
    <div class="card manage-container" style="height: 90vh">
        <DataTable :value="employee_status" v-model:selection="selectedStatus" dataKey="id" showGridlines stripedRows
            resizableColumns columnResizeMode="fit" scrollable scrollHeight="flex" responsiveLayout="scroll"
            :filters="filters1" selectionMode="single" :loading="loading">
            <template #header>
                <h4>{{ $t('TREE.EMPLOYEE_STATUS') }}</h4>
                <div class="flex justify-content-between flex-column sm:flex-row">
                    <span></span>
                    <span>
                        <InputGroup>
                            <InputGroupAddon>
                                <i class="pi pi-search"></i>
                            </InputGroupAddon>
                            <InputText v-model="filters1['global'].value" :placeholder="$t('FORM.LABELS.SEARCH')" />
                            <Button :label="$t('FORM.BUTTONS.ADD')"
                                @click="this.$router.push('/manage/employee_status_create')" icon="pi pi-plus" />
                        </InputGroup>
                    </span>
                </div>
            </template>

            <Column selectionMode="single" style="width: 20px"></Column>
            <Column field="name" :header="$t('FORM.LABELS.NAME')" style="min-width: 150px" />
            <Column field="i2ce_hidden" :header="$t('FORM.LABELS.LOCKED')" style="width: 80px">
                <template #body="{ data }">
                    <i v-if="data.i2ce_hidden" class="pi pi-lock" style="color: #f44336"></i>
                    <i v-else class="pi pi-lock-open" style="color: #4caf50"></i>
                </template>
            </Column>
            <Column field="actions" :header="$t('FORM.BUTTONS.ACTIONS')" style="width: 100px">
                <template #body="{ data }">
                    <employee_statusAction :entity="data" action-id="'action-' + data.id"
                        @reloademployee_statusList="reloademployee_statusList" />
                </template>
            </Column>
        </DataTable>
        <div>
            <b>{{ employee_status.length }} {{ $t('TREE.employee_STATUS') }}</b>
        </div>
    </div>
</template>

<style scoped>
.p-datatable.p-datatable-gridlines .p-datatable-tbody>tr>td {
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