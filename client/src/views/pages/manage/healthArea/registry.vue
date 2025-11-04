
<script>
import { defineComponent } from 'vue';
import HealthAreaService from './healtharea.service';
import HealthAreaAction from './actions.vue';
import { FilterMatchMode } from '@primevue/core/api';

export default defineComponent({
    name: 'HealthAreaRegistry',
    data() {
        return {
            healthareas: [],
            selectedUser: null,
            loading: false,
            filters1: { global: { value: null, matchMode: FilterMatchMode.CONTAINS } }
        };
    },
    created() {
        this.getHealthAreas();
    },
    components: {
        HealthAreaAction
    },
    methods: {
        getHealthAreas() {
            this.loading = true;
            HealthAreaService.read()
                .then((healthareas) => {
                    this.healthareas = healthareas;
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
            :value="healthareas"
            v-model:selection="selectedUser"
            paginator 
            :rows="100"
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
                <h4>{{ $t('TREE.HEALTH_AREA') }}</h4>
                <div class="flex justify-content-between flex-column sm:flex-row">
                    <span></span>

                    <span>
                        <InputGroup>
                            <InputGroupAddon>
                                <i class="pi pi-search"></i>
                            </InputGroupAddon>
                            <InputText v-model="filters1['global'].value" placeholder="Search" /> 
                            <Button :label="$t('FORM.BUTTONS.ADD')" @click="this.$router.push('/manage/health_area_create')" icon="pi pi-plus"/>
                           </InputGroup>
                    </span>
                </div>
            </template>

            <Column selectionMode="single" style="width: 20px"></Column>
            <Column field="county_name" :header="$t('TREE.COUNTY')" />
            <Column field="name" :header="$t('FORM.LABELS.NAME')" />
            <Column field="code" :header="$t('FORM.LABELS.CODE')" />
            <Column field="actions" :header="$t('Actions')" style="width: 80px;">
                <template #body="{ data }">
                    <HealthAreaAction :entity="data" action-id="${data.id}" />
                </template>
            </Column>
        </DataTable>
        <div>
            <b> {{ healthareas.length }} {{ $t('TREE.HEALTH_AREA') }} </b>
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


