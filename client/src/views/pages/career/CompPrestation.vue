<script setup>
import { onMounted, ref } from 'vue';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { FilterMatchMode } from '@primevue/core/api';
import apiService from '@/service/ApiService';
import xlsx from 'json-as-xlsx';
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
const chartData = ref({ labels: null, datasets: [] });
const chartOptions = ref(null);
const plugins = ref([ChartDataLabels]);
const interval = ref([]);
const startDate = ref(new Date());
const endDate = ref(new Date());
const zsFilter = ref(false);
const reportUrl = ref(null);
const selectedOption = ref({ name: 'Mois', code: 1 });
const selectionInterval = ref(3);
const loading = ref(false);
const reportOption = ref([{ name: 'Mois', code: 1 }]);
const filters2 = ref({
    fosa: { value: null, matchMode: FilterMatchMode.CONTAINS }
});
const products = ref([]);

onMounted(() => {
    reportOption.value.push({
        name: 'Six derniers mois (' + getLastMonth()[0] + ' au ' + getLastMonth()[1] + ')',
        code: -6
    });
    reportOption.value.push({
        name: 'Douze derniers mois(' + getLastMonth(12)[0] + ' au ' + getLastMonth()[1] + ')',
        code: -12
    });
    startDate.value = getLastMonth(6, 1)[0];

    chartData.value = setChartData();
    chartOptions.value = setChartOptions();
});

const onclickGetReport = () => {
    currentNode.value = _AppCache.getCurrentNode();
    if (!currentNode.value) return;
    if (loading.value) return;
    loading.value = true;

    reportUrl.value =
        '/reports/timesheet_report?' +
        'org_unit_id=' +
        currentNode.value +
        '&' +
        'start_date=' +
        startDate.value.toLocaleString('sv', { timeZoneName: 'short' }).slice(0, 10) +
        '&' +
        'end_date=' +
        endDate.value.toLocaleString('sv', { timeZoneName: 'short' }).slice(0, 10) +
        '&' +
        '&selectOption=' +
        selectedOption.value.code +
        '&selectionInterval=' +
        +selectionInterval.value +
        '&title=' +
        props.title +
        '&zs_filter=' +
        (zsFilter.value ? 1 : 0);
    products.value = [];
    apiService
        .get(reportUrl.value)
        .then((res) => {
            error.value = null;

            interval.value = res.data.intervals;
            var y = 0;
            var mdata = [];

            let _chartData_g = [];
            let _chartData_actif = [];
            let _chartDatalabel = [];
            let _chartDataIntCom = [];
            res.data.report.data.forEach((elt) => {
                console.log(elt);
                elt.id = y += 1;
                elt.moyenne = elt.moyenne.toFixed(1);
                elt.effectif = elt.effectif_gen;
                elt.effectif_inactif = elt.effectif_gen - elt.effectif_actif;
                elt.taux_general = (elt.effectif_gen >= 0 ? (elt.moyenne / elt.effectif_gen) * 100 : 0).toFixed(2);
                elt.taux_actif = (elt.effectif_actif >= 0 ? (elt.moyenne / elt.effectif_actif) * 100 : 0).toFixed(2);
                elt.com_int_perc = elt.com_int_perc.toFixed(2);
                mdata.push(elt);
                _chartDatalabel.push(elt.location);
                _chartData_g.push(elt.taux_general);
                _chartData_actif.push(elt.taux_actif);
                _chartDataIntCom.push(elt.com_int_perc);
            });
            products.value = mdata;
            chartData.value.labels = _chartDatalabel;
            chartData.value.datasets[0] = { data: _chartData_g, label: 'Taux comp. prestation / effectif general' };
            chartData.value.datasets[1] = { data: _chartData_actif, label: "Taux comp.prestation / l'effectif actif" };
            chartData.value.datasets[2] = { data: _chartDataIntCom, label: 'Taux comp. interne' };
        })
        .catch((err) => {
            error.value = err;
            console.log(err);
        })
        .finally(() => {
            loading.value = false;
        });
};
const onChangeSelectionOption = (val) => {
    if (val.value.code == -6) {
        startDate.value = getLastMonth(6, 1)[0];
        endDate.value = getLastMonth(6, 1)[1];
        selectionInterval.value = 6;
    } else if (val.value.code == -12) {
        startDate.value = getLastMonth(12, 1)[0];
        endDate.value = getLastMonth(12, 1)[1];
        selectionInterval.value = 12;
    }
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

const setChartData = () => {
    const documentStyle = getComputedStyle(document.documentElement);

    return {
        labels: [],
        datasets: [
            {
                label: 'Compétude  de prestation / effectif general',
                backgroundColor: '#fd7e14',
                borderColor: documentStyle.getPropertyValue('--blue-500'),
                data: []
            },
            {
                label: 'Compétude  de prestation / effectif actif',
                backgroundColor: '#38c172',
                borderColor: documentStyle.getPropertyValue('--pink-500'),
                data: []
            },
            {
                label: 'Compétude  de prestation / effectif actif',
                backgroundColor: '#1c80cf',
                borderColor: documentStyle.getPropertyValue('--pink-500'),
                data: []
            }
        ]
    };
};
const setChartOptions = () => {
    const documentStyle = getComputedStyle(document.documentElement);
    const textColorSecondary = documentStyle.getPropertyValue('--text-color-secondary');
    const surfaceBorder = documentStyle.getPropertyValue('--surface-border');

    return {
        maintainAspectRatio: false,
        aspectRatio: 0.8,
        responsive: true,
        plugins: {
            datalabels: {
                formatter: function (value) {
                    return value + '%';
                },

                anchor: 'end',
                backgroundColor: function (context) {
                    return context.dataset.backgroundColor;
                },
                borderColor: 'white',
                borderRadius: 25,
                borderWidth: 2,
                color: 'white',
                font: {
                    weight: 'bold'
                },
                padding: 6
            }
        },
        scales: {
            x: {
                ticks: {
                    color: textColorSecondary,
                    font: {
                        weight: 500
                    }
                },
                grid: {
                    display: false,
                    drawBorder: false
                }
            },
            y: {
                ticks: {
                    color: textColorSecondary
                },
                grid: {
                    color: surfaceBorder,
                    drawBorder: false
                }
            }
        }
    };
};

const downloadFile = (_file) => {
    if (reportUrl.value != null) {
        download(reportUrl.value + '&download=' + _file + '&title=' + exportFileName());
    }
};

const download = (url) => {
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
const downloadExcelFile = () => {
    let settings = {
        fileName: 'COMPLETUDE DE PRSTATION - ' + exportFileName() + ' - ' + new Date().toLocaleString(),
        writeMode: 'writeFile',
        RTL: false
    };

    let data = [
        {
            sheet: 'Complétude interne  ',
            columns: [
                { label: 'No', value: 'id' },
                { label: 'LIEU', value: 'location' },
                { label: 'EFFECTIF GENETAL', value: 'effectif' },
                { label: 'EFFECTIF ACTIF', value: 'effectif_actif' },
                { label: 'EFFECTIF INACTIF ', value: 'effectif_inactif' }
            ],

            content: products.value
        }
    ];
    interval.value.forEach((val) => {
        data[0].columns.push({ label: val.local_abb, value: val.key });
    });

    data[0].columns.push(
        ...[
            { label: 'MOYENNE', value: 'moyenne' },
            { label: 'COMP. INTERNE', value: 'com_int_perc' },
            { label: 'COMP. ACTIF', value: 'taux_actif' },
            { label: 'COMP. GENERAL', value: 'taux_general' }
        ]
    );
    xlsx(data, settings);
};
</script>
<template>
    <div>
        <PyarmidPath :reload="onclickGetReport" />

        <div class="card">
            <h5>COMPLÉTUDE DE PRESTATION</h5>
            <hr />
            <div class="grid">
                <div class="col-6 sm:col-4 md:col-3 lg:col-2">
                    <label for="startDate" class="">Debut:</label>
                    <Calendar v-model="startDate" :show-icon="true" dateFormat="dd/mm/yy" class="p-inputtext-sm w-full" />
                </div>
                <div class="col-6 sm:col-4 md:col-3 lg:col-2">
                    <label for="startDate" class="">Fin:</label>
                    <Calendar v-model="endDate" :show-icon="true" dateFormat="dd/mm/yy" class="p-inputtext-sm w-full" />
                </div>
                <div class="col-6 sm:col-4 md:col-3 lg:col-2">
                    <label for="startDate" class="">Selection:</label>
                    <Dropdown class="p-inputtext-sm w-full" v-model="selectedOption" :options="reportOption" @change="onChangeSelectionOption($event)" optionLabel="name" placeholder="Option d'affichage" />
                </div>

                <div class="col-12 sm:col-12 sm:col-3 lg:col-6 text-right">
                    <label for="switch1">Filtrer les ZS</label>
                    <InputSwitch v-model="zsFilter" @change="onclickGetReport()" inputId="switch1" class="ml-2" />
                    <Button @click="onclickGetReport()" label="VISUALISER" icon="pi pi-refresh" :loading="loading" class="p-button-primary p-button-sm ml-3" />
                </div>
            </div>
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
                <Message v-if="products.length == 0 && !loading && error == null" severity="info"> <b>Aucune donnée</b>, liste vide </Message>

                <TabView v-if="products.length > 0 && error == null">
                    <TabPanel :key="1" :header="'Détails'" class="p-0">
                        <DataTable
                            :value="products"
                            stripedRows
                            class="p-datatable-sm timesheet_table"
                            :paginator="true"
                            :rows="40"
                            responsiveLayout="scroll"
                            :scrollable="true"
                            dataKey="id"
                            v-model:filters="filters2"
                            filterDisplay="menu"
                            :loading="loading"
                            :globalFilterFields="['fosa']"
                            scrollHeight="100%"
                            :resizableColumns="true"
                            columnResizeMode="fit"
                            showGridlines
                            ref="dt"
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
                                        <Button @click="downloadFile(3)" label="PDF" icon="pi pi-file-pdf" class="p-button-danger p-button-sm p-button-outlined p-button ml-2" iconPos="right" />
                                        <Button @click="downloadExcelFile()" label="EXCEL" icon="pi pi-file-excel" class="p-button-success p-button-sm p-button-outlined p-button ml-2" iconPos="right" />
                                        <Button @click="downloadFile(2)" label="DETAILLÉ" icon="pi pi-file-excel" class="p-button-success p-button-sm p-button-outlined p-button ml-2" iconPos="right" />
                                    </div>
                                </div>
                            </template>
                            <ColumnGroup type="header">
                                <Row>
                                    <Column sortable header="LIEUX" field="location" :rowspan="2" />
                                    <Column header="EFFECTIFS" class="text-center" colspan="3" />
                                    <Column sortable v-for="col of interval" :header="col.local_abb" :key="col.key" :rowspan="2"></Column>
                                    <Column header="MOY." sortable field="moyenne" rowspan="2" />
                                    <Column header="COMPLETUDES DE PRESTATION" colspan="3" />
                                </Row>

                                <Row>
                                    <Column sortable header="GENERAL" field="effectif" />
                                    <Column sortable header="ACTIF" field="effectif_actif" />
                                    <Column sortable header="INACTIF" field="effectif_inactif" />
                                    <Column sortable header="INTERNE" field="com_int_perc" />
                                    <Column sortable header="ACTIF" field="taux_actif" />
                                    <Column sortable header="INACTIF" field="taux_general" />
                                </Row>
                            </ColumnGroup>
                            <Column :sortable="true" field="location" header="LIEU" class="fosa_col font-medium"></Column>
                            <Column :sortable="true" field="effectif" header="EF. GN">
                                <template #body="{ data }">
                                    <div class="font-semibold">
                                        {{ data.effectif }}
                                    </div>
                                </template>
                            </Column>
                            <Column :sortable="true" field="effectif_actif" header="ACTIF" class="text-green-500 font-medium"></Column>
                            <Column :sortable="true" field="effectif_inactif" header="INACTIF" class="text-red-500 font-medium"></Column>
                            <Column :sortable="true" v-for="col of interval" :field="col.key" :header="col.local_abb" :key="col.key"></Column>
                            <Column :sortable="true" field="moyenne" header="MOYENNE" class="font-semibold"></Column>
                            <Column :sortable="true" field="com_int_perc" header="COMPLE. INTERNE %" class="text-blue-500 font-semibold"></Column>
                            <Column :sortable="true" field="taux_actif" header="COMPLE PRESTAT. ACTIF %" class="text-green-500 font-semibold"> </Column>
                            <Column :sortable="true" field="taux_general" header="COMPLE PRESTAT. GENE. %" class="text-orange-500 font-semibold"></Column>
                        </DataTable>
                    </TabPanel>
                    <TabPanel :key="2" :header="'Graphique'">
                        <div v-if="!loading" style="height: 300px">
                            <Chart type="bar" style="height: 300px" :plugins="plugins" :data="chartData" :options="chartOptions" />
                        </div>
                        <div v-if="loading">
                            <h5 class="mt-3">Chargement en cours ...</h5>
                            <Skeleton width="100%" height="150px"></Skeleton>
                        </div>
                    </TabPanel>
                </TabView>
            </div>
        </div>
    </div>
</template>
