<script setup>
import { ref, onMounted } from 'vue';
import { FilterMatchMode } from '@primevue/core/api';
import apiService from '@/service/ApiService';
import xlsx from 'json-as-xlsx';
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

const error = ref(null);
const studentError = ref(null);
const interval = ref([]);
const startDate = ref(new Date());
const endDate = ref(new Date());
const zsFilter = ref(false);
const reportUrl = ref(null);
const provinceType = ref(1);
const selectedCategory = ref({ name: 'Mois', code: 1 });
const selectionInterval = ref(3);
const loading = ref(false);
const detaDialogDisplay = ref(false);
const reportLine = ref({});
const students = ref([]);
const loadingStudents = ref(false);
const reportCategory = ref([
    { code: '1', name: 'Toutes les catégories' },
    { code: 'training_course_category|1', name: 'Formation en data manager et en anglais' },
    { code: 'training_course_category|10', name: 'Formation spécifique des acteurs de santé communautaire' },
    { code: 'training_course_category|2', name: 'Formation en management des SSP des ECZS' },
    { code: 'training_course_category|3', name: 'Formation clinique des prestataires (training clinique)' },
    { code: 'training_course_category|4', name: 'Formation des cliniciens spécialistes' },
    { code: 'training_course_category|5', name: 'Formation sur le paquet SRMNEA' },
    { code: 'training_course_category|6', name: 'Formation en eau, hygiène & assainissement (EHA/WASH),gestion spécifique des déchets biomédicaux' },
    { code: 'training_course_category|7', name: 'Formation en communication pour la promotion de la santé' },
    { code: 'training_course_category|8', name: 'Formation sur la lutte contre la maladie' },
    { code: 'training_course_category|9', name: 'Formation en logistique (maintenance y compris)' }
]);
const filters2 = ref({
    name: { value: null, matchMode: FilterMatchMode.CONTAINS },
    firstname: { value: null, matchMode: FilterMatchMode.CONTAINS },
    surname: { value: null, matchMode: FilterMatchMode.CONTAINS },
    othername: { value: null, matchMode: FilterMatchMode.CONTAINS }
});

const filters = ref({
    firstname: { value: null, matchMode: FilterMatchMode.CONTAINS },
    surname: { value: null, matchMode: FilterMatchMode.CONTAINS },
    othername: { value: null, matchMode: FilterMatchMode.CONTAINS },
    id_num: { value: null, matchMode: FilterMatchMode.CONTAINS },
    health_area: { value: null, matchMode: FilterMatchMode.CONTAINS },
    facility: { value: null, matchMode: FilterMatchMode.CONTAINS }
});

const data = ref([]);
const personcategories = ref([]);
const categoryChartData = ref(null);
const genderChartData = ref(null);
const idnumChartData = ref(null);
const delayed = ref(null);
const training_course_details_url = ref('');
const lightOptions = ref({
    plugins: {
        legend: {
            labels: {
                color: '#blue'
            }
        }
    }
});
onMounted(() => {
    startDate.value = getLastMonth(30, 1)[0];
    endDate.value = getLastMonth(12, 1)[1];
    onclickGetReport();
});
const onclickGetReport = () => {
    loading.value = true;
    let currentProvince_id = props.currentPR != null ? props.currentPR.key : '0';
    let currentTerritory_id = props.currentTR != null ? props.currentTR.key : '0';
    let currentHealtharia_id = props.currentHA != null ? props.currentHA.key : '0';
    let currentFacility = props.currentFacility != null ? props.currentFacility.key : '0';

    reportUrl.value =
        '/people/scheduled_training_course?' +
        'province_id=' +
        currentProvince_id +
        '&tr_id=' +
        currentTerritory_id +
        '&ha_id=' +
        currentHealtharia_id +
        '&startDate=' +
        startDate.value.toISOString().slice(0, 10) +
        '&endDate=' +
        endDate.value.toISOString().slice(0, 10) +
        '&assr=' +
        provinceType.value +
        '&category=' +
        selectedCategory.value.code;
    apiService
        .get(reportUrl.value)
        .then((res) => {
            error.value = null;
            data.value = [];
            // this.interval = res.data.interval;
            let i = 0;
            res.data.data.forEach((elt) => {
                var line = {
                    no: ++i,
                    id: elt.id,
                    name: elt.name,
                    start_date: new Date(elt.start_date).toLocaleDateString('fr'),
                    end_date: new Date(elt.end_date).toLocaleDateString('fr'),
                    instructors: elt.instructors,
                    stc: elt.stc,
                    location: elt.location,
                    category_name: elt.category_name,
                    gender_m: elt.gender_m,
                    gender_f: elt.gender_FaM - elt.gender_m,
                    total: elt.gender_FaM
                };

                data.value.push(line);
            });
            data.value.sort((a, b) => b.scheduled_training_course - a.scheduled_training_course);
        })
        .catch((err) => {
            error.value = err;
            console.log(err);
        })
        .finally(() => {
            loading.value = false;
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
const training_course_detail = (id) => {
    loadingStudents.value = true;
    training_course_details_url.value = '/people/scheduled_training_course_details/' + id;
    apiService
        .get(training_course_details_url.value)
        .then((res) => {
            console.log(res);
            studentError.value = null;
            students.value = [];
            personcategories.value = res.data.cadres;
            // console.log(this.personcategories )
            var genderStat = { m: 0, f: 0 };
            var idnumStat = { nu: 0, ss: 0 };
            var i = 0;
            res.data.data.forEach((elt) => {
                personcategories.value.forEach((cat) => {
                    if (cat.name == elt.cadre) {
                        if (cat.value) {
                            cat.value += 1;
                        } else {
                            cat.value = 1;
                        }
                    }
                });
                if (elt.gender == 'gender|M') {
                    genderStat.m += 1;
                } else if (elt.gender == 'gender|F') {
                    genderStat.f += 1;
                }
                if (elt.id_num.toUpperCase() == 'NU' || elt.id_num.toUpperCase() == 'N.U') {
                    idnumStat.nu += 1;
                } else if (elt.id_num.length > 3) {
                    idnumStat.ss += 1;
                }

                var line = {
                    no: ++i,
                    id: elt.id,
                    firstname: elt.firstname,
                    surname: elt.surname,
                    othername: elt.othername,
                    gender: elt.gender.replace('gender|', ''),
                    birth_date: new Date(elt.birth_date).toLocaleDateString('fr'),
                    cadre: elt.cadre,
                    health_area: elt.health_area,
                    facility: elt.facility,
                    id_num: elt.id_num
                };

                students.value.push(line);
            });
            initCategoryChart(personcategories.value);
            genderChartData.value = {
                labels: ['Hommes', 'Femmes'],
                datasets: [
                    {
                        data: [genderStat.m, genderStat.f],
                        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
                        hoverBackgroundColor: ['#FF6384', '#36A2EB', '#FFCE56']
                    }
                ]
            };
            idnumChartData.value = {
                labels: ['Nouvelles unités', 'Admis sous statut'],
                datasets: [
                    {
                        data: [idnumStat.nu, idnumStat.ss],
                        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
                        hoverBackgroundColor: ['#FF6384', '#36A2EB', '#FFCE56']
                    }
                ]
            };
        })
        .catch((err) => {
            studentError.value = err;
            console.log(err);
        })
        .finally(() => {
            loadingStudents.value = false;
        });
};

const onChangeSelectCategory = (val) => {
    console.log(val);
};
const initCategoryChart = (data) => {
    var lables = [];
    var values = [];
    data.forEach((cat) => {
        lables.push(cat.name);
        values.push(cat.value);
    });

    categoryChartData.value = {
        labels: lables,
        datasets: [
            {
                label: 'Agents formés par catégorie professionnelle',
                data: values,
                backgroundColor: [ '#36A2EB'],
            }
        ]
    };
};
const onDetail = (val) => {
    detaDialogDisplay.value = true;
    reportLine.value = val.data;
    training_course_detail(val.data.id);
    console.log(val);
};
const onCloseStudentsModal = () => {
    detaDialogDisplay.value = false;
};
const downloadExcelFile = (val) => {
    if (val == 1) {
        let settings = {
            fileName: 'FORMATIONS ORGANISEES - ' + new Date().toLocaleString(),
            writeMode: 'writeFile',
            RTL: false
        };

        let mdata = [
            {
                sheet: 'FORMATIONS ORGANISEES  ',
                columns: [
                    { label: 'no', value: 'no' },
                    { label: 'DEBUT', value: 'start_date' },
                    { label: 'FIN', value: 'end_date' },
                    { label: 'FORMATIONS ORGANISEES', value: 'name' },
                    { label: 'CATEGORIES %', value: 'category_name' },
                    { label: 'FORMATEURS', value: 'instructors' },
                    { label: 'LOCALISATION', value: 'location' },
                    { label: 'LIEUX', value: 'stc' },
                    { label: 'HOMMES FORMES %', value: 'gender_m' },
                    { label: 'FEMMES FORMEES', value: 'gender_f' },
                    { label: 'TOTAL', value: 'total' }
                ],
                content: data.value
            }
        ];
        xlsx(mdata, settings);
    } else if (val == 2) {
        let settings = {
            fileName: reportLine.value.name + ' - ' + new Date().toLocaleString(),
            writeMode: 'writeFile',
            RTL: false
        };

        let mdata = [
            {
                sheet: 'FORMES  ',
                columns: [
                    { label: 'no', value: 'no' },
                    { label: 'NOM', value: 'firstname' },
                    { label: 'POSTNOM', value: 'surname' },
                    { label: 'PRENOM', value: 'othername' },
                    { label: 'GENRE ', value: 'gender' },
                    { label: 'DATE.NAISSANCE', value: 'birth_date' },
                    { label: 'MATRICULE', value: 'id_num' },
                    { label: 'ZS', value: 'health_area' },
                    { label: 'STRUCTURE', value: 'facility' }
                ],
                content: students.value
            }
        ];
        xlsx(mdata, settings);
    }
};
const _exportFile = (val) => {
    var url = '';
    if (val == 1) {
        url = reportUrl.value + '&download=1';
    } else {
        url = training_course_details_url.value + '?download=1&title=FORMATION - ' + reportLine.value.name + '(' + reportLine.value.start_date + ' - ' + reportLine.value.end_date + ')';
    }

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
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            //  progress.finish();
        })
        .catch((err) => {
            console.log(err);
            // progress.finish();
        });
};

const updateReport = () => {
    onclickGetReport();
};
defineExpose({
    updateReport
});
</script>
<template>
    <div class="card">
        <div class="grid">
            <div class="col-12 md:col-6 lg:col-3">
                <Calendar v-model="startDate" :show-icon="true" dateFormat="dd/mm/yy" class="p-inputtext-sm w-full" />
            </div>
            <div class="col-12 md:col-6 lg:col-3">
                <Calendar v-model="endDate" :show-icon="true" dateFormat="dd/mm/yy" class="p-inputtext-sm w-full" />
                <br />
            </div>
            <div class="col-12 md:col-6 lg:col-3">
                <span class="p-fluid">
                    <Dropdown v-model="selectedCategory" :options="reportCategory" @change="onChangeSelectCategory($event)" optionLabel="name" placeholder="Catégories de formations continues" />
                </span>
            </div>
            <div class="col-12 md:col-6 lg:col-3">
                <Button @click="onclickGetReport()" :disabled="loading" label="VISUALISER" class="p-button-primary" />
            </div>
        </div>

        <Message v-if="data.length == 0 && error == null && !loading" :severity="warn" :key="1">Aucune formation pour la période ({{ startDate.toLocaleDateString('fr') }} - {{ endDate.toLocaleDateString('fr') }})!</Message>

        <div class="mt-4">
            <div v-if="(data.length == 0 && loading) || (loading && error != null)">
                <div class="text-center m-4 p-4">
                    <ProgressSpinner v-if="loading" />
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
            <DataTable
                v-if="data.length > 0 && error == null"
                :value="data"
                stripedRows
                class="p-datatable-sm"
                :paginator="true"
                :rows="16"
                responsiveLayout="scroll"
                :scrollable="true"
                dataKey="id"
                v-model:filters="filters2"
                filterDisplay="menu"
                scrollHeight="500px"
                :loading="loading"
                :globalFilterFields="['name']"
                showGridlines
                :resizableColumns="true"
                columnResizeMode="expand"
            >
                <template #header>
                    <div class="flex justify-content-end text-right">
                        <span class="p-input-icon-left float-left">
                            <i class="pi pi-search" />
                            <InputText v-model="filters2['name'].value" class="p-inputtext-sm" placeholder="Rechercher ..." />
                        </span>
                        <Button @click="_exportFile(1)" label="PDF" icon="pi pi-file-pdf" class="p-button-danger p-button-outlined p-button-sm ml-2 mb-4" iconPos="right" />
                        <Button @click="downloadExcelFile(1)" label="EXCEL" icon="pi pi-file-excel" class="p-button-success p-button-outlined p-button-sm ml-2 mb-4" iconPos="right" />
                    </div>
                </template>

                <ColumnGroup type="header">
                    <Row>
                        <Column header="Dates" :colspan="2" class="text-center" />
                        <Column :sortable="true" field="name" headerStyle="width: 300px;" header="Formations organisées" :rowspan="2"></Column>
                        <Column :sortable="true" field="category_name" headerStyle="width: 300px;" header="Catégorie" :rowspan="2"></Column>
                        <Column header="Personnel formé" :colspan="3" />
                        <Column header="Action" :rowspan="2" bodyStyle="text-align: right" class="text-right" />
                    </Row>
                    <Row>
                        <Column :sortable="true" field="start_date" style="width: 50px" header="Début" class="text-center"></Column>
                        <Column :sortable="true" field="end_date" style="width: 50px" header="Fin" class="text-center"></Column>
                        <Column :sortable="true" field="gender_m" header="M" class="text-center"></Column>
                        <Column :sortable="true" field="gender_f" header="F" class="text-center"></Column>
                        <Column :sortable="true" field="total" header="Total" class="font-weigth-bold text-center"></Column>
                    </Row>
                </ColumnGroup>
                <Column :sortable="true" field="start_date" header="Début"></Column>
                <Column :sortable="true" field="end_date" header="Fin"></Column>
                <Column :sortable="true" field="name" style="min-width: 300px" header="Formation"></Column>
                <Column :sortable="true" field="category_name" style="min-width: 300px" header="Catégorie"></Column>
                <Column :sortable="true" field="gender_m" headerStyle="width: 10%" header="M"></Column>
                <Column :sortable="true" field="gender_f" headerStyle="width: 10%" header="F"></Column>
                <Column :sortable="true" field="total" headerStyle="width: 10%" header="Total"></Column>
                <Column bodyStyle="text-align: right;display: block;" headerStyle="width: 10%" header="Action" class="text-right">
                    <template #body="slotProps">
                        <Button type="button" label="détails" @click="onDetail(slotProps)" class="p-button-sm p-button-primary float-right"></Button>
                    </template>
                </Column>
            </DataTable>
        </div>
        <Dialog v-model:visible="detaDialogDisplay" position="top" modal="true" maximizable="true" :breakpoints="{ '960px': '75vw', '640px': '100vw' }" :style="{ width: '70vw' }">
            <template #header>
                <h3>Formation: {{ reportLine.name }}</h3>
            </template>
            <div v-if="loadingStudents && students.length == 0" class="text-center m-4 p-4">
                <ProgressSpinner :animationDuration="'2s'" />
                <p class="m-4 text-muted">chargement en cours, veuillez patienter...</p>
            </div>
            <div v-if="studentError != null && !loadingStudents" class="row">
                <div class="col-sm-3"></div>
                <div class="col-sm-6 text-center m-4">
                    <div class="alert alert-danger text-center" role="alert">
                        <h4>Echec de connexion</h4>
                        <p>{{ studentError }}</p>
                        <hr />
                        <Button @click="training_course_detail(reportLine.id)" label="Réessayer" class="p-button-danger p-button-sm" />
                    </div>
                </div>
            </div>
            <Message v-if="students.length == 0 && studentError == null && !loadingStudents" :severity="warn" :key="1">Aucun personnel enregistré pour cette formation!</Message>

            <TabView v-if="students.length > 0 && studentError == null">
                <TabPanel header="Agents formés">
                    <DataTable
                        v-if="students.length > 0 && studentError == null"
                        :value="students"
                        stripedRows
                        class="p-datatable-sm"
                        :paginator="true"
                        :rows="16"
                        responsiveLayout="scroll"
                        :scrollable="true"
                        dataKey="id"
                        filterDisplay="menu"
                        scrollHeight="500px"
                        :loading="loadingStudents"
                        v-model:filters="filters"
                        :globalFilterFields="['firstname', 'surname', 'othername', 'id_num', 'health_area', 'facility']"
                    >
                        <template #header>
                            <div class="grid">
                                <div class="col">
                                    <div class="flex justify-content-">
                                        <IconField iconPosition="left">
                                            <InputIcon>
                                                <i class="pi pi-search" />
                                            </InputIcon>
                                            <InputText v-model="filters[('firstname', 'surname', 'othername', 'id_num', 'health_area', 'facility')].value" placeholder="Keyword Search" />
                                        </IconField>
                                    </div>
                                </div>
                                <div class="col">
                                    <div class="flex justify-content-end text-right">
                                        <Button @click="_exportFile(2)" label="PDF" icon="pi pi-file-pdf" class="p-button-danger p-button-outlined p-button-sm ml-2 mb-4" iconPos="right" />
                                        <Button @click="downloadExcelFile(2)" label="EXCEL" icon="pi pi-file-excel" class="p-button-success p-button-outlined p-button-sm ml-2 mb-4" iconPos="right" />
                                    </div>
                                </div>
                            </div>
                        </template>

                        <Column :sortable="true" field="firstname" header="Nom" class=""> </Column>
                        <Column :sortable="true" field="othername" header="Postnom" class=""></Column>
                        <Column :sortable="true" field="surname" header="Prénom" class=""></Column>
                        <Column :sortable="true" headerStyle="width: 10px" bodyStyle="width: 10px" field="gender" header="Sexe"></Column>
                        <Column :sortable="true" headerStyle="width: 20px" field="birth_date" header="D. naissance"></Column>
                        <Column :sortable="true" field="cadre" header="Catégorie"></Column>
                        <Column :sortable="true" field="health_area" header="ZS"></Column>
                        <Column :sortable="true" field="facility" header="STRUCTURE"></Column>
                    </DataTable>
                </TabPanel>
                <TabPanel header="catégories">
                    <div class="grid">
                        <div class="col-8">
                            <Chart type="bar" :data="categoryChartData" :options="lightOptions" />
                        </div>
                        <div class="col-4">
                            <div v-for="cat of personcategories" :key="cat.name" class="border-bottom">
                                <small>{{ cat.name }}</small>
                                <span class="float-right text-info pl-2">({{ (cat.value = cat.value || 0) }})</span>
                            </div>
                        </div>
                    </div>
                </TabPanel>
                <TabPanel header="Statut d’emploi/Sexe">
                    <div class="grid">
                        <div class="col">
                            <h5>Agents formés par status d'emploi</h5>
                            <Chart type="doughnut" :data="idnumChartData" :options="lightOptions" />
                        </div>
                        
                        <div class="col">
                            <h5>Agents formés par sexe</h5>
                            <Chart type="doughnut" :data="genderChartData" :options="lightOptions" />
                        </div>
                        <div class="col"></div>
                    </div>
                </TabPanel>
            </TabView>

            <template #footer>
                <Button label="Fermer" @click="onCloseStudentsModal()" autofocus />
            </template>
        </Dialog>
    </div>
</template>
