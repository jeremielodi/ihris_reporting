<script setup>
import { ref, onMounted } from 'vue';
import apiService from '@/service/ApiService';
import xlsx from 'json-as-xlsx';
import { FilterMatchMode } from '@primevue/core/api';
import _AppCache from '../../../service/appCache';
import PyarmidPath from './PyarmidPath.vue';
const props = defineProps({
    
    title: {
        type: String,
        default: null
    },
    submenu_position: {
        type: Number,
        default: 0
    }
});

const currentNode = ref(null);
const error = ref(null);
const loadingReport = ref(false);
const report = ref([]);
const jobs = ref([]);
const cadres = ref([]);
const loadingCadres = ref(false);
const loadingJobs = ref(false);
const currentJob = ref({ id: '0', title: 'TOUTES LES FONCTIONS' });
const currentCadre = ref({ id: '0', name: 'TOUTES LES CATEGORIES' });

const currentClassification = ref({ id: '0', name: 'TOUTES LES PROFESSIONS' });
const loadingClassifications = ref(false);
const classifications = ref([]);

const zsFilter = ref(false);

const filters2 = ref({
    fosa: { value: null, matchMode: FilterMatchMode.CONTAINS }
});

onMounted(() => {
    onclickGetReport();
    setTimeout(() => {
        getCadres();
        getJobs();
        getClassifications();
    }, 100);
});

const onclickGetReport = () => {
    if (loadingReport.value) return;

    currentNode.value = _AppCache.getCurrentNode();
    if (!currentNode.value) return;
    let url = `/reports/situation_salaire_prime?org_unit_id=${currentNode.value}&cadre_id${currentCadre.value.id}&job_id=${currentJob.value.id}&zs_filter=${zsFilter.value ? 1 : 0}`;

    loadingReport.value = true;
    apiService
        .get(url)
        .then((res) => {
            error.value = null;
            var y = 0;
            report.value = [];
            console.log(res);
            res.data.report.data.forEach((elt) => {
                var line = {
                    id: (y += 1),
                    fosa: elt.location,
                    effectif: elt.effectif,
                    has_salary: elt.salaire,
                    has_not_salary: (elt.effectif || 0) - (elt.salaire || 0),
                    has_prime: elt.prime,
                    has_not_prime: (elt.effectif || 0) - (elt.prime || 0),
                    has_salary_or_prime: elt.salaire_ou_prime,
                    has_salary_and_prime: elt.salaire_et_prime,
                    no_salary_no_prime: elt.in_salaire_in_prime
                };
                report.value.push(line);
            });
        })
        .catch((err) => {
            error.value = err;
            console.log(err);
        })
        .finally(() => {
            loadingReport.value = false;
        });
};

const getCadres = (url = '/utils/cadres') => {
    if(loadingCadres.value) return;
    loadingCadres.value = true;

    apiService
        .get(url)
        .then((res) => {
            cadres.value = [];
            cadres.value.push(currentCadre.value);
            cadres.value.push(...res.data);
        })
        .catch((err) => {
            console.log(err);
        })
        .finally(() => {
            loadingCadres.value = false;
        });
};

const getJobs = (url = '/utils/jobs') => {
    if(loadingJobs.value) return;
    loadingJobs.value = true;

    apiService
        .get(url)
        .then((res) => {
            jobs.value = [];
            jobs.value.push(currentJob.value);
            jobs.value.push(...res.data);
            loadingJobs.value = false;
        })
        .catch((err) => {
            console.log(err);
        })
        .finally(() => {
            console.log('end');
            loadingJobs.value = false;
        });
};

const getClassifications = (url = '/utils/classifications') => {
    if(loadingClassifications.value ) return;
    loadingClassifications.value = true;

    apiService
        .get(url)
        .then((res) => {
            classifications.value = [];
            classifications.value.push(currentClassification.value);
            classifications.value.push(...res.data);
            loadingClassifications.value = false;
        })
        .catch((err) => {
            console.log(err);
        })
        .finally(() => {
            console.log('end');
            loadingClassifications.value = false;
        });
};
const exportFileName = () => {
    let name = '';
    if (props.currentFacility) name += ' - ' + props.currentFacility.label;
    if (props.currentHA) name += ' - ' + props.currentHA.label;
    if (props.currentTR) name += ' - ' + props.currentTR.label;
    if (props.currentPR) name += ' - ' + props.currentPR.label;
    if (name == '') name = 'NATIONAL';
    return name.toUpperCase();
};

const downloadExcelFile = () => {
    let settings = {
        fileName: 'SITUATION SALIRE ET PRIME - ' + exportFileName() + '- ' + new Date().toLocaleString(),
        writeMode: 'writeFile',
        RTL: false
    };
    let data = [
        {
            sheet: 'SITUATION SALAIRE ET PRIME  ',
            columns: [
                { label: 'No', value: 'id' },
                { label: 'LIEUX', value: 'fosa' },
                { label: 'EFFECTIF', value: 'effectif' },
                { label: 'SALAIRE', value: 'has_salary' },
                { label: 'SANS SALAIRE', value: 'has_salary' },
                { label: 'PRIME', value: 'has_prime' },
                { label: 'SANS PRIME', value: 'has_not_prime' },
                { label: 'SALAIRE OU PRIME', value: 'has_salary_or_prime' },
                { label: 'SALAIRE ET PRIME', value: 'has_salary_and_prime' },
                { label: 'NI SALAIRE NI PRIME', value: 'no_salary_no_prime' }
            ],
            content: report.value
        }
    ];

    xlsx(data, settings);
};

const currrentTreePosition = ref(null);

const updateReport = (orgUnitId) => {
    currentNode.value = orgUnitId;
    if (currrentTreePosition.value != exportFileName() || report.value.lenght == 0) onclickGetReport();
    currrentTreePosition.value = exportFileName();
};

defineExpose({
    updateReport
});
</script>
<template>
    <div>
        <PyarmidPath :reload="onclickGetReport"/>
   
    <div className="card">
        <h5>SITUATION SALAIRE & PRIMES</h5>
        <hr />
        <div>
            <div class="grid">
                <div class="col-12 sm:col-8 pb-0">
                    <div class="grid">
                        <div class="col-12 md:col-4">
                            <InputGroup>
                                <Dropdown class="p-inputtext-sm" :disabled="loadingJobs" :filter="true" v-model="currentJob" :options="jobs" optionLabel="title" placeholder="FILTRER PAR FONCTION" />
                                <Button icon="pi pi-refresh" :loading="loadingJobs" @click="getJobs()" title="Actualiser la liste" />
                            </InputGroup>
                        </div>
                        <div class="col-12 md:col-4">
                            <InputGroup>
                                <Dropdown class="p-inputtext-sm" :disabled="loadingCadres" :filter="true" v-model="currentCadre" :options="cadres" optionLabel="name" placeholder="FILTRER PAR CATEGORIE" />
                                <Button icon="pi pi-refresh" :loading="loadingCadres" @click="getCadres()" title="Actualiser la liste" />
                            </InputGroup>
                        </div>
                        <div class="col-12 md:col-4">
                            <InputGroup>
                                <Dropdown class="p-inputtext-sm" :disabled="loadingClassifications" :filter="true" v-model="currentClassification" :options="classifications" optionLabel="name" placeholder="FILTRER PAR PROFESSION" />
                                <Button icon="pi pi-refresh" :loading="loadingClassifications" @click="getClassifications()" title="Actualiser la liste" />
                            </InputGroup>
                        </div>
                    </div>
                </div>
                <div class="col-12 sm:col-4 text-right pb-0">
                    <label for="switch1">Filtrer les ZS</label>
                    <InputSwitch v-model="zsFilter" @change="onclickGetReport()" inputId="switch1" class="ml-2" />
                    <Button @click="onclickGetReport()" :loading="loadingReport" icon="pi pi-refresh" label="VISUALISER" class="p-button-primary p-button-sm ml-3" />
                </div>
            </div>

            <div class="mt-4">
                <div v-if="error != null && !loadingReport" class="row">
                    <div class="col-sm-3"></div>
                    <div class="col-sm-6 text-center m-4">
                        <div class="alert alert-danger text-center" role="alert">
                            <h4>Echec de connexion</h4>
                            <p>{{ error }}</p>
                            <hr />
                            <Button @click="onclickGetReport()" label="Réessayer" class="p-button-danger p-button-sm" />
                        </div>
                    </div>
                </div>
                <DataTable
                    v-if="error == null"
                    :value="report"
                    stripedRows
                    class="p-datatable-sm salaire_prime_table"
                    :paginator="true"
                    :rows="16"
                    responsiveLayout="scroll"
                    :scrollable="true"
                    dataKey="id"
                    v-model:filters="filters2"
                    filterDisplay="menu"
                    :loading="loadingReport"
                    :globalFilterFields="['fosa']"
                >
                    <template #header>
                        <div class="grid">
                            <div class="col-6">
                                <IconField iconPosition="left">
                                    <InputIcon class="pi pi-search"> </InputIcon>
                                    <InputText v-model="filters2['fosa'].value" class="p-inputtext-sm" placeholder="Rechercher ..." />
                                </IconField>
                            </div>
                            <div class="col-6 text-right">
                                <Button @click="downloadExcelFile()" label="EXCEL" icon="pi pi-file-excel" class="p-button-success p-button-sm p-button-outlined p-button ml-2" iconPos="right" />
                            </div>
                        </div>
                    </template>
                    <Column :sortable="true" field="fosa" style="min-width: 210px" header="LIEUX" class="fosa_col font-semibold"></Column>
                    <Column :sortable="true" field="effectif" header="EFFECTIF" class="font-semibold"></Column>
                    <Column :sortable="true" field="has_salary" header="SALAIRE" class="text-success"></Column>
                    <Column :sortable="true" field="has_not_salary" header="SANS SALAIRE" class="text-danger"></Column>
                    <Column :sortable="true" field="has_prime" header="PRIME" class="text-success"></Column>
                    <Column :sortable="true" field="has_not_prime" header="SANS PRIME" class="text-danger"></Column>
                    <Column :sortable="true" field="has_salary_or_prime" header="SALAIRE OU PRIME" class="text-warning"></Column>
                    <Column :sortable="true" field="has_salary_and_prime" header="SALAIRE ET PRIME" class="text-success"></Column>
                    <Column :sortable="true" field="no_salary_no_prime" header="NI SALAIRE NI PRIME" class="font-semibold text-red-300"></Column>
                </DataTable>
            </div>
        </div>
    </div>
 </div>
</template>
