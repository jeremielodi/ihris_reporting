<script>
import { defineComponent } from 'vue';
import UserService from './user.service';
import UserAction from './actions.vue';
import { FilterMatchMode } from '@primevue/core/api';
export default defineComponent({
    name: 'UserRegistry',
    data() {
        return {
            users: [],
            selectedUser: null,
            loading: false,
            filters1: { global: { value: null, matchMode: FilterMatchMode.CONTAINS } }
        };
    },
    created() {
        console.log('UserRegistry Component Created');
        this.getUsers();
    },
    methods: {
        getUsers() {
            this.loading = true;
            UserService.read()
                .then((users) => {
                    this.users = users;
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
    },
    components: {
        UserAction
    }
});
</script>

<template>
    <div class="card manage-container" style="height: 90vh">
        <DataTable
            :value="users"
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
                <h4>{{ $t('TREE.USER_REGISTRY') }}</h4>
                <div class="flex justify-content-between flex-column sm:flex-row">
                    <span></span>

                    <span>
                        <InputGroup>
                            <InputGroupAddon>
                                <i class="pi pi-search"></i>
                            </InputGroupAddon>
                            <InputText v-model="filters1['global'].value" placeholder="Search" /> 
                            <Button :label="$t('FORM.BUTTONS.ADD')" @click="this.$router.push('/manage/user_create')" icon="pi pi-plus"/>
                           </InputGroup>
                    </span>
                </div>
            </template>

            <Column selectionMode="single" style="max-width: 40px"></Column>

            <Column field="firstname" :header="$t('FORM.LABELS.FIRSTNAME')" style="max-width: 120px" filter filterPlaceholder="Search by firstname">
                <template #body="{ data }">
                    {{ data.firstname }}
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText type="text" v-model="filterModel.value" @input="filterCallback" class="p-column-filter" :placeholder="`Search by firstname - ${filterModel.matchMode}`" />
                </template>
            </Column>

            <Column field="lastname" :header="$t('FORM.LABELS.LASTNAME')" style="max-width: 120px" filter filterPlaceholder="Search by firstname">
                <template #body="{ data }">
                    {{ data.lastname }}
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText type="text" v-model="filterModel.value" @input="filterCallback" class="p-column-filter" :placeholder="`Search by firstname - ${filterModel.matchMode}`" />
                </template>
            </Column>
            <Column field="email" :header="$t('FORM.LABELS.EMAIL')" filter filterPlaceholder="Search by email">
                <template #body="{ data }">
                    {{ data.email }}
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText type="text" v-model="filterModel.value" @input="filterCallback" class="p-column-filter" :placeholder="`Search by email - ${filterModel.matchMode}`" />
                </template>
            </Column>

            <Column field="username" :header="$t('FORM.LABELS.USERNAME')" filterPlaceholder="Search by name">
                <template #body="{ data }">
                    {{ data.username }}
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText type="text" v-model="filterModel.value" @input="filterCallback" class="p-column-filter" :placeholder="`Search by name - ${filterModel.matchMode}`" />
                </template>
            </Column>

            <Column field="i2ce_hidden" style="width: 120px" :header="$t('FORM.LABELS.LOCKED')">
                <template #body="e">
                    <span>
                        {{ $t(e.data.i2ce_hidden ? 'FORM.LABELS.YES' : 'FORM.LABELS.NO') }}
                    </span>
                </template>
            </Column>

            <Column field="actions" :header="$t('Actions')" style="width: 80px">
                <template #body="{ data }">
                    <UserAction :entity="data" action-id="userAction" />
                </template>
            </Column>
        </DataTable>
        <div>
            <b> {{ users.length }} {{ $t('TREE.USERS') }} </b>
        </div>
    </div>
</template>
<style scoped></style>
