<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import GradeSelect from '@/components/GradeSelect.vue';
import GradeService from './grade.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'gradeCreateView',
    data() {
        return {
            formSubmitted: false,
            gradeId: null,
            grade: {
                name: null,
                description: null,
                parnet: null
            }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.gradeId = id;
            GradeService.read(id).then((grade) => {
                setTimeout(() => {
                    this.grade = grade;
                    this.grade.i2ce_hidden = !!grade.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText,
        GradeSelect
    },
    methods: {
        reset() {
            this.grade = {};
            this.formSubmitted = false;
            if (this.gradeId) {
                this.$router.push('/manage/grade_registry');
            }
        },
        validate() {
            const options = {
                name: this.grade.name,
                parentError: this.gradeId ? this.gradeId == this.grade.parent : true
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
        creategrade() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.gradeId ? GradeService.update(this.gradeId, this.grade) : GradeService.create(this.grade);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/grade_registry?id=${response.id}`);
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
        <h4>{{ gradeId ? $t('TREE.GRADE_UPDATE') : $t('TREE.GRADE_NEW') }}</h4>

        <form @submit.prevent="creategrade" style="width: 100%">
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
                        v-model="grade.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                grade.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                     <MyInputText
                        id="description"
                        v-model="grade.description"
                        label="FORM.LABELS.DESCRIPTION"
                        :required="false"
                        @onChange="
                            (value) => {
                                grade.description = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <GradeSelect
                        id="parent"
                        :value="grade.parent"
                        label="FORM.LABELS.PARENT"
                        :required="false"
                        :onChange="
                            (value) => {
                                grade.parent = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="gradeId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="grade.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
