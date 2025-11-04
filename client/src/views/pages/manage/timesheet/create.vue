<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import Person_TimesheetService from './person_timesheet.service';
import NotifyService from '@/service/Notify.service';
import UtilService from '@/service/UtilService.js';

export default defineComponent({
    name: 'person_timesheetCreateView',
    data() {
        return {
            formSubmitted: false,
            person_timesheetId: null,
            personId: null,
            person_timesheet: {
                id: null,
                parent: null,
                last_modified: null,
                created: null,
                days_absence_justified: 0,
                days_absence_unjustified: 0,
                days_leave: 0,
                days_holiday: 0,
                days_sick: 0,
                days_mission: 0,
                days_worked: 0,
                days_planned: 0,
                month_year: null,
                bonus_local: 0,
                bonus_pepfar: 0,
                bonus_partner: 0,
                bonus_risk: 0,
                project: null,
                salary_received: 0
            }
        };
    },
    created() {
        const { id, personId } = this.$route.query;
        this.personId = personId;
        if (id) {
            this.person_timesheetId = id;
            Person_TimesheetService.read(id).then((person_timesheet) => {
                setTimeout(() => {
                    this.person_timesheet = person_timesheet;
                    this.person_timesheet.i2ce_hidden = !!person_timesheet.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText
    },
    methods: {
        reset() {
            this.person_timesheet = {
                days_absence_justified: 0,
                days_absence_unjustified: 0,
                days_leave: 0,
                days_holiday: 0,
                days_sick: 0,
                days_mission: 0,
                days_worked: 0,
                days_planned: 0,
                month_year: null,
                bonus_local: 0,
                bonus_pepfar: 0,
                bonus_partner: 0,
                bonus_risk: 0,
                project: null,
                salary_received: 0
            };
            this.formSubmitted = false;
            if (this.person_timesheetId) {
                this.$router.push(`/manage/people_record_view?id=${this.personId}`);
            }
        },
        isDefined(value) {
            if (value == 0) return true;
            return value;
        },
        validate() {
            const options = {
                days_absence_justified: this.isDefined(this.person_timesheet.days_absence_justified),
                days_absence_unjustified: this.isDefined(this.person_timesheet.days_absence_unjustified),
                days_leave: this.isDefined(this.person_timesheet.days_leave),
                days_holiday: this.isDefined(this.person_timesheet.days_holiday),
                days_sick: this.isDefined(this.person_timesheet.days_sick),
                days_mission: this.isDefined(this.person_timesheet.days_mission),
                days_worked: this.isDefined(this.person_timesheet.days_worked),
                days_planned: this.isDefined(this.person_timesheet.days_planned),
                month_year: this.isDefined(this.person_timesheet.month_year),
                bonus_local: this.isDefined(this.person_timesheet.bonus_local),
                bonus_pepfar: this.isDefined(this.person_timesheet.bonus_pepfar),
                bonus_partner: this.isDefined(this.person_timesheet.bonus_partner),
                bonus_risk: this.isDefined(this.person_timesheet.bonus_risk),
                salary_received: this.isDefined(this.person_timesheet.salary_received)
            };
            let validKey = true;
            for (const key of Object.keys(options)) {
                if (!options[key]) {
                    console.log('Invalid key:', key);
                    validKey = false;
                    break;
                }
            }

            return validKey;
        },
        createPerson_Timesheet() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            this.loading = true;
            this.person_timesheet.person_id = this.personId;

            const formated = Object.assign({}, this.person_timesheet);
            formated.month_year = UtilService.formatDate(new Date(formated.month_year), 'YYYY-MM-DD');
            delete formated.created;

            const operation = this.person_timesheetId ? Person_TimesheetService.update(this.person_timesheetId, formated) : Person_TimesheetService.create(formated);
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
        <h4>{{ person_timesheetId ? $t('TREE.TIMESHEET_UPDATE') : $t('TREE.TIMESHEET_NEW') }}</h4>

        <form @submit.prevent="createPerson_Timesheet" style="width: 100%">
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
                        id="month_year"
                        v-model="person_timesheet.month_year"
                        label="FORM.LABELS.MONTH_YEAR"
                        type="date"
                        :maxVal="new Date()"
                        :required="true"
                        @onChange="
                            (value) => {
                                person_timesheet.month_year = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <MyInputText
                        id="days_absence_justified"
                        v-model="person_timesheet.days_absence_justified"
                        label="FORM.LABELS.DAYS_ABSENCE_JUSTIFIED"
                        type="number"
                        :required="false"
                        @onChange="
                            (value) => {
                                person_timesheet.days_absence_justified = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="days_absence_unjustified"
                        v-model="person_timesheet.days_absence_unjustified"
                        label="FORM.LABELS.DAYS_ABSENCE_UNJUSTIFIED"
                        type="number"
                        :required="true"
                        @onChange="
                            (value) => {
                                person_timesheet.days_absence_unjustified = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="days_leave"
                        v-model="person_timesheet.days_leave"
                        label="FORM.LABELS.DAYS_LEAVE"
                        type="number"
                        :required="true"
                        @onChange="
                            (value) => {
                                person_timesheet.days_leave = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="days_holiday"
                        v-model="person_timesheet.days_holiday"
                        label="FORM.LABELS.DAYS_HOLIDAY"
                        type="number"
                        :required="true"
                        @onChange="
                            (value) => {
                                person_timesheet.days_holiday = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="days_sick"
                        v-model="person_timesheet.days_sick"
                        type="number"
                        label="FORM.LABELS.DAYS_SICK"
                        :required="true"
                        @onChange="
                            (value) => {
                                person_timesheet.days_sick = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="days_mission"
                        v-model="person_timesheet.days_mission"
                        label="FORM.LABELS.DAYS_MISSION"
                        type="number"
                        :required="true"
                        @onChange="
                            (value) => {
                                person_timesheet.days_mission = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="days_worked"
                        v-model="person_timesheet.days_worked"
                        label="FORM.LABELS.DAYS_WORKED"
                        type="number"
                        :required="true"
                        @onChange="
                            (value) => {
                                person_timesheet.days_worked = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <MyInputText
                        id="days_planned"
                        v-model="person_timesheet.days_planned"
                        label="FORM.LABELS.DAYS_PLANNED"
                        type="number"
                        :required="true"
                        @onChange="
                            (value) => {
                                person_timesheet.days_planned = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <MyInputText
                        id="bonus_local"
                        v-model="person_timesheet.bonus_local"
                        label="FORM.LABELS.BONUS_LOCAL"
                        type="number"
                        :required="true"
                        @onChange="
                            (value) => {
                                person_timesheet.bonus_local = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="bonus_pepfar"
                        v-model="person_timesheet.bonus_pepfar"
                        label="FORM.LABELS.BONUS_PEPFAR"
                        type="number"
                        :required="true"
                        @onChange="
                            (value) => {
                                person_timesheet.bonus_pepfar = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="bonus_partner"
                        v-model="person_timesheet.bonus_partner"
                        label="FORM.LABELS.BONUS_PARTNER"
                        type="number"
                        :required="true"
                        @onChange="
                            (value) => {
                                person_timesheet.bonus_partner = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="bonus_risk"
                        v-model="person_timesheet.bonus_risk"
                        label="FORM.LABELS.BONUS_RISK"
                        type="number"
                        :required="true"
                        @onChange="
                            (value) => {
                                person_timesheet.bonus_risk = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="project"
                        v-model="person_timesheet.project"
                        label="FORM.LABELS.PROJECT"
                        type="number"
                        :required="false"
                        @onChange="
                            (value) => {
                                person_timesheet.project = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="salary_received"
                        v-model="person_timesheet.salary_received"
                        label="FORM.LABELS.SALARY_RECEIVED"
                        type="number"
                        :required="true"
                        @onChange="
                            (value) => {
                                person_timesheet.salary_received = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <div v-if="person_timesheetId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="person_timesheet.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
