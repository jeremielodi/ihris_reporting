<script setup>
import { ref } from 'vue';
import apiService from '@/service/ApiService';
import ChartDataLabels from 'chartjs-plugin-datalabels';
const loadingDashUtils = ref(false);
const loadingTimesheet = ref(false);
const showTreeError = ref(false);
const utilsDashData = ref({ effectif: null });
const basicData_labels = ref([]);

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

const basicData = ref({
    labels: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
    datasets: [
        {
            label: 'Formations organisées',
            backgroundColor: '#ff6500',
            data: [0, 0, 0, 0, 0, 0, 0]
        }
    ]
});
const personData = ref({
    labels: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
    datasets: [
        {
            label: 'Hommes',
            backgroundColor: '#ff6500',
            data: [0, 0, 0, 0, 0, 0, 0]
        },
        {
            label: 'Femmes',
            backgroundColor: '#42A5F5',
            data: [0, 0, 0, 0, 0, 0, 0]
        }
    ]
});
const optionsGender = ref({
    responsive: true,
    plugins: {
        datalabels: {
            formatter: function (value) {
                return value + '%';
            }
        }
    }
});

const genders = ref({
    labels: ['M', 'F', 'Non renseignés'],
    datasets: [
        {
            data: [0, 0, 0],
            backgroundColor: ['#36A2EB', '#FFCE56', '#FF6384'],
            hoverBackgroundColor: ['#36A2EB', '#FFCE56', '#FF6384']
        }
    ],
    plugins: [ChartDataLabels]
});
const getData = () => {
    // if (!props.currentPR) {
    //     showTreeError.value = true;
    //     return;
    // } else {
    /// this.getUtils();
    getTrainingDashBoard();
    setTimeout(() => {
        getTrainingDashBoard();

        // this.getCadreBoard();
    }, 600);
};

const getTrainingDashBoard = () => {
    loadingDashUtils.value = true;
    // let currentProvince_id = props.currentPR != null ? props.currentPR.key : '0';
    // let currentTerritory_id = props.currentTR != null ? props.currentTR.key : '0';
    // let currentHealtharia_id = props.currentHA != null ? props.currentHA.key : '0';
    // let currentFacility = props.currentFacility != null ? props.currentFacility.key : '0';

    let url = '/training/dashboard';
    apiService
        .get(url)
        .then((res) => {
            console.log(res);
            basicData.value.datasets[0].data = res.data.scheduled_training;

            personData.value.datasets[0].data = res.data.person_scheduled_training_m;
            personData.value.datasets[1].data = res.data.person_scheduled_training_f;

            basicData.value.labels = res.data.labels1;
            basicData_labels.value = res.data.labels;

            // this.timesheets.datasets[0].data = res.data.timesheet.values;
            //this.timesheets.labels = res.data.timesheet.labels;
        })
        .catch((err) => {
            console.log(err);
        })
        .finally(() => {
            loadingDashUtils.value = false;
        });
};
const breadcrumbItems = () => {
    var res = [];
    res.push({ label: 'Sélectionner une Province, Territoire, Zone de Santé' });
    if (props.currentPR) {
        res.pop();
        res.push({ label: props.currentPR.label });
    }
    if (props.currentTR) res.push({ label: props.currentTR.label });

    if (props.currentHA) res.push({ label: props.currentHA.label });

    return res;
};

const updateReport = () => {
    getData();
};
defineExpose({
    updateReport
});
</script>
<template>
    <div>
        <!--div class="border">
            <div class="row">
                <div class="col-sm-8">
                    <Breadcrumb class="p-menuitem" :model="breadcrumbItems()">
                        <template #item="{ item }">
                            <a :href="'#' + item.label">{{ item.label }}</a>
                        </template>
                    </Breadcrumb>
                </div>
                <div class="col-sm-4 text-right">
                    <Button label="Actualiser" icon="pi pi-bolt" class="float-end mr-2 mt-1 p-button-sm" :loading="loadingDashUtils" @click="getData()" />
                </div>
            </div>
        </!--div-->
        <Message :sticky="false" :life="10000" severity="info"> <small>Bienvenue au</small> Tableau de bord<small>, Pour visualiser, sélectionner votre province, Territoire, Zone de santé et cliquer</small> Actualiser. </Message>
        <Message v-if="showTreeError && !currentPR" severity="error"> Erreur: <Small>Veuillez sélectionner votre province, Territoire, Zone de santé et cliquer </Small>Actualiser </Message>

        <!-- div class="grid">
            <div class="col-12 md:col-6 lg:col-3">
                <div class="card">
                    <div class="card-body py-3">
                        <div>
                            <h6 class="mb-1">
                                Formations organisées
                                <Button v-if="!loadingDashUtils && utilsDashData.effectif" icon="pi pi-download" class="p-button-text p-button-sm float-right" v-tooltip="'Télécharger la liste'" />
                            </h6>
                            <Skeleton v-if="loadingDashUtils" class="mb-0" width="100%" height="17px" />
                            <small class="mb-0 text-primary" v-if="!loadingDashUtils && utilsDashData.effectif">{{ utilsDashData.effectif }} agents </small>
                            <small class="mb-0 text-primary" v-if="!loadingDashUtils && utilsDashData.effectif == null"> -- </small>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-12 md:col-6 lg:col-3">
                <div class="card">
                    <div class="card-body py-3">
                        <div>
                            <h6 class="mb-1">
                                Indicateur 1
                                <Button v-if="!loadingDashUtils && utilsDashData.admin" icon="pi pi-download" class="p-button-text p-button-sm float-right" v-tooltip="'Télécharger la liste d\'administratifs'" />
                            </h6>
                            <Skeleton v-if="loadingDashUtils" class="mb-0" width="100%" height="17px" />
                            <small class="mb-0 text-primary" v-if="!loadingDashUtils && utilsDashData.admin">{{ utilsDashData.admin }} agents </small>
                            <small class="mb-0 text-primary" v-if="!loadingDashUtils && !utilsDashData.admin"> -- </small>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-12 md:col-6 lg:col-3">
                <div class="card">
                    <div class="card-body py-3">
                        <div>
                            <h6 class="mb-1">
                                Indicateur 2
                                <Button v-if="!loadingDashUtils && utilsDashData.effectif" icon="pi pi-download" class="p-button-text p-button-sm float-right" v-tooltip="'Télécharger la liste de professionnels de santé'" />
                            </h6>
                            <Skeleton v-if="loadingDashUtils" class="mb-0" width="100%" height="17px" />
                            <small class="mb-0 text-primary" v-if="!loadingDashUtils && utilsDashData.effectif != null">{{ utilsDashData.effectif - utilsDashData.admin }} agents</small>
                            <small class="mb-0 text-primary" v-if="!loadingDashUtils && utilsDashData.effectif == null"> -- </small>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-12 md:col-6 lg:col-3">
                <div class="card">
                    <div class="card-body py-3">
                        <div>
                            <h6 class="mb-1">
                                Indicateur 3
                                <Button v-if="!loadingDashUtils && utilsDashData.enactivite" icon="pi pi-download" class="p-button-text p-button-sm float-right" v-tooltip="'Télécharger la liste des agents en position active'" />
                            </h6>
                            <Skeleton v-if="loadingDashUtils" class="mb-0" width="100%" height="17px" />
                            <small class="mb-0 text-primary" v-if="!loadingDashUtils && utilsDashData.enactivite">{{ utilsDashData.enactivite }} agents</small>
                            <small class="mb-0 text-primary" v-if="!loadingDashUtils && !utilsDashData.enactivite">--</small>
                        </div>
                    </div>
                </div>
            </div>
        </!-->

        <div class="grid">
            <div class="col-12 md:col-12 lg:col-8">
                <div class="card">
                    <div class="card-body">
                        <Skeleton v-if="loadingDashUtils" class="mb-0" width="100%" height="17px"></Skeleton>
                        <h4 v-if="!loadingTimesheet">Formations organisées par thèmatique</h4>
                        <div class="row">
                            <div class="col-md-7">
                                <Chart type="bar" :data="basicData" />
                            </div>
                            <div class="col-md-5">
                                <ol>
                                    <li v-for="item in basicData_labels" :key="item">
                                        <b> {{ item }}</b>
                                    </li>
                                </ol>
                            </div>
                        </div>
                    </div>
                </div>
                <hr />
                <div class="card">
                    <div class="card-body">
                        <Skeleton v-if="loadingDashUtils" class="mb-0" width="100%" height="17px"></Skeleton>
                        <h4 v-if="!loadingTimesheet">Personnel formé par thèmatique & par genre</h4>
                        <div class="row">
                            <div class="col-md-7">
                                <Chart type="bar" :data="personData" />
                            </div>
                            <div class="col-md-5">
                                <ol>
                                    <li v-for="item in basicData_labels" :key="item">
                                        <b> {{ item }}</b>
                                    </li>
                                </ol>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-12 md:col-12 lg:col-4">
                <div class="card">
                    <div class="card-body">
                        <h4 v-if="!loadingDashUtils">....</h4>
                        <Skeleton v-if="loadingDashUtils" class="mb-0" width="100%" height="17px" />
                        <div class="mx-4">
                            <Chart type="doughnut" :data="genders" :options="optionsGender" :plugins="plugins" />
                        </div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-body">
                        <h4 v-if="!loadingDashUtils">...</h4>
                        <Skeleton v-if="loadingDashUtils" class="mb-0" width="100%" height="17px" />
                        <div class="mx-4">
                            <Chart type="doughnut" :data="genders" :options="optionsGender" :plugins="plugins" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
