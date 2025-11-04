<script>
import { defineComponent } from 'vue';

import RoleService from './roleService';
import userService from '../user/user.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'UserRoleModal',
    props: {
        user: Object,
        close: Function,
        display: {
            type: Boolean,
            default: false
        }
    },
    data() {
        return {
            items: [],
            roles: [],
            selectedUser: {},
            validationErrors: {},
            submitted: false
        };
    },
    watch: {
        display(newVal) {
            if (newVal) {
                this.find();
            }
        }
    },
    methods: {
        closeDialog() {
            this.close(false);
        },
        submit() {
            if (this.loading) return;

            this.submitted = true;
            const codes = [];
            this.roles.forEach((role) => {
                if (role.affected) codes.push(role.id);
            });

            console.log(codes);
            const data = { user_id: this.user.id, role_ids: codes };
            RoleService.userAddRoles(data)
                .then(() => {
                    NotifyService.success(this, '', 'FORM.INFO.OPERATION_SUCCESS');
                    this.close(true);
                })
                .catch(() => {
                    NotifyService.danger(this, '', 'FORM.INFO.OPERATION_FAILED');
                });
        },
        onInputChange(change) {
            this.selectedUser[change.id] = change.value;
        },
        find() {
            if (!this.user.id) return;
            userService.read(this.user.id).then((user) => {
                this.selectedUser = user;
            });
            RoleService.userRoles(this.user.id).then((roles) => {
                this.roles = roles.map((r) => {
                    r.affected = !!r.affected;
                    return r;
                });
            });
        }
    }
});
</script>

<template>
    <Dialog v-if="display" :closable="false" position="top" :style="{ width: '30vw' }" :modal="true" :visible="display" footer="Footer">
        <div>
            <h6>
                {{ $t('FORM.LABELS.ROLE') }} /
                <span class="text-primary">
                    {{ user.name }}
                </span>
            </h6>
            <hr />
            <ul class="treeview-menu">
                <li v-for="(role, index) in roles" :key="role.id">
                    <label class="radio-inline link">
                        <input type="checkbox" v-model="role.affected" />
                        <span :title="role.name" :id="'role' + index">{{ role.name }}</span>
                    </label>
                </li>
            </ul>
        </div>
        <template #footer>
            <Button id="cancelButton" :label="$t('FORM.BUTTONS.CANCEL')" @click="closeDialog" class="p-button-text" />
            <Button id="submitButton" type="submit" @click="submit" :label="user.id ? $t('FORM.BUTTONS.UPDATE') : $t('FORM.BUTTONS.SAVE')" />
        </template>
    </Dialog>
</template>

<style scoped>
.treeview-menu {
    list-style: none;
    padding: 0px;
}
</style>
