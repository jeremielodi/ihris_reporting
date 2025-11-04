<script>
import RoleService from './roleService';
import roleActions from './actions.vue';
import CreateUpdateModal from './createUpdateModal.vue';


export default {
    data() {
        return {
            roles: [],
            role: {},
            items: [],
            selectedRole: null,
            displayCreateModal: false
        };
    },
    created() {
        this.getRoles();
    },
    methods: {
        getRoles() {
            RoleService.read().then((roles) => {
                this.roles = roles;
            });
        },
        onRowSelect($event) {
            console.log($event.data);
        },
        Add() {
            this.displayCreateModal = true;
            this.role = {};
        },
        closeDialog(result) {
            if (result) {
                this.getRoles();
            }
            this.displayCreateModal = false;
        },

        toggleAction(event) {
            this.$refs.cm.show(event.originalEvent);
            this.items = [
                {
                    label: 'delete',
                    icon: 'pi pi-check',
                    command: () => {}
                }
            ];
        }
    },
    components: {
        roleActions,
        CreateUpdateModal
    }
};
</script>

<template>
    <div class="card manage-container" style="height: 90vh">
        <div style="float: right; width: 300px">
            <span class="p-buttonset">
                <Button style="float: right" v-on:click="Add()" :label="$t('FORM.BUTTONS.ADD')" icon="pi pi-plus" />
            </span>
        </div>
        <br />
        <br />
        <br />

        <DataTable @rowSelect="onRowSelect" :value="roles" showGridlines stripedRows v-model:selection="selectedRole" dataKey="uuid" responsiveLayout="scroll">
            <template #header>
                {{ $t('TREE.ROLE') }}
            </template>

            <template #empty>
                {{ $t('FORM.SELECT.EMPTY') }}
            </template>

            <Column selectionMode="single" headerStyle="width: 3em"></Column>

            <Column field="name" :header="$t('FORM.LABELS.LABEL')"></Column>
            <Column field="is_default" headerStyle="width: 16em" :header="$t('FORM.LABELS.DEFAULT_ROLE')">
                <template #body="e">
                    <span>{{ e.data.is_default ? $t('FORM.LABELS.YES') : $t('FORM.LABELS.NO') }}</span>
                </template>
            </Column>

            <Column field="action" header="Action" style="width: 100px">
                <template #body="e">
                    <roleActions :entity="e.data" v-on:reloadRoleList="getRoles()" />
                </template>
            </Column>
        </DataTable>

        <CreateUpdateModal :role="role" ref="addroleModal" :close="closeDialog" :display="displayCreateModal"> </CreateUpdateModal>
    </div>
</template>
