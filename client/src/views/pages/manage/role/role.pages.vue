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
            tree: [],
            allPage: false,
            selectedUser: {},
            validationErrors: {},
            submitted: false
        };
    },
    watch: {
        display(newVal) {
            if (newVal) {
                this.load();
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
            var codes = [];
            for (var i = 0; i < this.tree.length; i++) {
                var _module = this.tree[i];
                for (var j = 0; j < _module.pages.length; j++) {
                    var page = _module.pages[j];
                    if (page.affected) {
                        codes.push(page.code);
                    }
                }
            }

            var data = {
                role_id: this.role.id,
                pageCodes: codes
            };
            RoleService.affectPages(data)
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
        load() {
            RoleService.loadModules(this.role.id).then((modules) => {
                this.tree = modules.filter((_module) => {
                    _module.pages.forEach((p) => {
                        p.affected = !!p.affected;
                    });
                    return _module.pages.length > 0;
                });
            });
        },
        setModule(modules) {
            const moduleState = !modules.affected;
            modules.affected = moduleState;
            modules.pages.forEach((p) => {
                p.affected = moduleState;
            });
        },
        selectAll() {
            this.allPage = !this.allPage;
            for (var i = 0; i < this.tree.length; i++) {
                var _module = this.tree[i];
                for (var j = 0; j < _module.pages.length; j++) {
                    var page = _module.pages[j];
                    page.affected = this.allPage;
                }
            }
        }
    }
});
</script>

<template>
    <Dialog v-if="display" :closable="false" position="top" :style="{ width: '30vw' }" :modal="true" :visible="display" footer="Footer">
        <div>
            <h6>
                Pages pour
                <span class="text-primary">
                    {{ role.label }}
                </span>
            </h6>
            <hr />

            <div v-for="_module in tree" :key="_module.id">
                <h5 @click="setModule(_module)" class="link">
                    <i :class="_module.icon"></i> <b>{{ $t(_module.label) }}</b>
                </h5>
                <div>
                    <ul class="treeview-menu">
                        <li v-for="page in _module.pages" :key="page.id">
                            <label class="radio-inline link">
                                <input type="checkbox" v-model="page.affected" />
                                <span :title="$t(page.label)">{{ $t(page.label) }}</span>
                            </label>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
        <template #footer>
            <Button :label="$t('FORM.INFO.SELECT_ALL')" @click="selectAll()" class="p-button-text"> </Button>
            <Button :label="$t('FORM.BUTTONS.CANCEL')" @click="closeDialog" class="p-button-text" />
            <Button type="submit" @click="submit" :label="$t('FORM.BUTTONS.SAVE')" />
        </template>
    </Dialog>
</template>

<style scoped>
.treeview-menu {
    list-style: none;
    padding: 0px;
    padding-left: 10px;
}
</style>
