
<script>
import { defineComponent } from 'vue';
import Institution_typeService from './institution_type.service';
import Institution_typeAction from './actions.vue';
import { FilterMatchMode } from '@primevue/core/api';

export default defineComponent({
    name: 'Institution_typeRegistry',
    data() {
        return {
            institution_types: [],
            selectedUser: null,
            loading: false,
            filters1: { global: { value: null, matchMode: FilterMatchMode.CONTAINS } }
        };
    },
    created() {
        this.getInstitution_types();
    },
    components: {
        Institution_typeAction
    },
    methods: {
        getInstitution_types() {
            this.loading = true;
            Institution_typeService.read()
                .then((institution_types) => {
                    this.institution_types = institution_types;
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
            :value="institution_types"
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
                <h4>{{ $t('TREE.INSTITUTION_TYPE') }}</h4>
                <div class="flex justify-content-between flex-column sm:flex-row">
                    <span></span>

                    <span>
                        <InputGroup>
                            <InputGroupAddon>
                                <i class="pi pi-search"></i>
                            </InputGroupAddon>
                            <InputText v-model="filters1['global'].value" placeholder="Search" /> 
                            <Button :label="$t('FORM.BUTTONS.ADD')" @click="this.$router.push('/manage/institution_type_create')" icon="pi pi-plus"/>
                           </InputGroup>
                    </span>
                </div>
            </template>

            <Column selectionMode="single" style="width: 20px"></Column>
            <Column field="code" :header="$t('FORM.LABELS.CODE')" /> 
            <Column field="name" :header="$t('FORM.LABELS.NAME')" /> 
            <Column field="actions" :header="$t('Actions')" style="width: 80px;">
                <template #body="{ data }">
                    <Institution_typeAction :entity="data" action-id="${data.id}" />
                </template>
            </Column>
        </DataTable>
        <div>
            <b> {{ institution_types.length }} {{ $t('TREE.INSTITUTION_TYPE') }} </b>
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


