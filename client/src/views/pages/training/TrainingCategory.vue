<script setup>
import { ref, onMounted } from 'vue';
import xlsx from 'json-as-xlsx';
import apiService from '@/service/ApiService';
import { FilterMatchMode } from '@primevue/core/api';

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
const interval = ref(null);
const startDate = ref(new Date());
const endDate = ref(new Date());
const reportUrl = ref(null);
const provinceType = ref(1);
const selectedCategory = ref({ name: 'Mois', code: 1 });
const loading = ref(false);
const detaDialogDisplay = ref(false);
const reportLine = ref({});
const students = ref([]);
const loadingStudents = ref(false);

const filters2 = ref({
    name: { value: null, matchMode: FilterMatchMode.CONTAINS },
    firstname: { value: null, matchMode: FilterMatchMode.CONTAINS },
    surname: { value: null, matchMode: FilterMatchMode.CONTAINS },
    othername: { value: null, matchMode: FilterMatchMode.CONTAINS }
});
const data = ref([]);
const personcategories = ref([]);
const categoryChartData = ref(null);
const genderChartData = ref(null);
const idnumChartData = ref(null);

onMounted(() => {
    onclickGetReport();
});
const onclickGetReport = () => {
    loading.value = true;
    let currentProvince_id = props.currentPR != null ? props.currentPR.key : '0';
    let currentTerritory_id = props.currentTR != null ? props.currentTR.key : '0';
    let currentHealtharia_id = props.currentHA != null ? props.currentHA.key : '0';
    let currentFacility = props.currentFacility != null ? props.currentFacility.key : '0';

    reportUrl.value =
        '/training/trainingcours?' +
        'province_id=' +
        currentProvince_id +
        '&tr_id=' +
        currentTerritory_id +
        '&ha_id=' +
        currentHealtharia_id +
        '&startDate=' +
        startDate.value.toISOString().slice(0, 10) +
        '/' +
        'endDate=' +
        endDate.value.toISOString().slice(0, 10) +
        '?assr=' +
        provinceType.value +
        '&category=' +
        selectedCategory.value.code;
    apiService
        .get(reportUrl.value)
        .then((res) => {
            error.value = null;
            data.value = [];
            interval.value = res.data.interval;

            res.data.data.forEach((elt) => {
                var line = {
                    id: elt.id,
                    name: elt.name,
                    scheduled_training_course: elt.scheduled_training_course,
                    gender_m: elt.gender_m,
                    gender_f: elt.gender_f,
                    category: elt.category,
                    total: elt.gender_f + elt.gender_m
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
const training_course_detail = (id) => {
    loadingStudents.value = true;
    apiService
        .get('/api/v1/training_course_detail/' + id)
        .then((res) => {
            studentError.value = null;
            students.value = [];
            personcategories.value = res.data.categories;
            var genderStat = { m: 0, f: 0 };
            var idnumStat = { nu: 0, ss: 0 };

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
                    id: elt.id,
                    firstname: elt.firstname,
                    surname: elt.surname,
                    othername: elt.othername,
                    gender: elt.gender.replace('gender|', ''),
                    birth_date: new Date(elt.birth_date).toLocaleDateString('fr'),
                    cadre: elt.cadre
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
            console.log(genderStat);
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
    //this.categoryChartData.lables = lables;
    //this.categoryChartData.datasets[0].data = values;
    categoryChartData.value = {
        labels: lables,
        datasets: [
            {
                label: 'Agents formés par catégorie professionnelle',
                data: values
            }
        ]
    };
    //console.log(this.categoryChartData)
};

const exportFileName = () => {
    return 'OK';
};

const downloadExcelFile = () => {
    let settings = {
        fileName: 'Formations  ' + new Date().toLocaleString(),
        writeMode: 'writeFile',
        RTL: false
    };
    let mdata = [
        {
            sheet: 'Complétude de prestation  ',
            columns: [
                { label: 'No', value: 'id' },
                { label: 'Cours de formation', value: 'name' },
                { label: 'Thématique', value: 'category' },
                { label: 'Formation organisées', value: 'scheduled_training_course' },

                { label: 'M', value: 'gender_m' },
                { label: 'f', value: 'gender_f' },
                { label: 'total', value: 'total' }
            ],
            content: data.value
        }
    ];

    xlsx(mdata, settings);
};
const exportFile = (format = 'pdf') => {
    window.open(apiService.defaults.baseURL + '/' + reportUrl.value + '&' + format + '=1&title=' + exportFileName(), '_blank');
};

const updateReport = () => {
    onclickGetReport();
};
defineExpose({
    updateReport
});
</script>
<template>
    <div className="card">
        <div>
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
                <Message v-if="data.length == 0 && error == null && !loading" :severity="warn" :key="1">Liste vide</Message>

                <DataTable
                    v-if="data.length > 0 && error == null"
                    :value="data"
                    stripedRows
                    class="p-datatable-sm"
                    :paginator="true"
                    :rows="20"
                    responsiveLayout="scroll"
                    :scrollable="true"
                    dataKey="id"
                    v-model:filters="filters2"
                    filterDisplay="menu"
                    scrollHeight="700px"
                    :loading="loading"
                    :globalFilterFields="['name']"
                >
                    <template #header>
                        <div class="flex justify-content-end text-right">
                            <span class="p-input-icon-left float-left">
                                <i class="pi pi-search" />
                                <InputText v-model="filters2['name'].value" class="p-inputtext-sm" placeholder="Rechercher ..." />
                            </span>
                            <!-- Button @click="exportFile()" label="PDF" icon="pi pi-file-pdf" class="p-button-danger p-button-outlined p-button-sm ml-2 mb-4" iconPos="right" / -->
                            <Button @click="downloadExcelFile()" label="EXCEL" icon="pi pi-file-excel" class="p-button-success p-button-outlined p-button-sm ml-2 mb-4" iconPos="right" />
                        </div>
                    </template>

                    <ColumnGroup type="header">
                        <Row>
                            <Column :sortable="true" headerStyle="width:40%" field="name" header="Cours de Formation" :rowspan="2"></Column>
                            <Column :sortable="true" field="category" header="Thématique" :rowspan="2"></Column>
                            <Column :sortable="true" field="scheduled_training_course" header="Formation Organisée" :rowspan="2"></Column>
                            <Column header="Agents formés" :colspan="3" />
                        </Row>
                        <Row>
                            <Column :sortable="true" field="gender_m" header="Hommes" class="text-center"></Column>
                            <Column :sortable="true" field="gender_f" header="Femmes" class="text-center"></Column>
                            <Column :sortable="false" field="total" header="Total" class="font-weigth-bold text-center"></Column>
                        </Row>
                    </ColumnGroup>
                    <Column :sortable="true" bodyStyle="min-width:40%" field="name" header="Formation"></Column>
                    <Column :sortable="true" bodyStyle="min-width:40%" field="category" header="Catégorie"></Column>

                    <Column :sortable="true" field="scheduled_training_course" header="Formations organisées"></Column>
                    <Column :sortable="true" headerStyle="width: 10px" field="gender_m" header="M"></Column>
                    <Column :sortable="true" headerStyle="width: 10px" field="gender_f" header="F"></Column>
                    <Column :sortable="true" field="total" header="Total"></Column>
                </DataTable>
            </div>
        </div>
    </div>
</template>
