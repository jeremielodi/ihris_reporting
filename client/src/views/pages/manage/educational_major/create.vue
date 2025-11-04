<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import EducationalMajourService from './educational_major.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'educationalMajorCreateView',
    data() {
        return {
            formSubmitted: false,
            educationalMajorId: null,
            educationalMajor: { name: null, code: null }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.educationalMajorId = id;
            EducationalMajourService.read(id).then((educationalMajor) => {
                setTimeout(() => {
                    this.educationalMajor = educationalMajor;
                    this.educationalMajor.i2ce_hidden = !!educationalMajor.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText
    },
    methods: {
        reset() {
            this.educationalMajor = {};
            this.formSubmitted = false;
            if (this.educationalMajorId) {
                this.$router.push('/manage/educationalMajor_registry');
            }
        },
        validate() {
            const options = {
                name: this.educationalMajor.name
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
        createeducationalMajor() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.educationalMajorId ? EducationalMajourService.update(this.educationalMajorId, this.educationalMajor) : EducationalMajourService.create(this.educationalMajor);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/educational_major_registry?id=${response.id}`);
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
        <h4>{{ educationalMajorId ? $t('TREE.EDUCATIONAL_MAJOR_UPDATE') : $t('TREE.EDUCATIONAL_MAJOR_NEW') }}</h4>

        <form @submit.prevent="createeducationalMajor" style="width: 100%">
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
                        v-model="educationalMajor.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                educationalMajor.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="code"
                        v-model="educationalMajor.code"
                        label="FORM.LABELS.CODE"
                        :required="false"
                        @onChange="
                            (value) => {
                                educationalMajor.code = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="educationalMajorId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="educationalMajor.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
