<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import employment_statuservice from './employment_status.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'employment_statusCreateView',
    data() {
        return {
            formSubmitted: false,
            employment_statusId: null,
            employment_status: { code: null, name: null }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.employment_statusId = id;
            employment_statuservice.read(id).then((employment_status) => {
                setTimeout(() => {
                    this.employment_status = employment_status;
                    this.employment_status.i2ce_hidden = !!employment_status.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText
    },
    methods: {
        reset() {
            this.employment_status = {};
            this.formSubmitted = false;
            if (this.employment_statusId) {
                this.$router.push('/manage/employment_status_registry');
            }
        },
        validate() {
            const options = {
                name: this.employment_status.name
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
        createEmployment_status() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.employment_statusId ? employment_statuservice.update(this.employment_statusId, this.employment_status) : employment_statuservice.create(this.employment_status);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/employment_status_registry?id=${response.id}`);
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
        <h4>{{ employment_statusId ? $t('TREE.EMPLOYMENT_STATUS_UPDATE') : $t('TREE.EMPLOYMENT_STATUS_NEW') }}</h4>

        <form @submit.prevent="createEmployment_status" style="width: 100%">
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
                        id="code"
                        v-model="employment_status.code"
                        label="FORM.LABELS.CODE"
                        :required="false"
                        @onChange="
                            (value) => {
                                employment_status.code = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="name"
                        v-model="employment_status.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                employment_status.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="employment_statusId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="employment_status.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
