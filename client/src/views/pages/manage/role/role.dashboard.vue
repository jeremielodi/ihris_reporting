<script>
import { defineComponent } from 'vue';

import NotifyService from '@/service/Notify.service';
import DashboardManageService from '../metabase_dashboard/dashboard.service';

export default defineComponent({
    name: 'UserDashboardModal',
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
            dashboards: [],
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
            const ids = this.dashboards.filter((action) => action.affected).map((action) => action.uuid);

            const param = {
                role_id: this.role.id,
                dashboard_uuids: [...ids]
            };

            this.loading = true;
            DashboardManageService.assignToRole(param)
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

            DashboardManageService.role(this.role.id).then((dashboards) => {
                this.dashboards = dashboards.map((r) => {
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
        <template #header>
            <div>
                 {{ $t('TREE.METABASE_DASHBOARD') }} / <b>{{ role.name }}</b>
            </div>
        </template>
        <div>
           
            <hr />
            <ul class="treeview-menu">
                <li v-for="act in dashboards" :key="act.id">
                    <label class="radio-inline link">
                        <input type="checkbox" v-model="act.affected" />
                        <span :title="act.label">{{ act.label }}</span>
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
