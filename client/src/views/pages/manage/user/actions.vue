<script>
import { defineComponent } from 'vue';
import NotifyService from '@/service/Notify.service';
import ConfirmModal from '@/components/ConfirmModal.vue';
import UserRoleModal from "../role/user.roles.vue";
import UserService from './user.service';
export default defineComponent({
    name: 'UserAction',
    props: {
        entity: Object,
        actionId: String
    },
    data() {
        return {
            items: [],
            display: false,
            displayConfirm: false,
            displayUserRoleMoal: false
        };
    },
    emits: ['reloadServiceList'],
    setup() {},
    methods: {
        toggle(event) {
            this.$refs.menu.toggle(event);
            this.setItems();
        },

        closeDialog(result) {
            if (result) {
                this.$emit('reloadServiceList', true);
            }
            this.display = false;
            this.displayConfirm = false;
            this.displayUserRoleMoal = false;
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

            UserService.delete(this.entity.id)
                .then(() => {
                    NotifyService.success(this, '', null);
                    this.$emit('reloadServiceList', true);
                    this.HideModal();
                })
                .catch(() => {
                    NotifyService.danger(this, '', null);
                });
        },

        setItems() {
            this.items = [
                {
                    label: this.entity.lastname,
                    items: [
                        {
                            label: this.$t('FORM.BUTTONS.EDIT'),
                            icon: 'pi pi-fw pi-pencil',
                            command: () => {
                                this.$router.push(`/manage/user_create?id=${this.entity.id}`);
                            }
                        },
                        {
                        label: this.$t("FORM.LABELS.ROLE"),
                        icon: "pi pi-cog",
                        command: () => {
                            this.displayUserRoleMoal = true;
                        },
                        },
                    ]
                }
            ];
        }
    },
    components: {
        ConfirmModal,
        UserRoleModal
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
        <ConfirmModal :user="entity" :close="DeleteConfirmDialog" :display="displayConfirm"> </ConfirmModal>
        <UserRoleModal
            :user="entity"
            ref="userRoleModal"
            :close='closeDialog'
            :display="displayUserRoleMoal">
        </UserRoleModal>
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
