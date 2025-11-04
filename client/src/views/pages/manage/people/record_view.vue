<script>
import { defineComponent } from 'vue';
import OrgUnitService from '@/views/pages/manage/organization_units/orgUnit.service';
import EmploymnettInfoService from './people.employment.service';
import PeopleService from './people.service';
import ContactTypeService from '../contact_type/contact_type.service';
import ContactService from '../contact/contact.service';
import IdentificationService from '../identification/identification.service';
import TimesheetService from '../timesheet/person_timesheet.service';

export default defineComponent({
    name: 'RecordView',
    data() {
        return {
            formSubmitted: false,
            personId: null,
            person: { lastname: null, residence: null },
            employmentStatusInfos: [],
            contactTypes: [],
            contacts: [],
            identifications: [],
            passportList: [],
            timesheetList: [],
            loading: false,
            server: import.meta.env.VITE_SERVER_URL
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.personId = id;
            PeopleService.read(id).then((person) => {
                this.person = person;
                if (this.person.residence) this.getResidence(this.person.residence);
            });
            this.getEmploymentStatusInfo(id);
            this.getPhotos(id);
            this.getContactTypes();
            this.getIdentifications();
            this.getTimeSheets(id);
        }
    },
    methods: {
        getTimeSheets(id) {
            TimesheetService.person(id).then((timesheets) => {
                this.timesheetList = timesheets;
            });
        },
        getIdentifications() {
            IdentificationService.person(this.personId).then((identifications) => {
                this.identifications = identifications;
            });
        },
        getContactTypes() {
            ContactTypeService.read(null, {}).then((types) => {
                this.contactTypes = types;
                return this.getContacts();
            });
        },
        getContacts() {
            ContactService.person(this.personId).then((contacts) => {
                this.contacts = contacts;
                for (const contactType of this.contactTypes) {
                    contactType.contacts = contacts.filter((c) => c.contact_type == contactType.id);
                }
            });
        },
        getPhotos(id) {
            PeopleService.passport.list(id).then((photos) => {
                if (photos.length > 0) {
                    this.passportList = [photos[photos.length - 1]];
                }
            });
        },
        async getEmploymentStatusInfo(id) {
            try {
                this.employmentStatusInfos = await EmploymnettInfoService.person(id);
                for (const info of this.employmentStatusInfos) {
                    info.facility_info = await OrgUnitService.path(info.facility_id);
                }
            } catch (error) {
                console.log(error);
            }
        },
        getResidence(id) {
            OrgUnitService.read(id).then((result) => {
                this.person.residence = result.name;
            });
        },

        reset() {
            this.person = {};
            this.formSubmitted = false;
            if (this.personId) {
                this.$router.back();
            }
        },
        viewFile(path) {
            window.open(`${this.server}uploads/${path}`, '_blank');
        }
    }
});
</script>
<template>
    <div class="card manage-container">
        <h4>
            View Person: <span class="view_title">{{ person.firstname }}, {{ person.lastname }}</span>
        </h4>
        <table class="table">
            <thead>
                <tr>
                    <th colspan="2">
                        <span>{{ $t('FORM.LABELS.PHOTO') }}</span>
                        <span style="float: right">
                            <Button :label="$t('FORM.BUTTONS.' + (passportList.length > 0 ? 'UPDATE' : 'ADD'))" @click="this.$router.push(`/manage/people_passport?personId=${personId}`)" />
                        </span>
                    </th>
                </tr>
            </thead>
            <tbody>
                <template v-for="passport of this.passportList" :key="passport.id">
                    <tr>
                        <td colspan="2">
                            <center>
                                <img @click="viewFile(passport.path)" :src="`${this.server}uploads/${passport.path}`" class="passport" />
                            </center>
                        </td>
                    </tr>
                </template>
            </tbody>
        </table>

        <table class="table">
            <thead>
                <tr>
                    <th colspan="2">
                        <span>{{ $t('FORM.LABELS.AGENT') }}</span>
                        <span style="float: right">
                            <Button :label="$t('FORM.BUTTONS.UPDATE')" @click="this.$router.push(`/manage/people_create?id=${personId}`)" />
                        </span>
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="fieldName">{{ $t('FORM.LABELS.LASTNAME') }}</td>
                    <td class="fieldValue">{{ person.lastname }}</td>
                </tr>
                <tr>
                    <td class="fieldName">{{ $t('FORM.LABELS.MIDDLE_NAME') }}</td>
                    <td class="fieldValue">{{ person.middlename }}</td>
                </tr>
                <tr>
                    <td class="fieldName">{{ $t('FORM.LABELS.FIRST_NAME') }}</td>
                    <td class="fieldValue">{{ person.firstname }}</td>
                </tr>
                <tr>
                    <td class="fieldName">{{ $t('FORM.LABELS.SEX') }}</td>
                    <td class="fieldValue">
                        {{ person.gender }}
                    </td>
                </tr>
                <tr>
                    <td class="fieldName">{{ $t('FORM.LABELS.PLACE_OF_BIRTH') }}</td>
                    <td class="fieldValue">{{ person.birthplace }}</td>
                </tr>
                <tr>
                    <td class="fieldName">{{ $t('FORM.LABELS.DOB') }}</td>
                    <td class="fieldValue">{{ person.birthdate }}</td>
                </tr>
                <tr>
                    <td class="fieldName">{{ $t('FORM.LABELS.MARITAL_STATUS') }}</td>
                    <td class="fieldValue">{{ person.marital_status }}</td>
                </tr>
                <tr>
                    <td class="fieldName">{{ $t('TREE.EDUCATIONAL_LEVEL') }}</td>
                    <td class="fieldValue">{{ person.degree }}</td>
                </tr>

                <tr>
                    <td class="fieldName">{{ $t('FORM.LABELS.RESIDENCE') }}</td>
                    <td class="fieldValue">{{ person.residence }}</td>
                </tr>
                <tr>
                    <td class="fieldName">{{ $t('FORM.LABELS.NATIONALITY') }}</td>
                    <td class="fieldValue">{{ person.nationality }}</td>
                </tr>
            </tbody>
        </table>

        <table class="table">
            <thead>
                <tr>
                    <th colspan="2">
                        <span>{{ $t('TREE.IDENTIFICATION') }}</span>

                        <span style="float: right">
                            <InputGroup>
                                <Button :label="$t('FORM.BUTTONS.ADD')" severity="contrast" @click="this.$router.push(`/manage/identification_create?personId=${personId}`)" />
                            </InputGroup>
                        </span>
                    </th>
                </tr>
            </thead>
            <tbody>
                <template v-for="(identification, index) of identifications" :key="identification.id">
                    <table class="table">
                        <thead>
                            <tr>
                                <td class="fieldName fieldValue" colspan="2">
                                    <div class="infoBil2">
                                        <Button :label="index + 1" severity="info" rounded variant="outlined" aria-label="User" />
                                    </div>

                                    <span style="float: right">
                                        <Button :label="$t('FORM.BUTTONS.UPDATE')" @click="this.$router.push(`/manage/identification_create?id=${identification.id}&personId=${personId}`)" />
                                    </span>
                                </td>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td class="fieldName">{{ $t('FORM.LABELS.TYPE') }}</td>
                                <td class="fieldValue">{{ identification.type_name }}</td>
                            </tr>
                            <tr>
                                <td class="fieldName">{{ $t('FORM.LABELS.NUMBER') }}</td>
                                <td class="fieldValue">{{ identification.number }}</td>
                            </tr>
                            <tr>
                                <td class="fieldName">{{ $t('Date of Issue') }}</td>
                                <td class="fieldValue">{{ identification.acquisition_date }}</td>
                            </tr>
                            <tr>
                                <td class="fieldName">{{ $t(' Date of Expiration') }}</td>
                                <td class="fieldValue">{{ identification.expiration_date }}</td>
                            </tr>
                            <tr>
                                <td class="fieldName">{{ $t('Country of Issue') }}</td>
                                <td class="fieldValue">{{ identification.country_name }}</td>
                            </tr>
                        </tbody>
                    </table>
                </template>
            </tbody>
        </table>
        <table class="table">
            <thead>
                <tr>
                    <th colspan="2">
                        <span>{{ $t('FORM.LABELS.CONTACT') }}</span>
                    </th>
                </tr>
            </thead>
            <tbody>
                <template v-for="contactType of contactTypes" :key="contactType.id">
                    <table class="table">
                        <thead>
                            <tr>
                                <th colspan="2">
                                    <span>{{ contactType.name }}</span>
                                    <span style="float: right" v-if="(contactType.contacts || []).length == 0">
                                        <InputGroup>
                                            <Button :label="$t('FORM.BUTTONS.ADD')" severity="contrast" @click="this.$router.push(`/manage/contact_create?typeId=${contactType.id}&personId=${personId}`)" />
                                        </InputGroup>
                                    </span>
                                    <span style="float: right" v-if="(contactType.contacts || []).length > 0">
                                        <Button :label="$t('FORM.BUTTONS.UPDATE')" @click="this.$router.push(`/manage/contact_create?id=${contactType.contacts[0].id}&personId=${personId}`)" />
                                    </span>
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            <template v-for="contact of contactType.contacts || []" :key="contact.id">
                                <tr>
                                    <td class="fieldName">Adresse</td>
                                    <td class="fieldValue">{{ contact.address }}</td>
                                </tr>
                                <tr>
                                    <td class="fieldName">Mobile Phone Number:</td>
                                    <td class="fieldValue">{{ contact.mobile_phone }}</td>
                                </tr>
                                <tr>
                                    <td class="fieldName">Mailing Address:</td>
                                    <td class="fieldValue">{{ contact.email }}</td>
                                </tr>
                                <tr>
                                    <td class="fieldName">Telephone Number:</td>
                                    <td class="fieldValue">{{ contact.telephone }}</td>
                                </tr>

                                <tr>
                                    <td class="fieldName">Alternate Telephone Number:</td>
                                    <td class="fieldValue">{{ contact.alt_phone }}</td>
                                </tr>
                                <tr>
                                    <td class="fieldName">Fax Number:</td>
                                    <td class="fieldValue">{{ contact.fax }}</td>
                                </tr>
                                <tr>
                                    <td class="fieldName">Notes:</td>
                                    <td class="fieldValue">{{ contact.notes }}</td>
                                </tr>
                            </template>
                        </tbody>
                    </table>
                </template>
            </tbody>
        </table>

        <table class="table">
            <thead>
                <tr>
                    <th colspan="2">
                        <span>{{ $t('FORM.LABELS.EMPLOYMENT_STATUS_INFO') }}</span>

                        <span style="float: right">
                            <InputGroup>
                                <Button :label="$t('FORM.BUTTONS.ADD')" severity="contrast" @click="this.$router.push(`/manage/people_employment_status?personId=${personId}`)" />
                            </InputGroup>
                        </span>
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td colspan="2" v-if="employmentStatusInfos.length > 0">
                        <template v-for="(info, index) of employmentStatusInfos" :key="info.id">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <td class="fieldName fieldValue" colspan="2">
                                            <div class="infoBil2">
                                                <Button :label="index + 1" severity="info" rounded variant="outlined" aria-label="User" />
                                            </div>

                                            <span style="float: right">
                                                <Button v-if="employmentStatusInfos.length > 0" :label="$t('FORM.BUTTONS.UPDATE')" @click="this.$router.push(`/manage/people_employment_status?id=${info.id}&personId=${personId}`)" />
                                            </span>
                                        </td>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td class="fieldName">{{ $t('FORM.LABELS.JOB') }}</td>
                                        <td class="fieldValue">{{ info.classification_name }}</td>
                                    </tr>
                                    <tr>
                                        <td class="fieldName">{{ $t('TREE.GRADE') }}</td>
                                        <td class="fieldValue">{{ info.grade_name }}</td>
                                    </tr>
                                    <tr>
                                        <td class="fieldName">{{ $t('FORM.LABELS.CATEGORY') }}</td>
                                        <td class="fieldValue">{{ info.cadre_name }}</td>
                                    </tr>
                                    <tr>
                                        <td class="fieldName">{{ $t('FORM.LABELS.FACILITY') }}</td>
                                        <td class="fieldValue">
                                            <Breadcrumb :model="info.facility_info" class="border-0" v-if="info.facility_info">
                                                <template #item="{ item }">
                                                    <span style="cursor: pointer">
                                                        {{ item.name }}
                                                    </span>
                                                </template>
                                                <template #separator> / </template>
                                            </Breadcrumb>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class="fieldName">{{ $t('FORM.LABELS.DATE') }}</td>
                                        <td class="fieldValue">{{ info.employment_date }}</td>
                                    </tr>
                                    <tr>
                                        <td class="fieldName">Ref commission d'affectation</td>
                                        <td class="fieldValue">{{ info.position_decision_ref }}</td>
                                    </tr>
                                    <tr>
                                        <td class="fieldName">Ref Act d'engagement</td>
                                        <td class="fieldValue">{{ info.ref_engagement }}</td>
                                    </tr>

                                    <tr>
                                        <td class="fieldName">{{ $t('TREE.SALARY_SOURCE') }}</td>
                                        <td class="fieldValue">{{ info.salary_source_name }}</td>
                                    </tr>
                                    <tr>
                                        <td class="fieldName">{{ $t('TREE.JOB_TYPE') }}</td>
                                        <td class="fieldValue">{{ info.job_type_name }}</td>
                                    </tr>
                                    <tr>
                                        <td class="fieldName">{{ $t('FORM.LABELS.SALARY') }}</td>
                                        <td class="fieldValue">{{ $t(`FORM.LABELS.${info.salary ? 'YES' : 'NO'}`) }}</td>
                                    </tr>

                                    <tr>
                                        <td class="fieldName">Prime</td>
                                        <td class="fieldValue">{{ $t(`FORM.LABELS.${info.allowance ? 'YES' : 'NO'}`) }}</td>
                                    </tr>
                                    <tr>
                                        <td class="fieldName">Position</td>
                                        <td class="fieldValue">{{ info.employee_status_name }}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </template>
                        <br />
                    </td>
                </tr>
            </tbody>
        </table>

        <table class="table">
            <thead>
                <tr>
                    <th colspan="2">
                        <span>{{ $t('TREE.TIMESHEET') }} (Timesheet)</span>
                        <span style="float: right">
                            <InputGroup>
                                <Button :label="$t('FORM.BUTTONS.ADD')" severity="contrast" @click="this.$router.push(`/manage/timesheet?personId=${personId}`)" />
                            </InputGroup>
                        </span>
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td colspan="2" v-if="timesheetList.length > 0">
                        <div style="height: 200px; overflow-y: scroll">
                            <template v-for="timesheet of timesheetList" :key="timesheet.id">
                                <div style="padding: 2px; margin-top: 10px" class="bottomBorder">
                                    <i class="pi pi-pencil" style="cursor: pointer" @click="this.$router.push(`/manage/timesheet?id=${timesheet.id}&personId=${personId}`)"></i>

                                    {{ $t('FORM.LABELS.MONTH_YEAR') }}: <span class="text-primary">{{ timesheet.month_year }}</span
                                    >,

                                    {{ $t('FORM.LABELS.DAYS_ABSENCE_JUSTIFIED') }}: <span class="text-primary">{{ timesheet.days_absence_justified }}</span
                                    >,

                                    {{ $t('FORM.LABELS.DAYS_ABSENCE_UNJUSTIFIED') }}: <span class="text-primary">{{ timesheet.days_absence_unjustified }}</span
                                    >,

                                    {{ $t('FORM.LABELS.DAYS_LEAVE') }}: <span class="text-primary">{{ timesheet.days_leave }}</span
                                    >,

                                    {{ $t('FORM.LABELS.DAYS_HOLIDAY') }}: <span class="text-primary">{{ timesheet.days_holiday }}</span
                                    >,

                                    {{ $t('FORM.LABELS.DAYS_SICK') }}: <span class="text-primary">{{ timesheet.days_sick }}</span
                                    >,

                                    {{ $t('FORM.LABELS.DAYS_MISSION') }}: <span class="text-primary">{{ timesheet.days_mission }}</span
                                    >,

                                    {{ $t('FORM.LABELS.DAYS_WORKED') }}: <span class="text-primary">{{ timesheet.days_worked }}</span
                                    >,

                                    {{ $t('FORM.LABELS.DAYS_PLANNED') }}: <span class="text-primary">{{ timesheet.days_planned }}</span
                                    >,

                                    {{ $t('FORM.LABELS.BONUS_LOCAL') }}: <span class="text-primary">{{ timesheet.bonus_local }}</span
                                    >,

                                    {{ $t('FORM.LABELS.BONUS_PEPFAR') }}: <span class="text-primary">{{ timesheet.bonus_pepfar }}</span
                                    >,

                                    {{ $t('FORM.LABELS.BONUS_PARTNER') }}: <span class="text-primary">{{ timesheet.bonus_partner }}</span
                                    >,

                                    {{ $t('FORM.LABELS.BONUS_RISK') }}: <span class="text-primary">{{ timesheet.bonus_risk }}</span
                                    >,

                                    {{ $t('FORM.LABELS.PROJECT') }}: <span class="text-primary">{{ timesheet.project }}</span
                                    >,

                                    {{ $t('FORM.LABELS.SALARY_RECEIVED') }}:
                                    <span class="text-primary">{{ timesheet.salary_received }}</span>
                                </div>
                            </template>
                        </div>
                        <br />
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<style lang="css" scoped>
.table {
    box-shadow: 0px -1px 10px rgb(196, 196, 201);
    width: 100%;
    margin-top: 30px;
    margin-bottom: 20px;
    position: relative;
    z-index: 10;
    border-radius: 5px;
    background-color: #fff;
}

.table table {
    margin: 5px;
    margin-top: 20px;
    width: 99%;
}

thead {
    background-color: #f3f4f6;
    color: #585858;
    font-size: 17px;
}

thead tr {
    text-align: left;
}

thead tr th {
    padding: 10px;
}

tbody td {
    padding: 5px;
}

.leftBorder {
    border-left: 1px solid #adafb1;
}

.rightBorder {
    border-right: 1px solid #adafb1;
}

.bottomBorder {
    border-bottom: 1px solid #adafb1;
}

.fieldName {
    border-bottom: 1px solid #f2f2f5;
    width: 30%;
}

.view_title {
    color: rgb(98, 98, 244);
}

.fieldValue {
    border-left: 1px solid #f2f2f5;
    border-bottom: 1px solid #f2f2f5;
    font-weight: 600;
    color: rgb(98, 98, 244);
}

.infoBil2 {
    width: 40px;
    float: left !important;
}

.infoBil {
    background-color: rgb(167, 167, 170);
    padding: 5px;
    padding-left: 12px;
    padding-right: 12px;
    border-radius: 50%;
    color: white;
    font-weight: bold;
    width: 40px;
    margin-top: 10px !important;
    text-align: center;
    float: left;
}

.passport {
    max-width: 170px;
    text-align: center;
    margin: auto;
    cursor: pointer;
}

.manage-container {
    background: #efeeee !important;
    padding-bottom: 100px;
}
</style>
