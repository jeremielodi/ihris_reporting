<script>
import { defineComponent } from 'vue';
import PeopleService from './people.service';
import { FilterMatchMode } from '@primevue/core/api';
import RoleService from '../role/roleService';
import constants from '../../../../service/constants';

export default defineComponent({
    name: 'Payment_frequencyRegistry',
    data() {
        return {
            payment_frequencys: [],
            selectedUser: null,
            canEditPerson: false,
            loading: false,
            searchText: '',
            filters1: { global: { value: null, matchMode: FilterMatchMode.CONTAINS } }
        };
    },
    created() {
        this.loadPeopleList();
        this.init();

    },
    methods: {
        async init() {
            this.canEditPerson = await this.checkPermission(constants.ACTIONS.CAN_EDIT_PERSON);
        },
        checkPermission(id) {
            return RoleService.userHasAction(id);
        },
        searchPeople() {
            console.log('change');
            if (this.loading) return;
            if (this.searchText.length == 0) {
                return this.loadPeopleList();
            }
            if (this.searchText.length < 3) return;
            this.loading = true;
            PeopleService.read(null, { name: this.searchText })
                .then((payment_frequencys) => {
                    this.payment_frequencys = payment_frequencys;
                })
                .catch((error) => {
                    console.error('Error fetching user data:', error);
                })
                .finally(() => {
                    this.loading = false;
                });
        },
        gotoView(id) {
            this.$router.push(`/manage/people_record_view?id=${id}`);
        },
        loadPeopleList() {
            this.loading = true;
            PeopleService.read()
                .then((payment_frequencys) => {
                    this.payment_frequencys = payment_frequencys;
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
            :value="payment_frequencys"
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
                <h4>{{ $t('TREE.PEOPLE_LIST') }}</h4>
                <div class="flex justify-content-between flex-column sm:flex-row">
                    <span></span>

                    <span>
                        <InputGroup>
                            <InputGroupAddon>
                                <i class="pi pi-search"></i>
                            </InputGroupAddon>
                            <InputText v-model="searchText" @update:modelValue="searchPeople()" placeholder="Search" />
                            <Button v-if="canEditPerson" :label="$t('FORM.BUTTONS.ADD')" @click="this.$router.push('/manage/people_create')" icon="pi pi-plus" />
                        </InputGroup>
                    </span>
                </div>
            </template>

            <Column selectionMode="single" style="width: 20px"></Column>
            <Column field="eye" header="#">
                <template #body="{ data }">
                    <i @click="gotoView(data.id)" class="pi pi-eye" style="font-size: 1.4rem"></i>
                </template>
            </Column>
            <Column field="lastname" :header="$t('FORM.LABELS.LASTNAME')" />
            <Column field="middlename" :header="$t('FORM.LABELS.MIDDLE_NAME')" />
            <Column field="firstname" :header="$t('FORM.LABELS.FIRST_NAME')" />
            <Column field="birthdate" :header="$t('FORM.LABELS.DOB')" />
            <Column field="gender" :header="$t('FORM.LABELS.SEX')" />
            <Column field="marital_status" :header="$t('ETAT CIVIL')" />
            <Column field="nationality" :header="$t('FORM.LABELS.NATIONALTY')" />
        </DataTable>
        <div>
            <b> {{ payment_frequencys.length }} {{ $t('FORM.LABELS.AGENT') + 's' }} </b>
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
