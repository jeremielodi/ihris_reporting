<script>
import { defineComponent } from 'vue';
import classificationService from '../../classification/classification.service';
import cadreService from '../../cadre/cadre.service';
import jobTypeService from '../../job_type/job_type.service';
import MaritalStatusSelect from '@/components/MaritalStatus.vue';
import GradeSelect from '@/components/GradeSelect.vue';
import GenderSelect from '@/components/GenderSelect.vue';

export default defineComponent({
    props: {
        selectedRow: Object,
        display: {
            type: Boolean,
            default: false
        },
        close: Function,
        saveEdit: Function
    },
    data() {
        return {
            classifications: [],
            jobs: [],
            jobTypes: [],
            editedRow: null,
            item: {}
        };
    },
    created() {
        this.init();
    },
    watch: {
        display(newVal) {
            if (newVal) {
                this.editedRow = JSON.parse(JSON.stringify(this.selectedRow));
            }
        }
    },
    components: {
        MaritalStatusSelect,
        GradeSelect,
        GenderSelect
    },
    methods: {
        init() {
            cadreService
                .read()
                .then((jobs) => {
                    this.jobs = jobs;
                    return classificationService.read();
                })
                .then((classes) => {
                    this.classifications = classes;
                    return jobTypeService.read();
                })
                .then((jobType) => {
                    this.jobTypes = jobType;
                });
        }
    }
});
</script>

<template>
    <Dialog v-model:visible="display" modal header="Modifier l'employé"
        :closable="true"        :style="{ width: '800px' }" :breakpoints="{ '1199px': '75vw', '575px': '90vw' }">
        <div v-if="editedRow" class="p-fluid">
            <br />
            <div class="grid formgrid p-fluid">
                <!-- Personal Information Section -->
                <div class="field col-12">
                    <h3 class="text-lg font-semibold mb-3">Informations personnelles</h3>
                </div>

                <!-- Matricule -->
                <div class="field col-12 md:col-6">
                    <label for="matricule">Matricule</label>
                    <InputText id="matricule" v-model="editedRow.identification.number" />
                </div>

                <!-- Nom -->
                <div class="field col-12 md:col-6">
                    <label for="nom">Nom</label>
                    <InputText id="nom" v-model="editedRow.person.lastname" />
                </div>

                <!-- Prénom -->
                <div class="field col-12 md:col-6">
                    <label for="prenom">Prénom</label>
                    <InputText id="prenom" v-model="editedRow.person.firstname" />
                </div>

                <!-- Sexe -->
                <div class="field col-12 md:col-6">
                    <GenderSelect
                        id="gender"
                        :value="editedRow.person.gender?.id"
                        label="FORM.LABELS.GENDER"
                        :required="true"
                        :onChange="
                            (value) => {
                                editedRow.person.gender = value;
                            }
                        "
                        :validationTrigger="false"
                    />
                </div>

                <!-- Date Naissance -->
                <div class="field col-12 md:col-6">
                    <label for="birthdate">Date de naissance</label>
                    <Calendar id="birthdate" v-model="editedRow.person.birthdate" dateFormat="yy-mm-dd" showIcon class="w-full" />
                </div>

                <!-- Lieu Naissance -->
                <div class="field col-12 md:col-6">
                    <label for="birthplace">Lieu de naissance</label>
                    <InputText id="birthplace" v-model="editedRow.person.birthplace" />
                </div>

                <!-- Etat Civil -->
                <div class="field col-12 md:col-6">
                    <MaritalStatusSelect
                        id="marital_status"
                        :value="editedRow.person.marital_status ? editedRow.person.marital_status.id : null"
                        label="FORM.LABELS.MARITAL_STATUS"
                        :onChange="
                            (value) => {
                                editedRow.person.marital_status = value;
                            }
                        "
                        :validationTrigger="false"
                    />
                </div>

                <!-- Employment Information Section -->
                <div class="field col-12">
                    <h3 class="text-lg font-semibold mb-3 mt-4">Informations professionnelles</h3>
                </div>

                <!-- Poste -->
                <div class="field col-12 md:col-6">
                    <label for="job">Poste <span class="text-danger">*</span></label>
                    <Dropdown id="job" v-model="editedRow.employment.job" :options="jobs" optionLabel="name" optionValue="id" filter class="w-full" />
                </div>

                <!-- Catégorie Professionnelle -->
                <div class="field col-12 md:col-6">
                    <label for="classification">Catégorie professionnelle <span class="text-danger">*</span></label>
                    <Dropdown id="classification" v-model="editedRow.employment.classification" :options="classifications" optionLabel="name" optionValue="id" filter class="w-full" />
                </div>

                <!-- Statut -->
                <div class="field col-12 md:col-6">
                    <label for="jobType">Statut</label>
                    <Dropdown id="jobType" v-model="editedRow.employment.job_type" :options="jobTypes" optionLabel="name" optionValue="id" filter class="w-full" />
                </div>

                <!-- Spécialité -->
                <div class="field col-12 md:col-6">
                    <label for="specialty">Spécialité</label>
                    <InputText id="specialty" v-model="editedRow.employment.specialty" />
                </div>

                <!-- Grade -->
                <div class="field col-12 md:col-6">
                    <GradeSelect
                        id="grade"
                        :value="editedRow.employment.grade"
                        label="TREE.GRADE"
                        :required="true"
                        :onChange="
                            (value) => {
                                editedRow.employment.grade = value.id;
                            }
                        "
                        :validationTrigger="false"
                    />
                </div>

                <!-- Echelon -->
                <div class="field col-12 md:col-6">
                    <label for="seniority">Échelon</label>
                    <InputNumber id="seniority" v-model="editedRow.employment.seniority" />
                </div>

                <!-- Ancien Poste -->
                <div class="field col-12 md:col-6">
                    <label for="previousJob">Ancien poste</label>
                    <InputText id="previousJob" v-model="editedRow.employment.previous_job" />
                </div>

                <!-- Position actuelle -->
                <div class="field col-12 md:col-6">
                    <label for="currentPosition">Position actuelle</label>
                    <InputText id="currentPosition" v-model="editedRow.employment.current_position" />
                </div>

                <!-- Dates Section -->
                <div class="field col-12">
                    <h3 class="text-lg font-semibold mb-3 mt-4">Dates</h3>
                </div>

                <!-- Date Intégration -->
                <div class="field col-12 md:col-6">
                    <label for="recruitmentDate">Date d'intégration</label>
                    <Calendar id="recruitmentDate" v-model="editedRow.person.recruitment_date" dateFormat="yy-mm-dd" showIcon class="w-full" />
                </div>

                <!-- Date Service -->
                <div class="field col-12 md:col-6">
                    <label for="startServiceDate">Date de service</label>
                    <Calendar id="startServiceDate" v-model="editedRow.employment.start_service_date" dateFormat="yy-mm-dd" showIcon class="w-full" />
                </div>
            </div>
        </div>

        <!-- Modal Footer -->
        <template #footer>
            <Button :label="$t('FORM.BUTTONS.CANCEL')" icon="pi pi-times" @click="close" class="p-button-text" />
            <Button :label="$t('FORM.BUTTONS.VALIDATE')" icon="pi pi-check" @click="() => saveEdit(this.editedRow)" autofocus />
        </template>
    </Dialog>
</template>

<style scoped>
.text-danger {
    color: #dc3545;
    font-weight: bold;
}
.has-error {
    font-size: 0.875rem;
}
</style>