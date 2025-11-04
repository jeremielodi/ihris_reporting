
<script>
import { defineComponent } from 'vue';
import ContactService from './contact.service';
import ContactAction from './actions.vue';
import { FilterMatchMode } from '@primevue/core/api';

export default defineComponent({
    name: 'ContactRegistry',
    data() {
        return {
            contacts: [],
            selectedUser: null,
            loading: false,
            filters1: { global: { value: null, matchMode: FilterMatchMode.CONTAINS } }
        };
    },
    created() {
        this.getContacts();
    },
    components: {
        ContactAction
    },
    methods: {
        getContacts() {
            this.loading = true;
            ContactService.read()
                .then((contacts) => {
                    this.contacts = contacts;
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
            :value="contacts"
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
                <h4>{{ $t('TREE.CONTACT') }}</h4>
                <div class="flex justify-content-between flex-column sm:flex-row">
                    <span></span>

                    <span>
                        <InputGroup>
                            <InputGroupAddon>
                                <i class="pi pi-search"></i>
                            </InputGroupAddon>
                            <InputText v-model="filters1['global'].value" placeholder="Search" /> 
                            <Button :label="$t('FORM.BUTTONS.ADD')" @click="this.$router.push('/manage/contact_create')" icon="pi pi-plus"/>
                           </InputGroup>
                    </span>
                </div>
            </template>

            <Column selectionMode="single" style="width: 20px"></Column><Column field="name" :header="$t('FORM.LABELS.NAME')" /> 
<Column field="address" :header="$t('FORM.LABELS.ADDRESS')" /> 
<Column field="mobile_phone" :header="$t('FORM.LABELS.MOBILE_PHONE')" /> 
<Column field="telephone" :header="$t('FORM.LABELS.PHONE')" /> 
<Column field="alt_telephone" :header="$t('FORM.LABELS.ALT_PHONE')" /> 
<Column field="email" :header="$t('FORM.LABELS.EMAIL')" /> 
<Column field="fax" :header="$t('FORM.LABELS.FAX')" /> 
<Column field="notes" :header="$t('FORM.LABELS.NOTES')" /> 
<Column field="actions" :header="$t('Actions')" style="width: 80px;">
                <template #body="{ data }">
                    <ContactAction :entity="data" action-id="${data.id}" />
                </template>
            </Column>
        </DataTable>
        <div>
            <b> {{ contacts.length }} {{ $t('TREE.CONTACT') }} </b>
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


