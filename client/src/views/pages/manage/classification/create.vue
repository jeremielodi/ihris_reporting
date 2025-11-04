<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import ClassificationSelect from '@/components/ClassificationSelect.vue';
import ClassificationService from './classification.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'classificationCreateView',
    data() {
        return {
            formSubmitted: false,
            classificationId: null,
            classification: {
                code: null,
                name: null,
                description: null,
                parent: null
            }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.classificationId = id;
            ClassificationService.read(id).then((classification) => {
                setTimeout(() => {
                    this.classification = classification;
                    this.classification.i2ce_hidden = !!classification.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText,
        ClassificationSelect,
    },
    methods: {
        reset() {
            this.classification = {};
            this.formSubmitted = false;

            if (this.classificationId) {
                this.$router.push('/manage/classification_registry');
            }
        },
        validate() {
            const options = {
                name: this.classification.name,
                parentError: this.classificationId ? this.classificationId == this.classification.parent : true
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
        createclassification() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.classificationId ? ClassificationService.update(this.classificationId, this.classification) : ClassificationService.create(this.classification);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/classification_registry?id=${response.id}`);
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
        <h4>{{ classificationId ? $t('TREE.CLASSIFICATION_UPDATE') : $t('TREE.CLASSIFICATION_NEW') }}</h4>

        <form @submit.prevent="createclassification" style="width: 100%">
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
                        v-model="classification.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                classification.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <MyInputText
                        id="code"
                        v-model="classification.code"
                        label="FORM.LABELS.CODE"
                        :required="false"
                        @onChange="
                            (value) => {
                                classification.code = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                     <MyInputText
                        id="description"
                        v-model="classification.description"
                        label="FORM.LABELS.DESCRIPTION"
                        :required="false"
                        @onChange="
                            (value) => {
                                classification.description = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <ClassificationSelect
                        id="parent"
                        :value="classification.parent"
                        label="FORM.LABELS.PARENT"
                        :required="false"
                        :onChange="
                            (value) => {
                                classification.parent = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="classificationId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="classification.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
