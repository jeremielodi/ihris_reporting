<script>
import { defineComponent } from 'vue';
import NotifyService from '@/service/Notify.service';
import ConfirmModal from '@/components/ConfirmModal.vue';
import employee_statusService from './employee_status.service';

export default defineComponent({
    name: 'employee_statusAction',
    props: {
        entity: Object,
        actionId: String
    },
    data() {
        return {
            items: [],
            display: false,
            displayConfirm: false,
        };
    },
    emits: ['reloademployee_statusList'],
    methods: {
        toggle(event) {
            this.$refs.menu.toggle(event);
            this.setItems();
        },

        closeDialog(result) {
            if (result) {
                this.$emit('reloademployee_statusList', true);
            }
            this.display = false;
            this.displayConfirm = false;
        },

        HideModal() {
            this.display = false;
            this.displayConfirm = false;
        },

        DeleteConfirmDialog(result) {
            if (!result) {
                this.HideModal();
                return;
            }
            // Supprimer le statut
            this.displayConfirm = true;
            employee_statusService.delete(this.entity.id)
                .then(() => {
                    NotifyService.success(this, 'EMPLOYEE_STATUS.DELETE_SUCCESS', null);
                    this.$emit('reloademployee_statusList', true);
                    this.HideModal();
                })
                .catch((error) => {
                    console.error('Delete error:', error);
                    NotifyService.danger(this, 'EMPLOYEE_STATUS.DELETE_ERROR', null);
                })
                .finally(() => {
                    this.displayConfirm = false;
                });
        },

        setItems() {
            this.items = [
                {
                    label: this.entity.name || this.entity.id,
                    items: [
                        {
                            label: this.$t('FORM.BUTTONS.EDIT'),
                            icon: 'pi pi-fw pi-pencil',
                            command: () => {
                                this.$router.push(`/manage/employee_status_create?id=${this.entity.id}`);
                            }
                        },
                        {
                            label: this.$t('FORM.BUTTONS.DELETE'),
                            icon: 'pi pi-fw pi-trash',
                            command: () => {
                                this.displayConfirm = true;
                            }
                        }
                    ]
                }
            ];
        }
    },
    components: {
        ConfirmModal
    }
});
</script>

<template>
    <div style="text-align: right" :data-testid="actionId" :id="actionId">
        <div @click="toggle" class="link">
            <span style="font-size: 14px">Actions</span>
            <i class="link pi pi-chevron-down" style="fontsize: 1rem"> </i>
        </div>
        <Menu ref="menu" :model="items" :popup="true" />
        <ConfirmModal 
            :entity="entity" 
            :close="DeleteConfirmDialog" 
            :display="displayConfirm"
            :message="$t('EMPLOYEE_STATUS.CONFIRM_DELETE', { name: entity.name || entity.id })"
        />
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