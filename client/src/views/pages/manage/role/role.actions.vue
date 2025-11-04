<script>
import { defineComponent } from 'vue';

import RoleService from './roleService';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'UserRoleModal',
    props: {
        role: Object,
        close: Function,
        display: {
            type: Boolean,
            default: false
        }
    },
    data() {
        return {
            items: [],
            actions: [],
            selectedUser: {},
            validationErrors: {},
            submitted: false,
            loading: false
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
            this.submitted = false;
            this.close(false);
        },
        submit() {
            if (this.loading) return;

            this.submitted = true;
            const ids = this.actions.filter((action) => action.affected).map((action) => action.id);

            const param = {
                role_id: this.role.id,
                action_ids: [...ids]
            };

            this.loading = true;
            RoleService.assignActions(param)
                .then(() => {
                    NotifyService.success(this, '', null);
                    this.close();
                })
                .catch(() => {
                    NotifyService.danger(this, '', null);
                })
                .finally(() => {
                    this.loading = false;
                });
        },

        find() {
            if (!this.role.id) return;

            RoleService.actions(this.role.id).then((actions) => {
                this.actions = actions.map((r) => {
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
                {{ $t('FORM.BUTTONS.ACTIONS') }} /
                <span class="text-primary">
                    {{ role.label }}
                </span>
            </h6>
            <hr />
            <ul class="treeview-menu">
                <li v-for="act in actions" :key="act.id">
                    <label class="radio-inline link">
                        <input type="checkbox" v-model="act.affected" />
                        <span :title="role.description">{{ $t('FORM.ACTIONS.' + act.description) }}</span>
                    </label>
                </li>
            </ul>
        </div>
        <template #footer>
            <Button :label="$t('FORM.BUTTONS.CANCEL')" @click="closeDialog" class="p-button-text" />
            <Button type="submit" @click="submit" :label="$t('FORM.BUTTONS.SAVE')" />
        </template>
    </Dialog>
</template>

<style scoped>
.treeview-menu {
    list-style: none;
    padding: 0px;
}
</style>
