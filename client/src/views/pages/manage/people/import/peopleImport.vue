<script>
import * as XLSX from 'xlsx';
import { defineComponent } from 'vue';
import cadreService from '../../cadre/cadre.service';
import jobTypeService from '../../job_type/job_type.service';
import classificationService from '../../classification/classification.service';
import MaritalStatusService from '../../marital_status/marital_status.service';
import ListSkeleton from './skeleton.vue';
import EditModal from './modal.vue';
import PyramidSelect from '@/components/pyramidSelect/pyramidSelect.vue';
import PeopleService from '../people.service';

export default defineComponent({
    name: 'ExcelImporter',
    data() {
        return {
            rows: [],
            orgUnitId: null,
            loading: true,
            showOnlyErrors: false,
            showEditModal: false,
            globalFilter: '',
            unknownClassifications: [],
            jobs: [],
            classifications: [],
            selectedRow: {},
            jobTypes: [],
            genders: [],
            maritalStatusList: [],
            maritalStatusListMap: {},
            maps: {
                jobs: null,
                classification: null,
                jobTypes: null
            }
        };
    },
    components: {
        ListSkeleton,
        EditModal,
        PyramidSelect
    },
    computed: {
        filteredRows() {
            let r = this.rows;

            if (this.showOnlyErrors) {
                r = r.filter((x) => x.errors.length > 0);
            }

            if (this.globalFilter) {
                const f = this.globalFilter.toLowerCase();
                r = r.filter((x) => (x.person.lastname + ' ' + x.person.firstname).toLowerCase().includes(f));
            }

            return r;
        }
    },

    created() {
        this.init();
    },

    methods: {
        async init() {
            this.loading = true;
            try {
                if (!this.jobs.length) this.jobs = await cadreService.read();
                if (!this.classifications.length) this.classifications = await classificationService.read();
                if (!this.jobTypes.length) this.jobTypes = await jobTypeService.read(); // ✅ NEW
                this.maritalStatusList = await MaritalStatusService.read();
                this.maritalStatusList.forEach((m) => (this.maritalStatusListMap[m.name] = m));
                this.maps.jobs = this.buildIndex(this.jobs, 'name');
                this.maps.classification = this.buildIndex(this.classifications, 'name');
                this.maps.jobTypes = this.buildIndex(this.jobTypes, 'name'); // ✅ NEW
            } finally {
                this.loading = false;
            }
        },
        async submit() {
            try {
                this.loading = true;

                // 🔹 Convert Excel date → YYYY-MM-DD
                const excelToDate = (serial) => {
                    if (!serial) return null;

                    const excelEpoch = new Date(Date.UTC(1899, 11, 30));
                    const date = new Date(excelEpoch.getTime() + serial * 86400000);

                    return date.toISOString().split('T')[0];
                };

                // 🔹 Normalize ISO date → YYYY-MM-DD
                const formatISODate = (date) => {
                    if (!date) return null;
                    return new Date(date).toISOString().split('T')[0];
                };

                // 🔹 Build payload array
                const payload = this.rows.map((row) => {
                    return {
                        id: row.id,

                        person: {
                            firstname: row.person?.firstname?.trim(),
                            lastname: row.person?.lastname?.trim(),

                            gender: row.person?.gender?.id || null,
                            marital_status: row.person?.marital_status?.id || null,

                            birthplace: row.person?.birthplace || null,

                            // ✅ prioritize structured date, fallback to raw Excel
                            birthdate: row.person?.birthdate ? formatISODate(row.person.birthdate) : excelToDate(row.raw?.['Date de Naissance']),

                            degree: row.person?.degree || null
                        },

                        identification: {
                            number: row.identification?.number || row.raw?.Matricule || null
                        },

                        employment: {
                            job: row.employment?.job || null,
                            classification: row.employment?.classification || null,
                            job_type: row.employment?.job_type || null,
                            employment_type: row.employment?.employment_type || null,

                            grade: row.employment?.grade || null,
                            seniority: Number(row.employment?.seniority || 0),

                            // ✅ Dates
                            employment_date: row.employment?.employment_date ? formatISODate(row.employment.employment_date) : excelToDate(row.raw?.["Date d'intégration"]),

                            start_service_date: row.employment?.start_service_date ? formatISODate(row.employment.start_service_date) : excelToDate(row.raw?.['Date de prise de service']),

                            first_service_date: row.employment?.first_service_date ? formatISODate(row.employment.first_service_date) : excelToDate(row.raw?.['Date 1ère Prise de Service']),

                            previous_job: row.employment?.previous_job || null,
                            current_position: row.employment?.current_position || null
                        }
                    };
                });

                // 🔹 Remove rows with errors (VERY IMPORTANT)
                const cleanPayload = payload.filter((_, i) => {
                    return !this.rows[i].errors || this.rows[i].errors.length === 0;
                });

                console.log('FINAL PAYLOAD:', cleanPayload);

                PeopleService.importList(this.orgUnitId, cleanPayload);

                this.$toast.add({
                    severity: 'success',
                    summary: 'Succès',
                    detail: `${cleanPayload.length} enregistrements importés`,
                    life: 3000
                });
            } catch (error) {
                console.error(error);

                this.$toast.add({
                    severity: 'error',
                    summary: 'Erreur',
                    detail: error?.response?.data?.message || 'Erreur import',
                    life: 4000
                });
            } finally {
                this.loading = false;
            }
        },
        formatMaritalStatus(value) {
            if (!value) return null;
            return this.maritalStatusListMap[value];
        },
        formatGender(value) {
            if (!value) return null;
            const _value = `${value}`.toLowerCase();
            if (['m', 'male', 'masculin', 'homme', 'h'].includes(_value)) {
                return {
                    id: 'gender|M',
                    name: 'Masculin'
                };
            }

            if (['f', 'female', 'feminin', 'femme'].includes(_value)) {
                return {
                    id: 'gender|F',
                    name: 'Feminin'
                };
            }
        },

        excelDateToDate(v) {
            if (!v) return null;

            if (typeof v === 'string') {
                const d = new Date(v);
                return isNaN(d.getTime()) ? null : d;
            }

            if (typeof v === 'number') {
                const d = new Date((v - 25569) * 86400 * 1000);
                return isNaN(d.getTime()) ? null : d;
            }

            return null;
        },

        toYMD(value) {
            if (!value) return null;

            // ✅ Case 1: already a Date object
            if (value instanceof Date && !isNaN(value.getTime())) {
                return value.toISOString().slice(0, 10);
            }

            // ✅ Case 2: ISO string
            if (typeof value === 'string') {
                const d = new Date(value);
                if (!isNaN(d.getTime())) {
                    return d.toISOString().slice(0, 10);
                }
            }

            // ✅ Case 3: Excel serial number
            if (typeof value === 'number') {
                const excelEpoch = new Date(Date.UTC(1899, 11, 30));
                const d = new Date(excelEpoch.getTime() + value * 86400000);

                if (!isNaN(d.getTime())) {
                    return d.toISOString().slice(0, 10);
                }
            }

            return null;
        },
        // ===== UTILS =====

        excelDateToYMD(v) {
            if (!v) return null;
            if (typeof v === 'string') return v;
            const d = new Date((v - 25569) * 86400 * 1000);
            return isNaN(d) ? null : d.toISOString().slice(0, 10);
        },

        formateNoms(k) {
            if (!k) return null;
            return k
                .normalize('NFD')
                .replace(/[\u0300-\u036f]/g, '')
                .toUpperCase()
                .trim();
        },

        buildIndex(list, key) {
            const map = new Map();
            list.forEach((i) => i[key] && map.set(i[key].trim(), i.id));
            return map;
        },

        getIdSafe(map, value, unknownList = null) {
            if (!value) return null;
            const v = value.trim();
            const id = map.get(v);

            if (!id && unknownList && !unknownList.includes(v)) {
                unknownList.push(v);
            }

            return id || null;
        },
        getLabelById(list, id) {
            const item = list.find((i) => i.id === id);
            return item ? item.name : null;
        },
        // Methods
        openEditModal(row) {
            // Create a deep copy to avoid modifying the original until save
            this.selectedRow = row.data;
            if (['M', 'F'].includes(this.selectedRow.person.gender)) {
                this.selectedRow.person.gender = `gender|${this.selectedRow.person.gender}`;
            }
            this.showEditModal = true;
        },
        closeEditModal() {
            this.showEditModal = false;
            this.selectedRow = null;
        },
        saveEdit(editedRow) {
            // Find and update the original row in filteredRows
            const index = this.rows.findIndex((row) => row.id === editedRow.id);
            if (index !== -1) {
                this.rows[index] = editedRow;
            }
            // Close modal
            this.closeEditModal();
            this.refreshErrors();
            // Optional: Show success message
            // You can add a toast notification here
        },
        // ===== IMPORT =====
        handleFile(e) {
            const file = e.files[0];
            if (!file) return;

            this.loading = true;

            const reader = new FileReader();
            reader.onload = (evt) => {
                try {
                    const wb = XLSX.read(evt.target.result, { type: 'binary' });
                    const sheet = wb.Sheets[wb.SheetNames[0]];
                    const data = XLSX.utils.sheet_to_json(sheet);

                    this.rows = data.map((r, i) => this.transformRow(r, i));
                } finally {
                    this.loading = false;
                }
            };

            reader.readAsBinaryString(file);
        },

        // ===== TRANSFORM =====

        transformRow(row, index) {
            const id = `person|${index + 1}`;

            let nom = row['Nom & Prénom'] || '';
            const parts = nom.split(' ');

            const job_id = this.getIdSafe(this.maps.jobs, row['Poste']);
            const classification_id = this.getIdSafe(this.maps.classification, row['Catégorie Professionnelle'], this.unknownClassifications);

            const job_type_id = this.getIdSafe(this.maps.jobTypes, row['Statut']); // ✅ NEW

            let niveau_etude = null;
            if (row['Catégorie'] && row['Echelle']) {
                niveau_etude = `${row['Catégorie']}${row['Echelle']}`.replace('-', '');
            }

            return {
                id,

                person: {
                    lastname: this.formateNoms(parts[0] || ''),
                    firstname: this.formateNoms(parts.slice(1).join(' ')),
                    gender: this.formatGender(row['Sexe']),
                    birthdate: this.excelDateToDate(row['Date de Naissance']),
                    recruitment_date: this.excelDateToDate(row["Date d'Intégration"]),
                    birthplace: row['Lieu de Naissance'],
                    marital_status: this.formatMaritalStatus(row['Etat Civil']),
                    degree: niveau_etude
                },

                identification: {
                    number: row['Matricule']
                },

                employment: {
                    grade: row['Grade'],
                    job: job_id,
                    classification: classification_id,

                    job_type: job_type_id, // ✅ UPDATED
                    employment_type: job_type_id, // ✅ SAME AS NODE

                    seniority: row['Echelon'],
                    birthdate: this.excelDateToDate(row['Date de Naissance']),
                    employment_date: this.excelDateToDate(row["Date d'affectation"]),
                    start_service_date: this.excelDateToDate(row['Date de prise de service']),
                    first_service_date: this.excelDateToDate(row['Date 1ère Prise de Service']),

                    specialty: row['Spécialité'],
                    previous_job: row['Ancien Poste'],
                    current_position: row['Position actuelle']
                },

                errors: [!job_id ? 'job' : null, !classification_id ? 'classification' : null].filter(Boolean),

                raw: row
            };
        },

        getSeverity(row) {
            return row.errors.length ? 'danger' : 'success';
        },

        refreshErrors() {
            this.rows.forEach((r) => {
                r.errors = [!r.employment.job ? 'job' : null, !r.employment.classification ? 'classification' : null].filter(Boolean);
            });
        },

        exportJSON() {
            const blob = new Blob([JSON.stringify(this.rows, null, 2)]);
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = 'import.json';
            a.click();
        }
    }
});
</script>

<template>
    <div class="card manage-containe" style="height: 90vh">
        <h4>Importation des agents dans le système</h4>
        <div class="flex gap-3 mb-3 align-items-center">
            <div style="padding-right: 10px">
                <FileUpload mode="basic" @select="handleFile" :chooseLabel="$t('FORM.LABELS.CHOOSE_FILE')" customUpload auto severity="secondary" class="p-button-outlined" />
            </div>

            <PyramidSelect
                        id="orgUnitId"
                        :value="{ key: this.orgUnitId }"
                        label=""
                        :hideLabel="true"
                        :required="true"
                        :onChange="
                            (value) => {
                                this.orgUnitId = value.key;
                            }
                        "
                        :validationTrigger="formSubmitted"
            />

            <InputText v-model="globalFilter" :placeholder="$t('FORM.BUTTONS.SEARCH')" />
            <div v-if="filteredRows.filter((data) => data.errors.length).length"><Checkbox v-model="showOnlyErrors" binary /> <span>Erreurs</span></div>
            <button v-if="this.orgUnitId && filteredRows.length > 0 && !filteredRows.filter((data) => data.errors.length).length" @click="submit" class="p-button p-component p-button-primary" style="margin-left: 10px">
                <span class="p-button-label">{{ $t('FORM.BUTTONS.SUBMIT') }}</span>
            </button>
        </div>

        <!-- Actual Data Table -->
        <DataTable v-if="!loading" :value="filteredRows" scrollable showGridlines stripedRows resizableColumns scrollHeight="600px" selectionMode="single" v-model:selection="selectedRow" @row-select="openEditModal" dataKey="id">
            <!-- INDEX -->
            <Column header="#" frozen>
                <template #body="{ index }">{{ index + 1 }}</template>
            </Column>

            <!-- STATUS -->
            <Column header="" frozen>
                <template #body="{ data }">
                    <Tag :severity="getSeverity(data)" :value="data.errors.length ? $t('FORM.LABELS.ERROR') : 'OK'" style="cursor: pointer" @click="openEditModal({ data })" />
                </template>
            </Column>

            <!-- NOM -->
            <Column header="Nom & Prénom" frozen>
                <template #body="{ data }">
                    <span style="cursor: pointer" @click="openEditModal({ data })"> {{ data.person.lastname }} {{ data.person.firstname }} </span>
                </template>
            </Column>

            <!-- MATRICULE -->
            <Column header="Matricule">
                <template #body="{ data }">
                    <span style="cursor: pointer" @click="openEditModal({ data })">
                        {{ data.identification.number }}
                    </span>
                </template>
            </Column>

            <!-- SEXE -->
            <Column header="Sexe">
                <template #body="{ data }">
                    <span style="cursor: pointer" @click="openEditModal({ data })">
                        {{ data.person.gender ? data.person.gender.name : '' }}
                    </span>
                </template>
            </Column>

            <!-- DATE NAISSANCE -->
            <Column header="Date Naissance">
                <template #body="{ data }">
                    <span style="cursor: pointer" @click="openEditModal({ data })">
                        {{ toYMD(data.person.birthdate) }}
                    </span>
                </template>
            </Column>

            <!-- LIEU -->
            <Column header="Lieu Naissance">
                <template #body="{ data }">
                    <span style="cursor: pointer" @click="openEditModal({ data })">
                        {{ data.person.birthplace }}
                    </span>
                </template>
            </Column>

            <!-- ETAT CIVIL -->
            <Column header="Etat Civil">
                <template #body="{ data }">
                    <span style="cursor: pointer" @click="openEditModal({ data })">
                        {{ data.person.marital_status ? data.person.marital_status.name : '' }}
                    </span>
                </template>
            </Column>

            <!-- POSTE -->
            <Column header="Poste">
                <template #body="{ data }">
                    <span :class="!data.employment.job ? 'text-red-500 font-bold' : ''" style="cursor: pointer" @click="openEditModal({ data })">
                        {{ getLabelById(jobs, data.employment.job) || 'INCONNU' }}
                    </span>
                </template>
            </Column>

            <!-- CLASSIFICATION -->
            <Column header="Catégorie Professionnelle">
                <template #body="{ data }">
                    <span :class="!data.employment.classification ? 'text-red-500 font-bold' : ''" style="cursor: pointer" @click="openEditModal({ data })">
                        {{ getLabelById(classifications, data.employment.classification) || 'INCONNUE' }}
                    </span>
                </template>
            </Column>

            <!-- JOB TYPE -->
            <Column header="Statut">
                <template #body="{ data }">
                    <span :class="!data.employment.job_type ? 'text-red-500 font-bold' : ''" style="cursor: pointer" @click="openEditModal({ data })">
                        {{ getLabelById(jobTypes, data.employment.job_type) || 'INCONNU' }}
                    </span>
                </template>
            </Column>

            <!-- SPECIALITE -->
            <Column header="Spécialité">
                <template #body="{ data }">
                    <span style="cursor: pointer" @click="openEditModal({ data })">
                        {{ data.employment.specialty }}
                    </span>
                </template>
            </Column>

            <!-- GRADE -->
            <Column header="Grade">
                <template #body="{ data }">
                    <span style="cursor: pointer" @click="openEditModal({ data })">
                        {{ data.employment.grade }}
                    </span>
                </template>
            </Column>

            <!-- ECHELON -->
            <Column header="Echelon">
                <template #body="{ data }">
                    <span style="cursor: pointer" @click="openEditModal({ data })">
                        {{ data.employment.seniority }}
                    </span>
                </template>
            </Column>

            <!-- ANCIEN POSTE -->
            <Column header="Ancien Poste">
                <template #body="{ data }">
                    <span style="cursor: pointer" @click="openEditModal({ data })">
                        {{ data.employment.previous_job }}
                    </span>
                </template>
            </Column>

            <!-- POSITION -->
            <Column header="Position actuelle">
                <template #body="{ data }">
                    <span style="cursor: pointer" @click="openEditModal({ data })">
                        {{ data.employment.current_position }}
                    </span>
                </template>
            </Column>

            <!-- DATE INTEGRATION -->
            <Column header="Date Intégration">
                <template #body="{ data }">
                    <span style="cursor: pointer" @click="openEditModal({ data })">
                        {{ toYMD(data.person.recruitment_date) }}
                    </span>
                </template>
            </Column>

            <!-- DATE SERVICE -->
            <Column header="Date Service">
                <template #body="{ data }">
                    <span style="cursor: pointer" @click="openEditModal({ data })">
                        {{ toYMD(data.employment.start_service_date) }}
                    </span>
                </template>
            </Column>
        </DataTable>

        <!-- Loading Skeleton -->
        <template v-else>
            <ListSkeleton />
        </template>

        <EditModal :display="showEditModal" :saveEdit="saveEdit" :selectedRow="selectedRow" :close="closeEditModal" :jobs="jobs" :jobTypes="jobTypes" :classifications="classifications" />
    </div>
</template>
