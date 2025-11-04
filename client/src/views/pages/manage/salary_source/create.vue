<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import Salary_sourceService from './salary_source.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'salary_sourceCreateView',
    data() {
        return {
            formSubmitted: false,
            salary_sourceId: null,
            salary_source: { name: null, code: null, description: null }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.salary_sourceId = id;
            Salary_sourceService.read(id).then((salary_source) => {
                setTimeout(() => {
                    this.salary_source = salary_source;
                    this.salary_source.i2ce_hidden = !!salary_source.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText
    },
    methods: {
        reset() {
            this.salary_source = {};
            this.formSubmitted = false;
            if (this.salary_sourceId) {
                this.$router.push('/manage/salary_source_registry');
            }
        },
        validate() {
            const options = {
                name: this.salary_source.name
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
        createSalary_source() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.salary_sourceId ? Salary_sourceService.update(this.salary_sourceId, this.salary_source) : Salary_sourceService.create(this.salary_source);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/salary_source_registry?id=${response.id}`);
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
        <h4>{{ salary_sourceId ? $t('TREE.SALARY_SOURCE_UPDATE') : $t('TREE.SALARY_SOURCE_NEW') }}</h4>

        <form @submit.prevent="createSalary_source" style="width: 100%">
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
                        id="name"
                        v-model="salary_source.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                salary_source.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="code"
                        v-model="salary_source.code"
                        label="FORM.LABELS.CODE"
                        :required="false"
                        @onChange="
                            (value) => {
                                salary_source.code = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="description"
                        v-model="salary_source.description"
                        label="FORM.LABELS.DESCRIPTION"
                        :required="false"
                        @onChange="
                            (value) => {
                                salary_source.description = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="salary_sourceId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="salary_source.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
