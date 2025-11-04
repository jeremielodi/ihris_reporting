<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import personService from './people.service';
import NotifyService from '@/service/Notify.service';
import UtilService from '@/service/UtilService.js';
import GenderSelect from '@/components/GenderSelect.vue';
import MaritalStatusSelect from '@/components/MaritalStatus.vue';
import PyramidSelect from '@/components/pyramidSelect/pyramidSelect.vue';
import CountrySelect from '@/components/CountrySelect.vue';
import DegreeSelect from '@/components/DegreeSelect.vue';
import RoleService from '../role/roleService';
import constants from '../../../../service/constants';

export default defineComponent({
    name: 'personCreateView',
    data() {
        return {
            formSubmitted: false,
            personId: null,
            canEditPerson: false,
            person: { lastname: null, residence: null, dependents: 0 }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.personId = id;
            personService.read(id).then((person) => {
                setTimeout(() => {
                    this.person = person;
                    this.person.gender = person.gender_id;
                    this.person.degree = person.degree_id;
                    this.person.nationality = person.nationality_id;
                    this.person.residence = person.residence;
                    this.person.i2ce_hidden = !!person.i2ce_hidden;
                    this.person.marital_status = person.marital_status_id;
                    this.person.birthdate = new Date(person.birthdate);
                    if (person.recruitment_date) {
                        this.person.recruitment_date = new Date(person.recruitment_date);
                    }
                }, 400);
            });
        }
        this.init();
    },
    components: {
        MyInputText,
        GenderSelect,
        MaritalStatusSelect,
        PyramidSelect,
        CountrySelect,
        DegreeSelect
    },
    methods: {
        reset() {
            this.person = {};
            this.formSubmitted = false;
            if (this.personId) {
                this.$router.back();
            }
        },
        async init() {
            this.canEditPerson = await this.checkPermission(constants.ACTIONS.CAN_EDIT_PERSON);
            if (!this.canEditPerson) {
                this.$router.push('/auth/login');
            }
        },
        checkPermission(id) {
            return RoleService.userHasAction(id);
        },
        validate() {
            const options = {
                lastname: this.person.lastname,
                gender: this.person.gender,
                birthdate: this.person.birthdate,
                birthplace: this.person.birthplace,
                marital_status: this.person.marital_status,
                nationality: this.person.nationality
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
        createPerson() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const formated = Object.assign({}, this.person);
            formated.birthdate = UtilService.formatDate(new Date(formated.birthdate), 'YYYY-MM-DD');
            formated.recruitment_date = UtilService.formatDate(new Date(formated.recruitment_date), 'YYYY-MM-DD');
            delete formated.created;
            const operation = this.personId ? personService.update(this.personId, formated) : personService.create(formated);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/people_record_view?id=${response.id}`);
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
        <h4>{{ personId ? $t('TREE.PEOPLE_UPDATE') : $t('TREE.PERSON_NEW') }}</h4>

        <form @submit.prevent="createPerson" style="width: 100%">
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
                    <MyInputText
                        id="lastname"
                        v-model="person.lastname"
                        label="FORM.LABELS.LASTNAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                person.lastname = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="middlename"
                        v-model="person.middlename"
                        label="FORM.LABELS.MIDDLE_NAME"
                        :required="false"
                        @onChange="
                            (value) => {
                                person.middlename = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <MyInputText
                        id="firstname"
                        v-model="person.firstname"
                        label="FORM.LABELS.FIRST_NAME"
                        :required="false"
                        @onChange="
                            (value) => {
                                person.firstname = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <MyInputText
                        id="birthplace"
                        v-model="person.birthplace"
                        label="FORM.LABELS.PLACE_OF_BIRTH"
                        :required="true"
                        @onChange="
                            (value) => {
                                person.birthplace = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <MyInputText
                        id="birthdate"
                        v-model="person.birthdate"
                        label="FORM.LABELS.DOB"
                        type="date"
                        :maxVal="new Date()"
                        :required="true"
                        @onChange="
                            (value) => {
                                this.person.birthdate = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <GenderSelect
                        id="gender"
                        :value="person.gender"
                        label="FORM.LABELS.GENDER"
                        :required="true"
                        :onChange="
                            (value) => {
                                person.gender = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <br />

                    <DegreeSelect
                        id="degree"
                        :value="person.degree"
                        label="TREE.DEGREE"
                        :required="false"
                        :onChange="
                            (value) => {
                                person.degree = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <MaritalStatusSelect
                        id="marital_status"
                        :value="person.marital_status"
                        label="FORM.LABELS.MARITAL_STATUS"
                        :required="true"
                        :onChange="
                            (value) => {
                                person.marital_status = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <MyInputText
                        id="recruitment_date"
                        v-model="person.recruitment_date"
                        label="FORM.LABELS.RECUITMENT_DATE"
                        type="date"
                        :maxVal="new Date()"
                        :required="true"
                        @onChange="
                            (value) => {
                                this.person.recruitment_date = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <PyramidSelect
                        id="residence"
                        :value="{ key: this.person.residence }"
                        label="FORM.LABELS.RESIDENCE"
                        :required="true"
                        :onChange="
                            (value) => {
                                this.person.residence = value.key;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <br />

                    <CountrySelect
                        id="nationality"
                        :value="person.nationality"
                        label="FORM.LABELS.NATIONALTY"
                        :required="true"
                        :onChange="
                            (value) => {
                                person.nationality = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <MyInputText
                        id="dependents"
                        v-model="person.dependents"
                        label="FORM.LABELS.DEPENDENTS"
                        type="number"
                        :maxVal="new Date()"
                        :required="true"
                        @onChange="
                            (value) => {
                                this.person.dependents = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <div v-if="personId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="person.i2ce_hidden" />
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
