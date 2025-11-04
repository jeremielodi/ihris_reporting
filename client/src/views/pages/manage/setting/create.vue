<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import SettingService from './setting.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'settingCreateView',
    data() {
        return {
            formSubmitted: false,
            settingId: null,
            setting: { app_name: null }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.settingId = id;
            SettingService.read(id).then((setting) => {
                setTimeout(() => {
                    this.setting = setting;
                    this.setting.i2ce_hidden = !!setting.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText
    },
    methods: {
        reset() {
            this.setting = {};
            this.formSubmitted = false;
            if (this.settingId) {
                this.$router.push('/manage/setting_registry');
            }
        },
        validate() {
            const options = {
                app_name: this.setting.app_name,
                app_version: this.setting.app_version,
                responsible_name: this.setting.responsible_name,
                responsible_number: this.setting.responsible_number
            };
            let validKey = true;
            for (const key of Object.keys(options)) {
                if (!options[key]) {
                    validKey = false;
                    break;
                }
            }

            return validKey;
        },
        createSetting() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.settingId ? SettingService.update(this.settingId, this.setting) : SettingService.create(this.setting);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/setting_registry?id=${response.id}`);
                })
                .catch(() => {
                    NotifyService.danger(this, '', null);
                })
                .finally(() => {
                    this.loading = false;
                });
        }
    }
});
</script>

<template>
    <div class="card manage-container">
        <h4>{{ settingId ? $t('TREE.SETTING_UPDATE') : $t('TREE.SETTING_NEW') }}</h4>

        <form @submit.prevent="createSetting" style="width: 100%">
            <div class="grid">
                <div class="col-12">
                    <hr />
                    <button type="submit" class="p-button p-component p-button-primary">
                        <span class="p-button-label">
                            {{ $t('FORM.BUTTONS.SUBMIT') }}
                        </span>
                    </button>
                    <button type="reset" @click="reset" class="p-button p-component p-button-secondary" style="margin-left: 10px">
                        <span class="p-button-label">{{ $t('FORM.BUTTONS.CANCEL') }}</span>
                    </button>
                    <hr />
                </div>
                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <MyInputText
                        id="app_name"
                        v-model="setting.app_name"
                        label="FORM.LABELS.APP_NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                setting.app_name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="responsible_name"
                        v-model="setting.responsible_name"
                        label="FORM.LABELS.RESPONSIBLE_NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                setting.responsible_name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="responsible_number"
                        v-model="setting.responsible_number"
                        label="FORM.LABELS.RESPONSIBLE_NUMBER"
                        :required="true"
                        @onChange="
                            (value) => {
                                setting.responsible_number = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="settingId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="setting.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
