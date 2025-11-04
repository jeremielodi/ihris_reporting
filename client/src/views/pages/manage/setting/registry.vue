<script>
import { defineComponent } from 'vue';
import SettingService from './setting.service';
import SettingAction from './actions.vue';
import { FilterMatchMode } from '@primevue/core/api';

export default defineComponent({
    name: 'SettingRegistry',
    data() {
        return {
            settings: [],
            selectedUser: null,
            loading: false,
            server: import.meta.env.VITE_SERVER_URL,
            filters1: { global: { value: null, matchMode: FilterMatchMode.CONTAINS } }
        };
    },
    created() {
        this.getSettings();
    },
    components: {
        SettingAction
    },
    methods: {
        getSettings() {
            this.loading = true;
            SettingService.read()
                .then((settings) => {
                    this.settings = settings;
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
            :value="settings"
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
                <h4>{{ $t('TREE.SETTING') }}</h4>
            </template>

            <Column selectionMode="single" style="width: 20px"></Column>
            <Column field="logo" :header="$t('FORM.LABELS.LOGO')">
                <template #body="{ data }">
                    <img height="100" :src="server + 'uploads/' + data.logo" />
                </template>
            </Column>
            <Column field="app_name" :header="$t('FORM.LABELS.APP_NAME')" />
            <Column field="app_version" :header="$t('FORM.LABELS.VERSION')" />
            <Column field="responsible_name" :header="$t('FORM.LABELS.RESPONSIBLE_NAME')" />
            <Column field="responsible_number" :header="$t('FORM.LABELS.RESPONSIBLE_NUMBER')" />
            <Column field="actions" :header="$t('Actions')" style="width: 80px">
                <template #body="{ data }">
                    <SettingAction :entity="data" action-id="${data.id}" />
                </template>
            </Column>
        </DataTable>
        <div>
            <b> {{ settings.length }} {{ $t('TREE.SETTING') }} </b>
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
