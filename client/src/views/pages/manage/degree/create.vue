<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import DegreeSelect from '@/components/DegreeSelect.vue';
import DegreeService from './degreeService';
import NotifyService from '../../../../service/Notify.service';

export default defineComponent({
    name: 'degreeCreateView',
    data() {
        return {
            formSubmitted: false,
            degreeId: null,
            degree: {
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
            this.degreeId = id;
            DegreeService.read(id).then((degree) => {
                setTimeout(() => {
                    this.degree = degree;
                    this.degree.i2ce_hidden = !!degree.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText,
        DegreeSelect,
    },
    methods: {
        reset() {
            this.degree = {};
            this.formSubmitted = false;

            if (this.degreeId) {
                this.$router.push('/manage/degree_registry');
            }
        },
        validate() {
            const options = {
                name: this.degree.name,
                parentError: this.degreeId ? this.degreeId == this.degree.parent : true
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
        createdegree() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.degreeId ? DegreeService.update(this.degreeId, this.degree) : DegreeService.create(this.degree);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/degree_registry?id=${response.id}`);
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
        <h4>{{ degreeId ? $t('TREE.DEGREE_UPDATE') : $t('TREE.DEGREE_NEW') }}</h4>

        <form @submit.prevent="createdegree" style="width: 100%">
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
                        v-model="degree.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                degree.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <DegreeSelect
                        id="parent"
                        :value="degree.parent"
                        label="FORM.LABELS.PARENT"
                        :required="false"
                        :onChange="
                            (value) => {
                                degree.parent = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="degreeId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="degree.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
