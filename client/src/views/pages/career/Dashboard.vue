<script>
import { defineComponent } from 'vue';
import { useLayout } from '@/layout/composables/layout';
import DBCard from './DBCard.vue';
import apiService from '@/service/ApiService';
import VueApexCharts from 'vue3-apexcharts';
import xlsx from 'json-as-xlsx';
import PyarmidPath from './PyarmidPath.vue';
export default defineComponent({
    name: 'DashboardVue3',
    components: { DBCard, VueApexCharts, PyarmidPath },
    props: {
        title: { type: String, default: null }
    },

    data() {
        // from layout composable (Vue 3), keep reactive reference through getter
        const { layoutState, isDarkTheme } = useLayout();

        return {
            // layout
            layoutState,
            isDarkTheme,
            loading: false,
            // flags + errors
            loadingDashUtils: false,
            loadingError: null,

            // utilities summary
            utilsDashData: {
                effectif: null,
                admin: 0,
                retraite: 0,
                enactivite: 0,
                eligible_retaite: 0,
                dead: 0,
                validated: 0
            },

            // charts data & options
            recrutementSeries: [],
            chartOptionsCadreApexchart: null,
            chartOptionsCadreBarApexchart: null,
            chartOptionsPosition: null,
            chartOptionsPositionbar: null,
            chartOptionsDegreebar: null,
            chartOptionsDegree: null,
            chartOptionsAge: null,
            chartOptionsAgeLine: null,
            chartOptionsAgeGenderLine: null,
            chartOptionsAgeGender: null,

            staffChartOptions: null,
            staffEvolution: {
                series: [{ name: 'recrutement du staff', data: [31, 40, 28, 51, 42, 109, 100] }]
            },

            timesheetChartOptions: null,
            timesheetChartData: {
                series: [
                    { name: '', data: [31, 40, 28, 51, 42, 109, 100] },
                    { name: '', data: [31, 40, 28, 51, 42, 109, 100] }
                ]
            },

            categoryData: {
                labels: [],
                datasets: [{ label: 'Effectif par catégorie professionnelle', backgroundColor: '#ff6500', data: [] }]
            },

            employeePositionData: {
                labels: ['1960', '1965', '1970', '1975', '1980', '1985', '1990'],
                datasets: [{ label: 'Effectif', backgroundColor: '#42A5F5', data: [0, 0, 0, 0, 0, 0, 0] }]
            },

            degreeData: {
                labels: [],
                datasets: [{ label: "Effectif par niveau d'etude", backgroundColor: '#42A5F5', data: [] }]
            },

            genders: { m: 0, f: 0 },

            adstatut: {
                labels: ['Admis sous statut', 'Nouvelles unités'],
                datasets: [
                    {
                        data: [0, 0],
                        backgroundColor: ['#36A2EB', '#FF6384', '#FFCE56'],
                        hoverBackgroundColor: ['#36A2EB', '#FF6384', '#FFCE56']
                    }
                ]
            },

            agecurve: {
                labels: ['18-24 ans', '25-29 ans', '30-34 ans', '35-39 ans', '...'],
                datasets: [
                    { label: 'Admis sous statut', backgroundColor: '#38c172', data: [0, 0, 0, 0, 0], borderColor: '#38c172' },
                    { label: 'Nouvelles Unités', backgroundColor: '#FF6384', borderColor: '#FF6384', data: [0, 0, 0, 0, 0] }
                ]
            },

            toolbarOption: {
                show: true,
                tools: {
                    download: true,
                    selection: false,
                    zoom: false,
                    zoomin: false,
                    zoomout: false,
                    pan: false,
                    reset: false
                }
            },

            facility_data: [],
            facility_data_total: { base_list_max: 0, value: 0, progress: 0 }
        };
    },

    computed: {
        staticMenuDesktopInactive() {
            return this.layoutState.staticMenuDesktopInactive;
        }
    },

    watch: {
        '$store.state.blockReportPreview': function (newVal) {
            console.log('blocking', newVal);
            if (!newVal) {
                this.updateReport(this.$store.state.currentNode);
            }
        },

        // react to theme switch
        isDarkTheme: {
            handler(val) {
                if (val) this.applyDarkTheme();
                else this.applyLightTheme();
            },
            deep: false,
            immediate: true
        }
    },

    mounted() {
        this.getUtils();
    },
    expose: ['updateReport'],
    methods: {
        // ---------- helpers ----------
        exportTitle() {
            if (this.currentFacility) return this.currentFacility.label.toUpperCase();
            if (this.currentHA) return this.currentHA.label.toUpperCase();
            if (this.currentTR) return this.currentTR.label.toUpperCase();
            if (this.currentPR) return this.currentPR.label.toUpperCase();
            return 'NATIONAL';
        },
        exportFileName() {
            let name = '';
            if (this.currentFacility) name += ' - ' + this.currentFacility.label;
            if (this.currentHA) name += ' - ' + this.currentHA.label;
            if (this.currentTR) name += ' - ' + this.currentTR.label;
            if (this.currentPR) name += ' - ' + this.currentPR.label;
            if (name === '') name = 'NATIONAL';
            return name.toUpperCase();
        },
        mtitle(t = '') {
            return {
                text: `${t}${this.exportTitle()} (${new Date().toLocaleString('fr')})`,
                align: 'left',
                style: { fontSize: '12px', fontWeight: 'bold', color: '#3b82f6' }
            };
        },

        applyLightTheme() {
            // Put any global/light theming for your charts here if needed
            // Left in place to mirror your original watcher contract
        },
        applyDarkTheme() {
            // Put any global/dark theming for your charts here if needed
        },

        loadData() {
            const id = this.$store.state.currentNode;
            this.getUtils(id);
        },
        // ---------- core data loader ----------
        getUtils(orgUnitId) {
            if (!orgUnitId) return;
            if (this.loading) return;
            this.loading = true;
            this.loadingError = null;
            this.loadingDashUtils = true;
            const url = `/reports/dashboard?org_unit_id=${orgUnitId}`;

            apiService
                .get(url)
                .then((res) => {
                    // basic numbers
                    this.genders.m = res.data.gender.m;
                    this.genders.f = res.data.gender.f;

                    this.utilsDashData.effectif = res.data.effectif;
                    this.utilsDashData.admin = res.data.admin;
                    this.utilsDashData.retraite = res.data.retraite;
                    this.utilsDashData.enactivite = res.data.position_active;
                    this.utilsDashData.eligible_retaite = res.data.eligible_retaite || 0;
                    this.utilsDashData.dead = res.data.dead;
                    this.utilsDashData.validated = res.data.validated || 0;

                    // series
                    this.staffEvolution.series[0].data = res.data.recrutement.data;
                    this.staffEvolution.series[0].label = `Evolution du recrutement des staffs(${this.exportFileName()})`;
                    if (res.data.timesheet) {
                        this.timesheetChartData.series[0].data = res.data.timesheet.data.taux_general;
                        this.timesheetChartData.series[0].name = 'General';
                        this.timesheetChartData.series[1].data = res.data.timesheet.data.taux_actif;
                        this.timesheetChartData.series[1].name = 'Actif';
                    }
                    // tables
                    this.facility_data = res.data.facility_data || [];
                    this.facility_data_total.base_list_max = 0;
                    this.facility_data_total.value = 0;
                    this.facility_data_total.progress = 0;
                    this.facility_data.forEach((elt) => {
                        this.facility_data_total.base_list_max += elt.base_list_max;
                        this.facility_data_total.value += elt.value;
                    });
                    if (this.facility_data_total.base_list_max > 0) {
                        this.facility_data_total.progress = ((this.facility_data_total.value / this.facility_data_total.base_list_max) * 100).toFixed(2);
                    }

                    // misc datasets
                    this.categoryData.labels = res.data.classification.labels;
                    this.categoryData.datasets[0].data = res.data.classification.data;

                    this.employeePositionData.labels = res.data.position.labels;
                    this.employeePositionData.datasets[0].data = res.data.position.data;
                    this.degreeData.labels = res.data.degree.labels;
                    this.degreeData.datasets[0].data = res.data.degree.data;

                    // pies / bars labels
                    if (res.data.effectif > 0) {
                        const f = ((res.data.gender.f / res.data.effectif) * 100).toFixed(2) + ' %)';
                        const m = ((res.data.gender.m / res.data.effectif) * 100).toFixed(2) + ' %)';
                        const adminSS = ((res.data.effectif_adminSS / res.data.effectif) * 100).toFixed(2) + ' %)';
                        const nu = ((res.data.effectif_nu / res.data.effectif) * 100).toFixed(2) + ' %)';
                        this.adstatut.labels = ['Sous statut (' + res.data.effectif_adminSS + ' ou ' + adminSS, 'N.U (' + res.data.effectif_nu + ' ou' + nu];
                        //optional: update gender labels if you display them elsewhere
                        this.genders.labels = ['M (' + res.data.gender.m + ' ou ' + m, 'F (' + res.data.gender.f + ' ou ' + f];
                    }

                    // age curves
                    this.agecurve.datasets[0].data = res.data.agecurve.values.admis_statut;
                    this.agecurve.datasets[1].data = res.data.agecurve.values.nu;
                    this.agecurve.labels = res.data.agecurve.labels;

                    // compute chart options
                    this.getChartConfig(res);
                })
                .catch((err) => {
                    this.loadingError = err;
                    // console.error(err);
                })
                .finally(() => {
                    this.loading = false;
                    this.loadingDashUtils = false;
                });
        },

        // ---------- charts config (converted from .value to plain data props) ----------
        getChartConfig(res) {
            // ----- cadre (pie + bar)
            this.chartOptionsCadreApexchart = {
                chart: { type: 'pie', toolbar: { show: true } },
                title: this.mtitle('EFFECTIF PAR CATEGORIE PRO. - '),
                labels: res.data.classification.labels,
                responsive: [{ breakpoint: 480, options: { legend: { position: 'bottom' } } }]
            };

            this.chartOptionsCadreBarApexchart = {
                chart: { type: 'bar', height: 350, stacked: true },
                plotOptions: {
                    bar: {
                        horizontal: true,
                        dataLabels: { total: { enabled: true, offsetX: 30, offsetY: 6, style: { colors: ['#555'], fontSize: '10px', fontWeight: 400 } } }
                    }
                },
                dataLabels: { enabled: false, formatter: (val) => `${Math.abs(val)} (${((val / this.utilsDashData.effectif) * 100).toFixed(2)}%)` },
                colors: ['#41a0fc'],
                stroke: { width: 1, colors: ['#666'] },
                title: this.mtitle('EFFECTIF PAR CATEGORIE PRO. - '),
                xaxis: { categories: res.data.cadre.labels, labels: { show: false } },
                grid: { borderColor: '#ccc', strokeDashArray: 7, xaxis: { lines: { show: true } } },
                yaxis: { title: { text: undefined }, max: res.data.cadre.max * 1.25 },
                tooltip: { y: {} },
                fill: { opacity: 1 },
                legend: { position: 'top', horizontalAlign: 'left', offsetX: 40 }
            };

            // ----- position (pie + bar)
            this.chartOptionsPosition = {
                chart: { width: '100%', height: 350, type: 'pie', toolbar: { show: true } },
                title: this.mtitle('EFFECTIF PAR POSIT. ADMIN. - '),
                labels: res.data.position.labels,
                responsive: [{ breakpoint: 480, options: { legend: { position: 'bottom' } } }]
            };

            this.chartOptionsPositionbar = {
                chart: { type: 'bar', height: 350, stacked: true },
                plotOptions: {
                    bar: {
                        horizontal: true,
                        dataLabels: { total: { enabled: true, offsetX: 30, offsetY: 6, style: { colors: ['#555'], fontSize: '10px', fontWeight: 400 } } }
                    }
                },
                dataLabels: { enabled: false, formatter: (val) => `${Math.abs(val)} (${((val / this.utilsDashData.effectif) * 100).toFixed(2)}%)` },
                colors: ['#41a0fc'],
                stroke: { width: 1, colors: ['#666'] },
                title: this.mtitle('EFFECTIF PAR POSIT. ADMIN. - '),
                xaxis: { categories: res.data.position.labels, labels: { show: false } },
                grid: { borderColor: '#ccc', strokeDashArray: 7, xaxis: { lines: { show: true } } },
                yaxis: { title: { text: undefined }, max: res.data.position.max * 1.25 },
                tooltip: { y: {} },
                fill: { opacity: 1 },
                legend: { position: 'top', horizontalAlign: 'left', offsetX: 40 }
            };

            // ----- degree (pie + bar)
            this.chartOptionsDegree = {
                chart: { width: '100%', height: 350, stacked: true, type: 'pie', toolbar: { show: true } },
                title: this.mtitle("EFFECTIF PAR NIVEAU D'ETUDE - "),
                labels: res.data.degree.labels,
                responsive: [{ breakpoint: 380, options: { legend: { position: 'bottom' } } }]
            };

            this.chartOptionsDegreebar = {
                chart: { type: 'bar', height: 350, stacked: true },
                plotOptions: {
                    bar: {
                        horizontal: true,
                        dataLabels: { total: { enabled: true, offsetX: 30, offsetY: 6, style: { colors: ['#555'], fontSize: '10px', fontWeight: 400 } } }
                    }
                },
                dataLabels: { enabled: false, formatter: (val) => `${Math.abs(val)} (${((val / this.utilsDashData.effectif) * 100).toFixed(2)}%)` },
                colors: ['#41a0fc'],
                stroke: { width: 1, colors: ['#666'] },
                title: this.mtitle("EFFECTIF PAR NIVEAU D'ETUDE -"),
                xaxis: { categories: res.data.degree.labels, labels: { show: false } },
                grid: { borderColor: '#ccc', strokeDashArray: 7, xaxis: { lines: { show: true } } },
                yaxis: { title: { text: undefined }, max: res.data.degree.max * 1.25 },
                tooltip: { y: {} },
                fill: { opacity: 1 },
                legend: { position: 'top', horizontalAlign: 'left', offsetX: 40 }
            };

            // ----- age (line + diverging bar)
            this.chartOptionsAgeLine = {
                data: [
                    { name: 'ADMIS SOUS STATUT', data: res.data.agecurve.values.admis_statut },
                    { name: 'NOUVELLES UNITÉS', data: res.data.agecurve.values.nu }
                ],
                options: {
                    chart: { type: 'line', dropShadow: { enabled: true, color: '#000', top: 18, left: 7, blur: 10, opacity: 0.2 }, toolbar: this.toolbarOption },
                    colors: ['#008ffb', '#ff6384'],
                    dataLabels: { enabled: true },
                    stroke: { curve: 'smooth' },
                    title: this.mtitle("COURBE D'ÂGE - "),
                    grid: { borderColor: '#ccc', strokeDashArray: 7, xaxis: { lines: { show: true } } },
                    markers: { size: 1 },
                    xaxis: { categories: res.data.agecurve.labels },
                    yaxis: { min: 0, max: res.data.agecurve.max * 1.1, title: {} },
                    legend: { position: 'top', horizontalAlign: 'center', floating: true }
                }
            };

            const ageNeg = res.data.agecurve._values.admis_statut.map((v) => -v);
            this.chartOptionsAge = {
                data: [
                    { name: 'ADMIS SOUS STATUT', data: ageNeg },
                    { name: 'NOUVELLES UNITÉS', data: res.data.agecurve._values.nu }
                ],
                options: {
                    chart: { type: 'bar', stacked: true },
                    colors: ['#008FFB', '#ff5e78'],
                    legend: { show: true, position: 'top', floating: true, align: 'center' },
                    plotOptions: { bar: { horizontal: true, dataLabels: { position: 'top' } } },
                    dataLabels: {
                        enabled: true,
                        style: { colors: ['#555'], fontSize: '10px', fontWeight: 400 },
                        offsetX: 45,
                        formatter: (val) => `${Math.abs(val)} (${((Math.abs(val) / this.utilsDashData.effectif) * 100).toFixed(2)}%)`
                    },
                    stroke: { width: 1, colors: ['#666'] },
                    grid: { borderColor: '#ccc', strokeDashArray: 7, xaxis: { lines: { show: true } } },
                    yaxis: { min: -res.data.agecurve._max * 1.5, max: res.data.agecurve._max * 1.5, title: {} },
                    tooltip: { shared: false, x: { formatter: (v) => v }, y: { formatter: (v) => Math.abs(v) } },
                    title: this.mtitle("COURBE D'ÂGE - "),
                    xaxis: {
                        categories: res.data.agecurve._labels,
                        labels: { formatter: (val) => Math.abs(Math.round(val)) }
                    }
                }
            };

            // ----- age gender (line + diverging bar)
            this.chartOptionsAgeGenderLine = {
                data: [
                    { name: 'HOMMES', data: res.data.general_agecurve.values.mal },
                    { name: 'FEMMES', data: res.data.general_agecurve.values.fem }
                ],
                options: {
                    chart: {
                        height: 400,
                        type: 'line',
                        dropShadow: { enabled: true, color: '#000', top: 18, left: 7, blur: 10, opacity: 0.2 },
                        toolbar: this.toolbarOption
                    },
                    colors: ['#008ffb', '#ff6384'],
                    dataLabels: { enabled: true },
                    stroke: { curve: 'smooth' },
                    title: this.mtitle("COURBE D'ÂGE - "),
                    grid: { borderColor: '#ccc', strokeDashArray: 7, xaxis: { lines: { show: true } } },
                    markers: { size: 1 },
                    xaxis: { categories: res.data.general_agecurve.labels },
                    yaxis: { min: 0, max: res.data.general_agecurve.max * 1.1, tickAmount: 10, lines: { show: true }, title: {} },
                    legend: { position: 'top', horizontalAlign: 'center', floating: true }
                }
            };

            const maleNeg = res.data.general_agecurve._values.mal.map((v) => -v);
            this.chartOptionsAgeGender = {
                data: [
                    { name: 'HOMMES', data: maleNeg },
                    { name: 'FEMMES', data: res.data.general_agecurve._values.fem }
                ],
                options: {
                    chart: { type: 'bar', stacked: true },
                    colors: ['#008FFB', '#ff5e78'],
                    legend: { show: true, position: 'top', floating: true, align: 'center' },
                    plotOptions: { bar: { horizontal: true, dataLabels: { position: 'top' } } },
                    dataLabels: {
                        enabled: true,
                        style: { colors: ['#555'], fontSize: '10px', fontWeight: 400 },
                        offsetX: 45,
                        formatter: (val) => `${Math.abs(val)} (${((Math.abs(val) / this.utilsDashData.effectif) * 100).toFixed(2)}%)`
                    },
                    stroke: { width: 1, colors: ['#555'] },
                    grid: { borderColor: '#ccc', strokeDashArray: 7, xaxis: { lines: { show: true } } },
                    yaxis: { min: -res.data.general_agecurve._max * 1.5, max: res.data.general_agecurve._max * 1.5, title: {} },
                    tooltip: { shared: false, x: { formatter: (v) => v }, y: { formatter: (v) => Math.abs(v) } },
                    title: this.mtitle("COURBE D'ÂGE - "),
                    xaxis: {
                        categories: res.data.general_agecurve._labels,
                        labels: { formatter: (val) => Math.abs(Math.round(val)) }
                    }
                }
            };

            // ----- staff & timesheet (area)

            this.staffChartOptions = {
                chart: { height: 350, type: 'area', toolbar: this.toolbarOption },
                title: this.mtitle(),
                grid: { borderColor: '#ccc', strokeDashArray: 7 },
                dataLabels: { enabled: false },
                stroke: { curve: 'smooth' },
                yaxis: { type: 'number', tickAmount: 10, lines: { show: true } },
                xaxis: { tickPlacement: 'on', type: 'number', tickAmount: 20, categories: res.data.recrutement.labels, lines: { show: true } }
            };
            console.log(this.staffChartOptions);

            if (res.data.timesheet) {
                this.timesheetChartOptions = {
                    chart: { height: 350, type: 'area', toolbar: this.toolbarOption },
                    title: this.mtitle(),
                    dataLabels: { enabled: true },
                    grid: { borderColor: '#ccc', strokeDashArray: 7, xaxis: { lines: { show: true } } },
                    stroke: { curve: 'smooth' },
                    yaxis: { type: 'number', tickAmount: 10, lines: { show: true } },
                    colors: ['#00E396', '#008FFB'],
                    xaxis: { tickPlacement: 'on', type: 'number', tickAmount: 20, categories: res.data.timesheet.labels }
                };
            }
        },

        // ---------- export ----------
        downloadFacility_data() {
            if (!this.facility_data.length) return;

            const settings = {
                fileName: 'IHRIS EFFECTIF PAR ZS - ' + ' - ' + new Date().toLocaleString(),
                writeMode: 'writeFile',
                RTL: false
            };

            const data = [
                {
                    sheet: 'EFFECTIF',
                    columns: [
                        { label: 'ID', value: 'id' },
                        { label: 'ZONE DE SANTE', value: 'name' },
                        { label: 'EFFECTIF DECLARE', value: 'base_list_max' },
                        { label: 'EFFECTIF ENCODE', value: 'value' },
                        { label: "TAUX D'ENCODAGE", value: 'progression' }
                    ],
                    content: this.facility_data
                }
            ];

            xlsx(data, settings);
        },

        // method to be called by parent via $refs.child.updateReport()
        updateReport(node) {
            this.getUtils(node);
        }
    }
});
</script>

<template>
    <div class="grid dashboard">
       <div style="margin: 5px;" class="col-12">
         <PyarmidPath :reload="loadData"/>
       </div>
        <!-- Cards -->
        <div class="col-12 lg:col-6 xl:col-3">
            <DBCard
                title="EFFECTIF"
                :subtitle="utilsDashData.effectif"
                :meter="genders.m"
                :meter1="genders.f"
                filter="all"
                footer="100"
                subfooter="Validés"
                :loading="loadingDashUtils"
                :currentPR="currentPR"
                :currentTR="currentTR"
                :currentHA="currentHA"
                :currentFacility="currentFacility"
            />
        </div>

        <div class="col-12 lg:col-6 xl:col-3">
            <DBCard
                title="EFFECTIF VALIDÉ"
                :subtitle="utilsDashData.validated"
                :meter="utilsDashData.effectif"
                filter="validated"
                subfooter="dossiers validés"
                :loading="loadingDashUtils"
                :currentPR="currentPR"
                :currentTR="currentTR"
                :currentHA="currentHA"
                :currentFacility="currentFacility"
            />
        </div>

        <div class="col-12 lg:col-6 xl:col-3">
            <DBCard
                title="ADMINISTRATIFS"
                :subtitle="utilsDashData.admin"
                :meter="utilsDashData.effectif"
                filter="admin"
                :loading="loadingDashUtils"
                :currentPR="currentPR"
                :currentTR="currentTR"
                :currentHA="currentHA"
                :currentFacility="currentFacility"
            />
        </div>

        <div class="col-12 lg:col-6 xl:col-3">
            <DBCard
                title="PRO. SANTÉ "
                :subtitle="utilsDashData.effectif - utilsDashData.admin"
                :meter="utilsDashData.effectif"
                filter="prosante"
                :loading="loadingDashUtils"
                :currentPR="currentPR"
                :currentTR="currentTR"
                :currentHA="currentHA"
                :currentFacility="currentFacility"
            />
        </div>

        <div class="col-12 lg:col-6 xl:col-3">
            <DBCard
                title="EN ACTIVITÉ"
                :subtitle="utilsDashData.enactivite"
                :meter="utilsDashData.effectif"
                filter="activite"
                :loading="loadingDashUtils"
                :currentPR="currentPR"
                :currentTR="currentTR"
                :currentHA="currentHA"
                :currentFacility="currentFacility"
            />
        </div>

        <div class="col-12 lg:col-6 xl:col-3">
            <DBCard
                title="ÉLIGIBLE À LA RETRAITE"
                :subtitle="utilsDashData.eligible_retaite"
                :meter="utilsDashData.effectif"
                filter="eligible_retraite"
                :loading="loadingDashUtils"
                :currentPR="currentPR"
                :currentTR="currentTR"
                :currentHA="currentHA"
                :currentFacility="currentFacility"
            />
        </div>

        <div class="col-12 lg:col-6 xl:col-3">
            <DBCard
                title="RETRAITÉS"
                filter="retraite"
                :subtitle="utilsDashData.retraite"
                :meter="utilsDashData.effectif"
                :loading="loadingDashUtils"
                :currentPR="currentPR"
                :currentTR="currentTR"
                :currentHA="currentHA"
                :currentFacility="currentFacility"
            />
        </div>

        <div class="col-12 lg:col-6 xl:col-3">
            <DBCard title="DÉCÉDÉS" filter="dead" :subtitle="utilsDashData.dead" :meter="utilsDashData.effectif" :loading="loadingDashUtils" :currentPR="currentPR" :currentTR="currentTR" :currentHA="currentHA" :currentFacility="currentFacility" />
        </div>

        <!-- Staff evolution -->
        <div class="col-12 xl:col-6">
            <div class="card">
                <h5 class="ml-2 mb-1" v-if="!loadingDashUtils">EVOLUTION DU RECRUTEMENT DES STAFFS (Date engagement)</h5>
                <Skeleton v-if="loadingDashUtils" class="mb-0" width="100%" height="17px" />
                <TabView>
                    <TabPanel header="Graphique à barres">
                        <div v-if="staffChartOptions">
                            <VueApexCharts type="area" height="350" :options="staffChartOptions" :series="staffEvolution.series" />
                        </div>
                    </TabPanel>
                    <TabPanel header="Tableau">
                        <div v-if="staffChartOptions && staffEvolution.series && staffEvolution.series.length > 0" style="height: 300px; overflow-y: scroll">
                            <table class="table">
                                <tr v-for="(data, index) in staffEvolution.series[0].data" :key="index">
                                    <td>{{ staffChartOptions['xaxis'].categories[index] }}</td>
                                    <td>{{ data }}</td>
                                </tr>
                            </table>
                        </div>
                    </TabPanel>
                </TabView>
            </div>
        </div>

        <!-- Cadre (category) -->
        <div class="col-12 xl:col-6">
            <div class="card card-db">
                <div class="card-body">
                    <h5 class="ml-2 mb-0" v-if="!loadingDashUtils">EFFECTIF PAR CATÉGORIE PROFESSIONNELLE</h5>
                    <Skeleton v-if="loadingDashUtils" class="mb-0" width="100%" height="17px" />
                    <TabView>
                        <TabPanel header="Graphiques circulaire">
                            <div v-if="chartOptionsCadreApexchart" width="100%" style="min-height: 200px;">
                                <VueApexCharts type="pie" :options="chartOptionsCadreApexchart" :series="categoryData.datasets[0].data" />
                            </div>
                        </TabPanel>
                        <TabPanel header="Graphiques à colonnes">
                            <div v-if="chartOptionsCadreBarApexchart">
                                <VueApexCharts type="bar" :options="chartOptionsCadreBarApexchart" :series="[{ name: 'Effectif', data: categoryData.datasets[0].data }]" />
                            </div>
                        </TabPanel>

                        <TabPanel header="Tableau">
                            <div v-if="chartOptionsCadreApexchart && categoryData.datasets.length > 0">
                                <h5 class="text-primary">{{ chartOptionsCadreApexchart.title.text }}</h5>
                                <div style="'height:200px">
                                    <table class="table">
                                    <template v-for="(cat, i) in chartOptionsCadreApexchart.labels" :key="cat">
                                        <tr>
                                            <td>{{ cat }}</td>
                                            <td class="text-right">{{ categoryData.datasets[0].data[i] }}</td>
                                        </tr>
                                    </template>
                                </table>
                                </div>
                            </div>
                        </TabPanel>
                    </TabView>
                </div>
            </div>
        </div>

        <!-- Age - Gender -->
        <div class="col-12" :class="{ 'xl:col-4': staticMenuDesktopInactive, 'xl:col-6 ': !staticMenuDesktopInactive }">
            <div class="card">
                <h5 class="ml-2 mb-1" v-if="!loadingDashUtils">COURBE D'ÂGE - GENRE</h5>

                <Skeleton v-if="loadingDashUtils" class="mb-0" width="100%" />
                <TabView>
                    <TabPanel header="Graphique à barres">
                        <div v-if="chartOptionsAgeGender">
                            <VueApexCharts type="bar" :options="chartOptionsAgeGender.options" :series="chartOptionsAgeGender.data" />
                        </div>
                    </TabPanel>
                    <TabPanel header="Graphique en courbe">
                        <div v-if="chartOptionsAgeGenderLine">
                            <VueApexCharts type="line" :options="chartOptionsAgeGenderLine.options" :series="chartOptionsAgeGenderLine.data" />
                        </div>
                    </TabPanel>

                    <TabPanel header="Tableau">
                        <div v-if="chartOptionsAgeGender && chartOptionsAgeGender.options && staffEvolution.series && staffEvolution.series.length > 0" style="height: 300px; overflow-y:scroll">
                            <table class="table">
                                <tr v-for="(data, index) in chartOptionsAgeGender.data[0].data" :key="index">
                                    <td>{{ chartOptionsAgeGender.options['xaxis'].categories[index] }}</td>
                                    <td>{{ Math.abs(data) }}</td>
                                </tr>
                            </table>
                        </div>
                    </TabPanel>
                </TabView>
            </div>
        </div>

        <!-- Age - NU vs Statut -->
        <div class="col-12" :class="{ 'xl:col-4': staticMenuDesktopInactive, 'xl:col-6 ': !staticMenuDesktopInactive }">
            <div class="card">
                <div class="card-body card-db">
                    <h5 class="ml-2 mb-1" v-if="!loadingDashUtils">{{ "COURBE D'ÂGE - NOUVELLES UNITÉS & ADMIS SOUS STATUT" }}</h5>
                    <Skeleton v-if="loadingDashUtils" class="mb-0" width="100%" />
                    <TabView>
                        <TabPanel header="Graphique à barres">
                            <div v-if="chartOptionsAge">
                                <VueApexCharts type="bar" :options="chartOptionsAge.options" :series="chartOptionsAge.data" />
                            </div>
                        </TabPanel>
                        <TabPanel header="Graphique en courbe">
                            <div v-if="chartOptionsAgeLine">
                                <VueApexCharts type="line" :options="chartOptionsAgeLine.options" :series="chartOptionsAgeLine.data" />
                            </div>
                        </TabPanel>
                    </TabView>
                </div>
            </div>
        </div>

        <!-- Degree -->
        <div class="col-12" :class="{ 'xl:col-4': staticMenuDesktopInactive, 'xl:col-6 ': !staticMenuDesktopInactive }">
            <div class="card">
                <h5 class="ml-2 mb-0" v-if="!loadingDashUtils">EFFECTIF PAR NIVEAU D'ÉTUDE</h5>
                <Skeleton v-if="loadingDashUtils" class="mb-0" width="100%" />
                <TabView>
                    <TabPanel header="Graphique à colonnes">
                        <div v-if="chartOptionsDegreebar">
                            <VueApexCharts type="bar" :options="chartOptionsDegreebar" :series="[{ name: 'Effectif', data: degreeData.datasets[0].data }]" />
                        </div>
                    </TabPanel>
                    <TabPanel header="Graphique circulaire">
                        <div v-if="chartOptionsDegree">
                            <VueApexCharts type="pie" :options="chartOptionsDegree" :series="degreeData.datasets[0].data" />
                        </div>
                    </TabPanel>

                    <TabPanel header="Tableau">
                        <div v-if="chartOptionsDegreebar && degreeData.datasets.length > 0">
                            <h5 class="text-primary">{{ chartOptionsDegreebar.title.text }}</h5>
                            <table class="table">
                                <template v-for="(cat, i) in degreeData.labels" :key="cat">
                                    <tr>
                                        <td>{{ cat }}</td>
                                        <td class="text-right">{{ degreeData.datasets[0].data[i] }}</td>
                                    </tr>
                                </template>
                            </table>
                        </div>
                    </TabPanel>
                </TabView>
            </div>
        </div>

        <!-- Timesheet -->
        <div class="col-12 xl:col-6">
            <div class="card">
                <h5 class="ml-2 mb-1" v-if="!loadingDashUtils">COMPTÉTUDE DE PRESTATIONS</h5>
                <Skeleton v-if="loadingDashUtils" class="mb-0" width="100%" height="17px" />

                <div v-if="timesheetChartOptions">
                    <VueApexCharts type="area" height="350" :options="timesheetChartOptions" :series="timesheetChartData.series" />
                </div>
            </div>
        </div>

        <!-- Position admin -->
        <div class="col-12" :class="{ 'xl:col-4 md:col-6': staticMenuDesktopInactive, 'xl:col-6 ': !staticMenuDesktopInactive }">
            <div class="card card-db">
                <div class="card-body">
                    <h5 class="ml-2 mb-0" v-if="!loadingDashUtils">EFFECTIF PAR POSITION ADMINISTRATIVE</h5>
                    <Skeleton v-if="loadingDashUtils" class="mb-0" width="100%" />
                    <TabView>
                        <TabPanel header="Graphique à colonnes">
                            <div v-if="chartOptionsPositionbar">
                                <VueApexCharts type="bar" :options="chartOptionsPositionbar" :series="[{ name: 'Effectif', data: employeePositionData.datasets[0].data }]" />
                            </div>
                        </TabPanel>
                        <TabPanel header="Graphique circulaire">
                            <div v-if="chartOptionsPosition">
                                <VueApexCharts type="pie" :options="chartOptionsPosition" :series="employeePositionData.datasets[0].data" />
                            </div>
                        </TabPanel>
                    </TabView>
                </div>
            </div>
        </div>

        <!-- Facility table -->
        <div class="col-12" :class="{ 'xl:col-4 md:col-6': staticMenuDesktopInactive, 'xl:col-6 ': !staticMenuDesktopInactive }">
            <div v-if="!currentFacility">
                <div class="card card-db" v-if="currentPR && currentPR.key === 'district|2'">
                    <div class="card-body dashboard">
                        <div class="grid mb-0">
                            <div class="col pb-0">
                                <h5 class="ml-2 mb-1" v-if="!loadingDashUtils">EFFECTIF PAR STRUCTURES</h5>
                            </div>
                            <div class="col text-right pb-0">
                                <Button @click="downloadFacility_data()" :disabled="!facility_data.length" class="float-right" icon="pi pi-download" text rounded aria-label="Télécharger" v-tooltip.top="'Télécharger'" />
                            </div>
                        </div>

                        <DataTable :value="facility_data" stripedRows showGridlines :loading="loadingDashUtils" :rows="13" paginator size="small" tableStyle="min-width: 50rem">
                            <ColumnGroup type="header">
                                <Row>
                                    <Column sortable field="name" header="Zone de santé" :rowspan="2" />
                                    <Column header="Effectif" :colspan="2" style="text-align: center" />
                                    <Column sortable field="progression" header="Taux d'encodage" :rowspan="2" />
                                </Row>
                                <Row>
                                    <Column sortable field="base_list_max" header="Déclaré" />
                                    <Column sortable field="value" header="Encodé" />
                                </Row>
                            </ColumnGroup>

                            <Column field="name" sortable footer="TOTAL" header="ZONE DE SANTE" />
                            <Column field="base_list_max" sortable :footer="facility_data_total.base_list_max" class="text-right" style="width: 25px" />
                            <Column field="value" sortable :footer="facility_data_total.value" class="text-right" style="width: 25px" />
                            <Column field="progression" :footer="facility_data_total.progress + ' %'" sortable class="text-right" style="width: 25px">
                                <template #body="{ data }">
                                    <span>{{ Number(data.progression).toFixed(2) }} %</span>
                                </template>
                            </Column>
                        </DataTable>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<style lang="css" scoped>
.table {
    width: 100%;
    background-color: #ddd;
}
.table td {
    background-color: #fff;
}
</style>
