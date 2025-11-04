<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import Job_typeService from './job_type.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'job_typeCreateView',
    data() {
        return {
            formSubmitted: false,
            job_typeId: null,
            job_type: { name: null, code: null, description: null }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.job_typeId = id;
            Job_typeService.read(id).then((job_type) => {
                setTimeout(() => {
                    this.job_type = job_type;
                    this.job_type.i2ce_hidden = !!job_type.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText
    },
    methods: {
        reset() {
            this.job_type = {};
            this.formSubmitted = false;
            if (this.job_typeId) {
                this.$router.push('/manage/job_type_registry');
            }
        },
        validate() {
            const options = {
                name: this.job_type.name
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
        createJob_type() {
            console.log(this.job_type);
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.job_typeId ? Job_typeService.update(this.job_typeId, this.job_type) : Job_typeService.create(this.job_type);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/job_type_registry?id=${response.id}`);
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
        <h4>{{ job_typeId ? $t('TREE.JOB_TYPE_UPDATE') : $t('TREE.JOB_TYPE_NEW') }}</h4>

        <form @submit.prevent="createJob_type" style="width: 100%">
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
                        v-model="job_type.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                job_type.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <MyInputText
                        id="code"
                        v-model="job_type.code"
                        label="FORM.LABELS.CODE"
                        :required="false"
                        @onChange="
                            (value) => {
                                job_type.code = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <MyInputText
                        id="description"
                        v-model="job_type.description"
                        label="FORM.LABELS.DESCRIPTION"
                        :required="false"
                        @onChange="
                            (value) => {
                                job_type.description = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="job_typeId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="job_type.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
