<script>
import { defineComponent } from 'vue';
import CreateUpdateModal from './createUpdateModal.vue';
import RolePageModal from './role.pages.vue';
import RoleActionsModal from './role.actions.vue';
import RoleDashbardModal from './role.dashboard.vue';
import ConfirmModal from '@/components/ConfirmModal.vue';
import RoleService from './roleService';

export default defineComponent({
    name: 'RoleAction',
    props: {
        entity: Object
    },
    data() {
        return {
            items: [],
            display: false,
            displayConfirm: false,
            displayRolePageModal: false,
            displayRoleActionsModal: false,
            displayDashboardModal: false,
        };
    },
    emits: ['reloadRoleList'],
    setup() {},
    methods: {
        toggle(event) {
            this.$refs.menu.toggle(event);
            this.setItems();
        },

        closeDialog(result) {
            if (result) {
                this.$emit('reloadRoleList', true);
            }
            this.HideModal();
        },
        closeDashbardDialog() {
            this.HideModal();
        },
        HideModal() {
            this.display = false;
            this.displayConfirm = false;
            this.displayRolePageModal = false;
            this.displayRoleActionsModal = false;
            this.displayDashboardModal = false;
        },

        DeleteConfirmDialog(result) {
            if (!result) {
                this.HideModal();
                return;
            }

            RoleService.delete(this.entity.id)
                .then(() => {
                    this.$emit('reloadRoleList', true);
                    this.HideModal();
                })
                .catch(() => {});
        },

        setItems() {
            this.items = [
                {
                    label: this.entity.name,
                    items: [
                        {
                            label: this.$t('FORM.BUTTONS.EDIT'),
                            icon: 'pi pi-fw pi-pencil',
                            command: () => {
                                this.display = true;
                            }
                        },
                        {
                            label: this.$t('FORM.BUTTONS.DELETE'),
                            icon: 'pi pi-fw pi-times',
                            style: 'color:red',
                            command: () => {
                                this.displayConfirm = true;
                            }
                        },
                        {
                            label: this.$t('FORM.LABELS.PAGE'),
                            icon: 'pi pi-file-o',
                            style: 'color:red',
                            command: () => {
                                this.displayRolePageModal = true;
                            }
                        },

                        {
                            label: this.$t('TREE.METABASE_DASHBOARD'),
                            icon: 'pi pi-chart-bar',
                            style: 'color:red',
                            command: () => {
                                this.displayDashboardModal = true;
                            }
                        },
                                       {
                            label: this.$t('FORM.BUTTONS.ACTIONS'),
                            icon: 'pi pi-file-o',
                            style: 'color:red',
                            command: () => {
                                this.displayRoleActionsModal = true;
                            }
                        }
                    ]
                }
            ];
        }
    },
    components: {
        CreateUpdateModal,
        ConfirmModal,
        RolePageModal,
        RoleActionsModal,
        RoleDashbardModal
    }
});
</script>

<template>
    <div style="text-align: right">
        <div @click="toggle" class="link">
            <span style="font-size: 14px">Actions</span>
            <i class="link pi pi-chevron-down" style="font-size: 0.8rem; line-height: 1px"> </i>
        </div>
        <Menu ref="menu" :model="items" :popup="true" />
        <CreateUpdateModal :role="entity" :close="closeDialog" :display="display"> </CreateUpdateModal>

        <RolePageModal :role="entity" :close="closeDialog" :display="displayRolePageModal"> </RolePageModal>

        <RoleActionsModal :role="entity" :close="closeDialog" :display="displayRoleActionsModal"> </RoleActionsModal>
        <RoleDashbardModal :role="entity" :close="closeDashbardDialog" :display="displayDashboardModal"></RoleDashbardModal>
        <ConfirmModal :user="entity" message="Suppression du message" :close="DeleteConfirmDialog" :display="displayConfirm"> </ConfirmModal>
    </div>
</template>

<style>
select {
    width: 150px;
    line-height: 49px;
    height: 38px;
    font-size: 22px;
    outline: 0;
    margin-bottom: 15px;
}
.link {
    cursor: pointer;
}
</style>
