<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import ClassificationSelect from '@/components/ClassificationSelect.vue';
import Job_titleService from './job_title.service';
import CadreSelect from '@/components/CadreSelect.vue';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'job_titleCreateView',
    data() {
        return {
            formSubmitted: false,
            job_titleId: null,
            job_title: {
                name: null,
                cadre: null,
                classification: null
            }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.job_titleId = id;
            Job_titleService.read(id).then((job_title) => {
                setTimeout(() => {
                    this.job_title = job_title;
                    this.job_title.i2ce_hidden = !!job_title.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText,
        ClassificationSelect,
        CadreSelect
    },
    methods: {
        reset() {
            this.job_title = {};
            this.formSubmitted = false;
            if (this.job_titleId) {
                this.$router.push('/manage/job_title_registry');
            }
        },
        validate() {
            console.log(this.job_title);
            const options = {
                name: this.job_title.name,
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
        createJob_title() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.job_titleId ? Job_titleService.update(this.job_titleId, this.job_title) : Job_titleService.create(this.job_title);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/job_title_registry?id=${response.id}`);
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
        <h4>{{ job_titleId ? $t('TREE.JOB_TITLE_UPDATE') : $t('TREE.JOB_TITLE_NEW') }}</h4>

        <form @submit.prevent="createJob_title" style="width: 100%">
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
                        v-model="job_title.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                job_title.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <CadreSelect
                        id="cadre"
                        :value="job_title.cadre"
                        label="TREE.CADRE"
                        :required="false"
                        :onChange="
                            (value) => {
                                job_title.cadre = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <ClassificationSelect
                        id="classification"
                        :value="job_title.classification"
                        label="TREE.CLASSIFICATIONS"
                        :required="false"
                        :onChange="
                            (value) => {
                                job_title.classification = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                   
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="job_titleId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="job_title.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
