<script setup>
import { ref, onMounted } from 'vue';
import { FilterMatchMode } from '@primevue/core/api';
import apiService from '@/service/ApiService';
import _AppCache from '../../../service/appCache';
import PyarmidPath from './PyarmidPath.vue';
const props = defineProps({
    currentPR: {
        type: Object,
        default: null
    },
    currentTR: {
        type: Object,
        default: null
    },
    currentHA: {
        type: Object,
        default: null
    },
    currentFacility: {
        type: Object,
        default: null
    },
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
const interval = ref([]);
const loading = ref(false);
const selectedRevenu = ref(['salaire_recu']);
const loadingUitls = ref(true);
const loadingUitlsError = ref(null);
const selectedCadres = ref([]);
const selectedClassifications = ref([]);
const selectedJobs = ref([]);

const validationError = ref(false);
const startDate = ref(new Date());
const endDate = ref(new Date());
const zsFilter = ref(false);
const reportUrl = ref(null);
const provinceType = ref('1');
const classifications = ref([]);
const loadingClassifications = ref(false);
const jobs = ref([]);
const loadingJobs = ref(false);
const cadres = ref([]);
const loadingCadres = ref(false);

const selectedOption = ref({
    name: 'Revenu total',
    code: 1
});
 
const filters2 = ref({
    location: {
        value: null,
        matchMode: FilterMatchMode.CONTAINS
    }
});
const products = ref([]);

onMounted(() => {
    startDate.value = getLastMonth(6, 1)[0];
    getClassifications();
    getJobs();
    getCadres();
});


const onclickGetReport = () => {
     currentNode.value = _AppCache.getCurrentNode();
    if (!currentNode.value) return false;
    if (loading.value) return;
    if (selectedRevenu.value.length == 0) {
        validationError.value = true;
        return false;
    }
    validationError.value = false;
    loading.value = true;

    reportUrl.value =
        '/reports/revenu_report?org_unit_id=' +
        currentNode.value +
        '&cadres_ids=' +
        encodeURIComponent(JSON.stringify(selectedCadres.value.map((x) => x.id))) +
        '&class_ids=' +
        encodeURIComponent(JSON.stringify(selectedClassifications.value.map((x) => x.id))) +
        '&jobs_ids=' +
        encodeURIComponent(JSON.stringify(selectedJobs.value.map((x) => x.id))) +
        '&report_type=' +
        selectedOption.value.code +
        '&start_date=' +
        startDate.value.toISOString().slice(0, 10) +
        '&end_date=' +
        endDate.value.toISOString().slice(0, 10) +
        '&assr=' +
        provinceType.value +
        '&select_option=' +
        encodeURIComponent(JSON.stringify(selectedRevenu.value)) +
        '&zs_filter=' +
        (zsFilter.value ? 1 : 0);

    apiService
        .get(reportUrl.value)
        .then((res) => {
            error.value = null;
            products.value = [];
            interval.value = res.data.intervals;
            products.value = res.data.report.data;
        })
        .catch((err) => {
            error.value = err;
        })
        .finally(() => {
            loading.value = false;
        });
};
const formatCurrency = (value) => {
    if (value == null) return 0;
    return value.toLocaleString('en-US');
};
 
const getCadres = (url = '/utils/cadres') => {
    loadingCadres.value = true;

    apiService
        .get(url)
        .then((res) => {
            cadres.value = [];
            // cadres.value.push(currentCadre.value);
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
    loadingJobs.value = true;

    apiService
        .get(url)
        .then((res) => {
            jobs.value = [];
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
    loadingClassifications.value = true;
    apiService
        .get(url)
        .then((res) => {
            classifications.value = [];
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
const getLastMonth = (q = 6, local = 0) => {
    var x = new Date();
    var y = new Date();
    y.setDate(1);
    y.setMonth(y.getMonth() - q);

    if (local != 0) return [y, x];
    else return [y.toLocaleDateString('fr'), x.toLocaleDateString('fr')];
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
    download(reportUrl.value + '&download=1' + '&title=' + exportFileName());
};
const downloadingFile = ref(false);
const download = (url) => {
    downloadingFile.value = true;
    apiService
        .get(url, {
            responseType: 'arraybuffer'
        })
        .then((res) => {
            let headerLine = res.headers['content-disposition'];
            let startFileNameIndex = headerLine.indexOf('"') + 1;
            let endFileNameIndex = headerLine.lastIndexOf('"');
            let filename = headerLine.substring(startFileNameIndex, endFileNameIndex);
            const link = document.createElement('a');
            link.href = window.URL.createObjectURL(new Blob([res.data]));
            console.log(link);
            link.setAttribute('download', filename);
            console.log(link);
            document.body.appendChild(link);
            link.click();
        })
        .catch((err) => {
            console.log(err);
            downloadingFile.value = false;
            alert('Impossible de télécharger...');
        })
        .finally(() => {
            downloadingFile.value = false;
        });
};

const currrentTreePosition = ref(null);
const updateReport = (node) => {
    currentNode.value = node;
    if (currrentTreePosition.value != exportFileName() || products.value.lenght == 0) onclickGetReport();
    currrentTreePosition.value = exportFileName();
};


defineExpose({
    updateReport
});
</script>
<template>
    <div style="margin-bottom: 10px;">
        <PyarmidPath :reload="onclickGetReport"/>
    </div>
    <div className="card">
        <h5>RAPPORT SUR LA MOTIVATION</h5>
        <hr />
        <div class="grid">
            <div class="col-6 sm:col-3 md:col-3 lg:col-3">
                <label for="startDate" class="">Debut:</label>
                <Calendar id="startDate" v-model="startDate" :show-icon="true" dateFormat="dd/mm/yy" class="p-inputtext-sm w-full" />
            </div>
            <div class="col-6 sm:col-3 md:col-3 lg:col-3">
                <label for="endDate" class="">Fin:</label>
                <Calendar v-model="endDate" :show-icon="true" dateFormat="dd/mm/yy" class="p-inputtext-sm w-full" />
            </div>
            <div class="col-6 sm:col-4 md:col-4 lg:col-3">
                <label for="selectedCadres" class="">Filtre(Catégories):</label>
                <InputGroup>
                    <MultiSelect id="selectedCadres" display="chip" filter :maxSelectedLabels="3" v-model="selectedCadres" :options="cadres" optionLabel="name" placeholder="Filtrer les catégories" class="p-input-sm" />
                    <Button icon="pi pi-refresh" :loading="loadingCadres" @click="getCadres()" title="Actualiser " />
                </InputGroup>
            </div>
            <div class="col-6 sm:col-4 md:col-4 lg:col-3">
                <label for="selectedJobs" class="">Filtre(Fonctions):</label>
                <InputGroup>
                    <MultiSelect id="selectedJobs" display="chip" filter :maxSelectedLabels="3" v-model="selectedJobs" :options="jobs" optionLabel="title" placeholder="Filtrer les fonctions" class="p-input-sm" />
                    <Button icon="pi pi-refresh" :loading="loadingJobs" @click="getJobs()" title="Actualiser " />
                </InputGroup>
            </div>
            <div class="col-6 sm:col-4 md:col-4 lg:col-3">
                <label for="selectedClassifications" class="">Filtre(Professions):</label>
                <InputGroup>
                    <MultiSelect id="selectedClassifications" display="chip" filter :maxSelectedLabels="3" v-model="selectedClassifications" :options="classifications" optionLabel="name" placeholder="Filtrer les profession" class="p-input-sm" />
                    <Button icon="pi pi-refresh" :loading="loadingClassifications" @click="getClassifications()" title="Actualiser " />
                </InputGroup>
            </div>

            <div class="col-6 sm:col-4 md:col-3 lg:col-2">
                <br />
                <label for="switch1">Filtrer les ZS</label>
                <InputSwitch v-model="zsFilter" @change="onclickGetReport()" inputId="switch1" class="ml-2" />
            </div>
        </div>
        <br />
        <div class="grid">
            <div class="col-12 md:col-8">
                <b>Revenus : </b>
                <div class="mt-2">
                    <span class="p-4">
                        <Checkbox v-model="selectedRevenu" inputId="ingredient1" name="salaire" value="salaire_recu" class="mr-2" />
                        <label for="ingredient1"> Salaire </label>
                    </span>
                    <span>
                        <Checkbox v-model="selectedRevenu" inputId="ingredient2" name="prime_risque" value="prime_risque" class="mr-2" />
                        <label for="ingredient2" class="mr-4"> Prime de risque </label>
                    </span>
                    <span>
                        <Checkbox v-model="selectedRevenu" inputId="ingredient3" name="prime_locale" value="prime_locale" class="mr-2" />
                        <label for="ingredient3" class="mr-4"> Prime local </label>
                    </span>
                    <span>
                        <Checkbox v-model="selectedRevenu" inputId="ingredient4" name="prime_ptf" value="prime_ptf" class="mr-2" />
                        <label for="ingredient4" class="mr-4"> Prime PTF </label>
                    </span>
                </div>
            </div>
            <div class="col-12 md:col-4 text-right">
                <Button @click="onclickGetReport()" icon="pi pi-refresh" :loading="loading" label="VISUALISER" class="p-button-primary p-button-sm" />
            </div>
        </div>

        <div>
            <div class="mt-4">
                <div v-if="products.length == 0 && loading">
                    <div v-if="loading" class="mt-4 pt-4">
                        <ScaleLoader :color="'#3B82F6'"></ScaleLoader>
                        <p class="text-center">chargement ...</p>
                    </div>
                </div>
                <div v-if="error != null && !loading" class="row">
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

                <div class="text-danger" v-if="!loadingUitls && loadingUitlsError != null">
                    <Message severity="error">Echec de connexion... <a class="link" @click="getReportUtils()">Réessayer </a></Message>
                </div>
                <div class="text-danger" v-if="validationError">
                    <Message severity="error">Erreur, veuillez sélectionner le revenu (salaire, prime de risque, prime locale, ou prime PTF) à affichager ... </Message>
                </div>
                <div class="text-info" v-if="products.length == 0 && error == null && !loading">
                    <Message severity="info">Aucune donnée, liste vide!! </Message>
                </div>
                <DataTable
                    v-if="products.length > 0 && error == null"
                    :value="products"
                    stripedRows
                    class="p-datatable-sm revenu-table"
                    :paginator="true"
                    :rows="30"
                    responsiveLayout="scroll"
                    :scrollable="true"
                    dataKey="id"
                    v-model:filters="filters2"
                    filterDisplay="menu"
                    scrollHeight="600px"
                    :loading="loading"
                    :globalFilterFields="['location']"
                    showGridlines
                >
                    <template #header>
                        <div class="grid">
                            <div class="sm:col-6">
                                <IconField iconPosition="left">
                                    <InputIcon class="pi pi-search"> </InputIcon>
                                    <InputText v-model="filters2['location'].value" placeholder="Rechercher ..." />
                                </IconField>
                            </div>
                            <div class="sm:col-6 text-right">
                                <Button @click="downloadExcelFile()" label="EXCEL" :loading="downloadingFile" icon="pi pi-download" class="p-button-success p-button-sm p-button-outlined p-button ml-2" iconPos="right" />
                            </div>
                        </div>
                    </template>
                    <ColumnGroup type="header">
                        <Row>
                            <Column header="LIEU" :rowspan="2" headerStyle="width: 200px;" sortable />
                            <Column header="EFFECTIF" :rowspan="2" headerStyle=" text-align: right;" sortable />
                            <Column header="EF.ACTIF" :rowspan="2" headerStyle=" text-align: right;" sortable />
                            <Column v-for="col of interval" :key="col.key" :header="col.local_abb" :colspan="2" headerStyle=" text-align: center;"></Column>
                            <Column header="MOYENNE" :rowspan="2" field="moyenne" sortable />
                            <Column header="TOTAL" :rowspan="2" field="total" sortable />
                        </Row>
                        <Row>
                            <template v-for="(col, index) in interval" :key="index">
                                <Column header="MONTANT" :field="col.key" :title="'MONTANT'" sortable></Column>
                                <Column :header="'RAP.'" :field="col.effectif" title="RAPPORTS" sortable></Column>
                            </template>
                        </Row>
                    </ColumnGroup>
                    <Column :sortable="true" field="location" header="LIEU" class="fosa_col" style="min-width: 200px">
                        <template #body="{ data }">
                            <div class="">
                                <b>{{ data.location }}</b>
                            </div>
                        </template>
                    </Column>
                    <Column :sortable="true" field="effectif" header="EF. GN" class="f-txt-right">
                        <template #body="{ data }">
                            <div class="text-warning">
                                <b>{{ data.effectif }}</b>
                            </div>
                        </template>
                    </Column>
                    <Column :sortable="true" field="effectif_actif" header="EF. ACTIF" class="f-txt-right">
                        <template #body="{ data }">
                            <div class="text-success">
                                <b>{{ data.effectif_actif }}</b>
                            </div>
                        </template>
                    </Column>
                    <template v-for="col of interval" :key="col.key">
                        <Column :sortable="true" :field="col.key" class="f-txt-right">
                            <template #body="{ data }">
                                {{ formatCurrency(data[col.key]) }}
                            </template>
                        </Column>
                        <Column :field="col.effectif" class="f-txt-right text-blue-500"></Column>
                    </template>
                    <Column :sortable="true" field="moyenne" header="MOYENNE" class="f-txt-right">
                        <template #body="{ data }">
                            <b>{{ formatCurrency(data.moyenne) }} </b>
                        </template>
                    </Column>
                    <Column :sortable="true" field="total" header="TOTAL" class="text-success f-txt-right">
                        <template #body="{ data }">
                            <b> {{ formatCurrency(data.total) }}</b>
                        </template>
                    </Column>
                </DataTable>
            </div>
        </div>
    </div>
</template>
