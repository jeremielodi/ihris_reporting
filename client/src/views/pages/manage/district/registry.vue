
<script>
import { defineComponent } from 'vue';
import DistrictService from './district.service';
import DistrictAction from './actions.vue';
import { FilterMatchMode } from '@primevue/core/api';

export default defineComponent({
    name: 'DistrictRegistry',
    data() {
        return {
            districts: [],
            selectedUser: null,
            loading: false,
            filters1: { global: { value: null, matchMode: FilterMatchMode.CONTAINS } }
        };
    },
    created() {
        console.log('UserRegistry Component Created');
        this.getDistricts();
    },
    components: {
        DistrictAction
    },
    methods: {
        getDistricts() {
            this.loading = true;
            DistrictService.read()
                .then((districts) => {
                    this.districts = districts;
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
            :value="districts"
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
                <h4>{{ $t('TREE.DISTRICT') }}</h4>
                <div class="flex justify-content-between flex-column sm:flex-row">
                    <span></span>

                    <span>
                        <InputGroup>
                            <InputGroupAddon>
                                <i class="pi pi-search"></i>
                            </InputGroupAddon>
                            <InputText v-model="filters1['global'].value" placeholder="Search" /> 
                            <Button :label="$t('FORM.BUTTONS.ADD')" @click="this.$router.push('/manage/district_create')" icon="pi pi-plus"/>
                           </InputGroup>
                    </span>
                </div>
            </template>

            <Column selectionMode="single" style="width: 20px"></Column>
            <Column field="name" :header="$t('FORM.LABELS.NAME')" /><Column field="code" :header="$t('FORM.LABELS.CODE')" />
            <Column field="region" :header="$t('TREE.REGION')" />
            <Column field="actions" :header="$t('Actions')" style="width: 80px;">
                <template #body="{ data }">
                    <DistrictAction :entity="data" action-id="${data.id}" />
                </template>
            </Column>
        </DataTable>
        <div>
            <b> {{ districts.length }} {{ $t('TREE.DISTRICT') }} </b>
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


