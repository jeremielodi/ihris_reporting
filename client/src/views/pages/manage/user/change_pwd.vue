<script>
import { defineComponent } from 'vue';

import UserService from './user.service';
import NotifyService from '@/service/Notify.service';
import _AppCache from '../../../../service/appCache';

export default defineComponent({
    name: 'ChangePasswordModal',
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
            data: {},
            validationErrors: {},
            submitted: false
        };
    },
    watch: {
        display(newVal) {
            if (newVal) {
                console.log(newVal);
            }
        }
    },
    methods: {
        closeDialog() {
            this.data = {};
            this.close(false);
        },
        submit() {
            if (this.loading) return;

            this.submitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            this.loading = true;
            this.data.user_id = _AppCache.getSession().userId;
            UserService.changeSelfPassword(this.data)
                .then(() => {
                    NotifyService.success(this, '', null);
                    this.data = {};
                    this.close(true);
                })
                .catch(() => {
                    NotifyService.danger(this, '', null);
                })
                .finally(() => {
                    this.loading = false;
                });
        },

        find() {
            if (!this.role.uuid) return;
            UserService.read(this.role.uuid).then((role) => {
                this.data = role;
                console.log(role);
            });
        },
        validate() {
            if (!this.submitted) return;

            const requiredCols = ['old_password', 'new_password'];

            requiredCols.forEach((col) => {
                if (this.data[col]) {
                    delete this.validationErrors[col];
                } else {
                    this.validationErrors[col] = true;
                }
            });

            return Object.keys(this.validationErrors).length === 0;
        }
    }
});
</script>

<template>
    <Dialog v-if="display" :header="$t('FORM.LABELS.CHANGE_PASSWORD')" :closable="false" position="top" :style="{ width: '30vw' }" :modal="true" :visible="display" footer="Footer">
        <form @submit.prevent="submit()" class="p-fluid">
            <div class="col-p12" style="margin-top: 25px">
                <div class="p-field">
                    <label for="old_password" :class="{ 'p-error': validationErrors.old_password && submitted }"> {{ $t('FORM.LABELS.OLD_PASSWORD') }}* </label>
                    <br/>
                    <Password
                        id="password"
                        v-model="data.old_password"
                        :feedback="false"
                        v-on:input="validate()"
                        :class="{
                            'p-invalid': validationErrors.old_password && submitted
                        }"
                        toggleMask
                    >
                    </Password>
                </div>

                <div class="p-field">
                    <label for="new_password" :class="{ 'p-error': validationErrors.new_password && submitted }"> {{ $t('FORM.LABELS.NEW_PASSWORD') }}* </label>
                    <br/>
                    <Password
                        id="new_password"
                        v-model="data.new_password"
                        :feedback="false"
                        v-on:input="validate()"
                        :class="{
                            'p-invalid': validationErrors.new_password && submitted
                        }"
                        toggleMask
                    >
                    </Password>
                </div>

                <div class="p-field">
                    <label for="confirm_password" :class="{ 'p-error': validationErrors.confirm_password && submitted }"> {{ $t('FORM.LABELS.CONFIRM_PASSWORD') }}* </label>
                    <br/>
                    <Password
                        id="password"
                        v-model="data.confirm_password"
                        :feedback="false"
                        v-on:input="validate()"
                        :class="{
                            'p-invalid': validationErrors.confirm_password && submitted
                        }"
                        toggleMask
                    >
                    </Password>
                </div>
            </div>
        </form>
        <template #footer>
            <Button :label="$t('FORM.BUTTONS.CANCEL')" @click="closeDialog" class="p-button-text" />
            <Button type="submit" @click="submit" v-if="data.new_password && data.new_password === data.confirm_password" :label="$t('FORM.BUTTONS.SAVE')" />
        </template>
    </Dialog>
</template>
<style scoped>
.p-field {
    padding-top: 10px;
    margin-top: 10px;
}
.p-password {
  width: 100%;
}
</style>
