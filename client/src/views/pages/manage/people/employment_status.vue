<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import EmploymnettInfoService from './people.employment.service';
import PersonService from './people.service';
import NotifyService from '@/service/Notify.service';
import UtilService from '@/service/UtilService.js';
import GradeSelect from '@/components/GradeSelect.vue';
import CadreSelect from '@/components/CadreSelect.vue';
import ClassificationSelect from '@/components/ClassificationSelect.vue';
import PyramidSelect from '@/components/pyramidSelect/pyramidSelect.vue';
import EmployeeStatusSelect from '@/components/EmployeeStatusSelect.vue';
import SalarySourceSelect from '@/components/SalarySourceSelect.vue';
import JobTypeSelect from '@/components/JobTypeSelect.vue';

export default defineComponent({
    name: 'EmploymentStatusInfoView',
    data() {
        return {
            formSubmitted: false,
            personId: null,
            person: {},
            employmnet_info: {
                classification: null,
                grade: null,
                facility_id: null,
                employment_date: null
            }
        };
    },
    created() {
        const { id, personId } = this.$route.query;
        if (personId) {
            this.personId = personId;
            PersonService.read(personId).then((person) => {
                this.person = person;
            });
        }
        if (id) {
            this.employmnet_infoId = id;
            EmploymnettInfoService.read(id).then((info) => {
                setTimeout(() => {
                    this.employmnet_info = info;
                    this.employmnet_info.salary = !!this.employmnet_info.salary;
                    this.employmnet_info.allowance = !!this.employmnet_info.allowance;

                    if (info.start_service_date) {
                        this.employmnet_info.start_service_date = new Date(info.start_service_date);
                    }

                    if (info.employment_date) {
                        this.employmnet_info.employment_date = new Date(info.employment_date);
                    }
                }, 400);
            });
        }
    },
    components: {
        MyInputText,
        CadreSelect,
        GradeSelect,
        ClassificationSelect,
        PyramidSelect,
        EmployeeStatusSelect,
        SalarySourceSelect,
        JobTypeSelect
    },
    methods: {
        reset() {
            this.employmnet_info = {};
            this.formSubmitted = false;
            if (this.employmnet_infoId || this.personId) {
                this.$router.back();
            }
        },
        validate() {
            const options = {
                classification: this.employmnet_info.classification,
                grade: this.employmnet_info.grade,
                facility_id: this.employmnet_info.facility_id,
                employment_date: this.employmnet_info.employment_date,
            };
            let validKey = true;
            for (const key of Object.keys(options)) {
                if (!options[key]) {
                    console.log(key);
                    validKey = false;
                    break;
                }
            }

            return validKey;
        },
        sumit() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const formated = Object.assign({}, this.employmnet_info);
            formated.person_id = this.personId;
            formated.employment_date = UtilService.formatDate(formated.employment_date, 'YYYY-MM-DD');
            formated.start_service_date = UtilService.formatDate(formated.start_service_date, 'YYYY-MM-DD');

            delete formated.created;
            const operation = this.employmnet_infoId ? EmploymnettInfoService.update(this.employmnet_infoId, formated) : EmploymnettInfoService.create(formated);
            operation
                .then(() => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/people_record_view?id=${this.personId}`);
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
        <h4>Employment Status Information</h4>
        <h5>
            Person: <span class="view_title">{{ person.firstname }}, {{ person.lastname }}</span>
        </h5>
        <form @submit.prevent="sumit" style="width: 100%">
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

            <div class="grid blockPanel">
                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <GradeSelect
                        id="grade"
                        :value="this.employmnet_info.grade"
                        label="TREE.GRADE"
                        :required="true"
                        :onChange="
                            (value) => {
                                this.employmnet_info.grade = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <CadreSelect
                        id="cadre"
                        :value="this.employmnet_info.cadre"
                        label="Categorie"
                        :required="false"
                        :onChange="
                            (value) => {
                                this.employmnet_info.cadre = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <ClassificationSelect
                        id="classification"
                        :value="this.employmnet_info.classification"
                        label="Profession"
                        :required="true"
                        :onChange="
                            (value) => {
                                this.employmnet_info.classification = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />


                    <MyInputText
                        id="employment_date"
                        :modelValue="this.employmnet_info.employment_date"
                        label="Date d'engagement"
                        type="date"
                        :maxVal="new Date()"
                        :required="true"
                        @onChange="
                            (value) => {
                                this.employmnet_info.employment_date = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />


                    <PyramidSelect
                        id="access"
                        :value="{ key: this.employmnet_info.facility_id }"
                        label="FORM.LABELS.FACILITY"
                        :required="true"
                        :onChange="
                            (value) => {
                                if (!value || !value.key) return;
                                this.employmnet_info.facility_id = value.key;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />


                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">

                   <MyInputText
                        id="comm_affectation"
                        v-model="this.employmnet_info.position_decision_ref"
                        label="Ref commission d'affectation"
                        type="text"
                        :required="false"
                        @onChange="
                            (value) => {
                                this.employmnet_info.position_decision_ref = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <MyInputText
                        id="ref_engagement"
                        v-model="this.employmnet_info.ref_engagement"
                        label="Ref Act d'engagement"
                        type="text"
                        :required="false"
                        @onChange="
                            (value) => {
                                this.employmnet_info.ref_engagement = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <EmployeeStatusSelect
                        id="employee_status"
                        :value="this.employmnet_info.employee_status"
                        label="TREE.EMPLOYMENT_STATUS"
                        :required="false"
                        :onChange="
                            (value) => {
                                this.employmnet_info.employee_status = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />



                    <MyInputText
                        id="start_service_date"
                        :modelValue="this.employmnet_info.start_service_date"
                        label="Date d'engagement"
                        type="date"
                        :maxVal="new Date()"
                        :required="true"
                        @onChange="
                            (value) => {
                                this.employmnet_info.start_service_date = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <SalarySourceSelect
                        id="salary_source"
                        :value="this.employmnet_info.salary_source"
                        label="TREE.SALARY_SOURCE"
                        :required="false"
                        :onChange="
                            (value) => {
                                this.employmnet_info.salary_source = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <JobTypeSelect
                        id="job_type"
                        :value="this.employmnet_info.job_type"
                        label="TREE.JOB_TYPE"
                        :required="false"
                        :onChange="
                            (value) => {
                                this.employmnet_info.job_type = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <MyInputText
                        id="seniority"
                        v-model="this.employmnet_info.seniority"
                        label="Echellon"
                        type="number"
                        :maxValue="11"
                        :required="false"
                        @onChange="
                            (value) => {
                                this.employmnet_info.seniority = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <div  class="p-field-checkbox" style="margin-top: 10px;">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="this.employmnet_info.salary" />
                        <label for="i2ce_hidden"> {{ ' ' + $t('FORM.LABELS.SALARY') }}</label>
                    </div>

                    <div  class="p-field-checkbox" style="margin-top: 10px;">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="this.employmnet_info.allowance" />
                        <label for="i2ce_hidden"> {{ ' ' + $t('FORM.LABELS.ALLOWANCE') }}</label>
                    </div>

                    <div  class="p-field-checkbox" style="margin-top: 10px;">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="this.employmnet_info.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ ' ' + $t('FORM.LABELS.INACTIVE') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
<style lang="css" scoped>
.blockPanel {
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    margin: 10px;
}
</style>
