<script setup>
import { ref } from 'vue';
import { FilterMatchMode } from '@primevue/core/api';
import apiService from '@/service/ApiService';
import _AppCache from '../../../service/appCache';

const props = defineProps({
    currentPR: { type: Object, default: null },
    currentTR: { type: Object, default: null },
    currentHA: { type: Object, default: null },
    currentFacility: { type: Object, default: null },
    title: { type: String, default: null },
    submenu_position: { type: Number, default: 0 }
});

const currentNode = ref(null);
const error = ref(null);
const interval = ref([]);
const subdata = ref([]);
const startDate = ref(new Date());
const endDate = ref(new Date());
const zsFilter = ref(false);
const reportUrl = ref(null);
const selectedOption = ref({ name: 'Mois', code: 1 });
const selectionInterval = ref(3);
const loading = ref(false);
const filters2 = ref({
    fosa: { value: null, matchMode: FilterMatchMode.CONTAINS }
});
const products = ref([]);

/* ---------- helpers: numbers, currency, percent, date ---------- */
const toNum = (v) => {
    const n = Number(v);
    return Number.isFinite(n) ? n : 0;
};
const round2 = (v) => Number(toNum(v).toFixed(2)); // stays a Number
const formatUSD = (v) =>
    new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(toNum(v));
const formatPercent = (v) => toNum(v).toFixed(2); // returns "12.34" for display
const toYMD = (d) => {
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
};
/* -------------------------------------------------------------- */

const subDataSum = (i) => {
    let res = 0;
    subdata.value.forEach((elt) => {
        if (i === 1) res += toNum(elt.ips);
        else res += toNum(elt.dps);
    });
    return toNum(res).toFixed(2);
};

const onclickGetReport = () => {
    currentNode.value = _AppCache.getCurrentNode();
    if (!currentNode.value) return;
    loading.value = true;
    const baseUrl = '/reports/performance_bonus_calc';
    reportUrl.value = `${baseUrl}?org_unit_id=${currentNode.value}&start_date=${toYMD(startDate.value)}&end_date=${toYMD(endDate.value)}&selectOption=${selectedOption.value.code}&selectionInterval=${selectionInterval.value}&zs_filter=${
        zsFilter.value ? 1 : 0
    }`;

    apiService
        .get(reportUrl.value)
        .then((res) => {
            error.value = null;
            products.value = [];

            subdata.value = [
                {
                    no: 1,
                    indicator: 'Complétude générale de toutes les ZS',
                    prop: 40,
                    perc: round2(res.data.subdata.timesheet_perc_gen),
                    ips: round2(res.data.subdata.bonus_ips_comp_timesheet),
                    dps: round2(res.data.subdata.bonus_dps_comp_timesheet),
                    tag: ''
                },
                {
                    no: 2,
                    indicator: 'Complétude interne données carrière',
                    prop: 30,
                    perc: round2(res.data.subdata.career_data_comp_perc),
                    ips: round2(res.data.subdata.bonus_ips_career),
                    dps: round2(res.data.subdata.bonus_dps_career),
                    tag: 'Qualité des données'
                },
                {
                    no: 3,
                    indicator: 'Complétude interne données prestation',
                    prop: 30,
                    perc: round2(res.data.subdata.timesheet_com_int_perc),
                    ips: round2(res.data.subdata.bonus_ips_int_timesheet),
                    dps: round2(res.data.subdata.bonus_dps_int_timesheet),
                    tag: 'Qualité des données'
                }
            ];

            interval.value = res.data.intervals;

            res.data.report.data.forEach((elt, idx) => {
                // stable numeric transforms (no strings)
                const effectif_gen = toNum(elt.effectif_gen);
                const effectif_actif = toNum(elt.effectif_actif);

                elt.id = idx + 1; // dataKey can use this, or switch to facility_id if you prefer stability across reloads
                elt.effectif = effectif_gen;
                elt.effectif_inactif = effectif_gen - effectif_actif;

                elt.timesheet_average = round2(elt.timesheet_average);
                elt.timesheet_perc_gen = round2(elt.timesheet_perc_gen);
                elt.timesheet_perc_actif = round2(elt.timesheet_perc_actif);
                elt.timesheet_com_int_perc = round2(elt.timesheet_com_int_perc);
                elt.career_data_comp_perc = round2(elt.career_data_comp_perc);

                elt.perfomance_bonus_com_career = round2(elt.perfomance_bonus_com_career);
                elt.perfomance_bonus_com_int_timesheet = round2(elt.perfomance_bonus_com_int_timesheet);
                elt.perfomance_bonus_com_timesheet = round2(elt.perfomance_bonus_com_timesheet);
                elt.perfomance_bonus_total = round2(elt.perfomance_bonus_total);

                products.value.push(elt);
            });
        })
        .catch((err) => {
            error.value = err?.message || String(err);
            console.log(err);
        })
        .finally(() => {
            loading.value = false;
        });
};

const downloadFile = ref(false);
const download = () => {
    downloadFile.value = true;
    apiService
        .get(reportUrl.value + '&download=1', { responseType: 'arraybuffer' })
        .then((res) => {
            const headerLine = res.headers['content-disposition'] || '';
            const startFileNameIndex = headerLine.indexOf('"') + 1;
            const endFileNameIndex = headerLine.lastIndexOf('"');
            const filename = headerLine.substring(startFileNameIndex, endFileNameIndex) || 'report.pdf';
            const link = document.createElement('a');
            link.href = window.URL.createObjectURL(new Blob([res.data]));
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        })
        .catch((err) => {
            console.log(err);
            alert('Erreur: ' + (err?.message || String(err)));
        })
        .finally(() => {
            downloadFile.value = false;
        });
};

const updateReport = (orgUnitId) => {
    currentNode.value = orgUnitId;
    onclickGetReport();
};

defineExpose({ updateReport });
</script>

<template>
    <div class="card">
        <h4>PERFORMANCE ET PRIME</h4>
        <div>
            <div class="grid">
                <div class="col-6 sm:col-4 md:col-3 lg:col-2">
                    <label for="startDate">Début:</label>
                    <Calendar v-model="startDate" :show-icon="true" dateFormat="dd/mm/yy" class="p-inputtext-sm w-full" />
                </div>
                <div class="col-6 sm:col-4 md:col-3 lg:col-2">
                    <label for="endDate">Fin:</label>
                    <Calendar v-model="endDate" :show-icon="true" dateFormat="dd/mm/yy" class="p-inputtext-sm w-full" />
                </div>
                <div class="col-12 sm:col-4 md:col-6 lg:col-8 text-right">
                    <br />
                    <Button @click="onclickGetReport()" label="ACTUALISER" :loading="loading" :disabled="downloadFile" icon="pi pi-refresh" class="p-button-primary p-button-sm" />
                </div>
            </div>

            <div class="mt-4">
                <div v-if="products.length == 0 && loading" class="mt-4 pt-4">
                    <ScaleLoader color="#007bff" />
                    <p class="text-center">Chargement ....</p>
                </div>

                <div v-if="error != null && !loading" class="row">
                    <div class="col-sm-3"></div>
                    <div class="col-sm-6 text-center m-4">
                        <div class="alert alert-danger text-center" role="alert">
                            <h4>Échec de connexion</h4>
                            <p>{{ error }}</p>
                            <hr />
                            <Button @click="onclickGetReport()" label="Réessayer" class="p-button-danger p-button-sm" />
                        </div>
                    </div>
                </div>

                <Message v-if="products.length == 0 && !loading && error == null && currentPR != null" severity="info"> <b>Aucune donnée</b>, liste vide </Message>

                <div v-if="error == null && products.length > 0">
                    <h5>PRIME DE PERFORMANCE DES ZS, DPS ET IPS</h5>
                    <p>
                        <b>Échéance: </b>
                        <b class="text-info" v-for="col of interval" :key="col.key">{{ col.local_abb }}, </b>
                    </p>

                    <DataTable
                        :value="products"
                        stripedRows
                        showGridlines
                        class="p-datatable-sm"
                        :paginator="false"
                        responsiveLayout="scroll"
                        :scrollable="true"
                        dataKey="id"
                        v-model:filters="filters2"
                        filterDisplay="menu"
                        scrollHeight="600px"
                        :loading="loading"
                        :globalFilterFields="['fosa']"
                        :resizableColumns="true"
                        columnResizeMode="fit"
                        ref="dt"
                    >
                        <template #header>
                            <div class="grid">
                                <div class="sm:col-6">
                                    <IconField iconPosition="left">
                                        <InputIcon class="pi pi-search" />
                                        <InputText v-model="filters2['fosa'].value" placeholder="Rechercher ..." />
                                    </IconField>
                                </div>
                                <div class="sm:col-6 text-right">
                                    <Button @click="download()" label="TÉLÉCHARGER PDF" :loading="downloadFile" icon="pi pi-download" class="p-button-success p-button-sm p-button-outlined p-button ml-2 mb-3" iconPos="right" />
                                </div>
                            </div>
                        </template>

                        <ColumnGroup type="header">
                            <Row>
                                <Column header="LIEUX" :rowspan="3" style="width: 199px" />
                                <Column header="EFFECTIFS" :colspan="3" :rowspan="2" style="width: 240px; text-align: center" />
                                <Column header="COMPLÉTUDE DE PRESTATION" :colspan="2" :rowspan="2" style="max-width: 200px; text-align: center" />
                                <Column header="COMPLÉTUDE INTERNE" :colspan="2" :rowspan="2" style="max-width: 190px; text-align: center" />
                                <Column header="PRIME DE PERFORMANCE" style="max-width: 190px; text-align: center" field="perfomance_bonus" :colspan="4" />
                            </Row>
                            <Row>
                                <Column :sortable="true" :rowspan="2" header="T. RAPPORTAGE" style="text-align: center" field="perfomance_bonus_com_timesheet" />
                                <Column header="COMPLÉTUDE INTERNE" style="text-align: center" field="perfomance_bonus" :colspan="2" />
                                <Column :sortable="true" :rowspan="2" header="TOTAL" field="perfomance_bonus_total" style="text-align: center" />
                            </Row>
                            <Row>
                                <Column :sortable="true" header="GÉNÉRAL" field="effectif" style="width: 80px" />
                                <Column :sortable="true" header="ACTIF" field="effectif_actif" style="width: 80px" />
                                <Column :sortable="true" header="INACTIF" field="effectif_inactif" style="width: 80px" />

                                <Column :sortable="true" header="ACTIF" style="max-width: 85px" field="timesheet_perc_actif" />
                                <Column :sortable="true" header="GÉNÉRAL" style="max-width: 85px" field="timesheet_perc_gen" />

                                <Column :sortable="true" header="CARRIÈRE" style="max-width: 100px" field="career_data_comp_perc" />
                                <Column :sortable="true" header="PRESTATION" style="max-width: 100px" field="timesheet_com_int_perc" />

                                <Column :sortable="true" header="CARRIÈRE" field="perfomance_bonus_com_career" />
                                <Column :sortable="true" header="PRESTATION" field="perfomance_bonus_com_int_timesheet" />
                            </Row>
                        </ColumnGroup>

                        <Column :sortable="true" field="location" header="LIEU" class="fosa_col" />
                        <Column :sortable="true" style="max-width: 80px" field="effectif" header="EF. GN" class="justify-content-end font-bold w-full" />
                        <Column :sortable="true" style="max-width: 80px" field="effectif_actif" header="ACTIF" class="justify-content-end w-full" />
                        <Column :sortable="true" style="max-width: 80px" field="effectif_inactif" header="INACTIF" class="text-danger justify-content-end w-full" />

                        <Column :sortable="true" style="width: 90px" field="timesheet_perc_actif" header="COMPLE. PRESTATION ACTIF %" class="justify-content-end w-full">
                            <template #body="slotProps">{{ formatPercent(slotProps.data.timesheet_perc_actif) }} %</template>
                        </Column>
                        <Column :sortable="true" style="width: 90px" field="timesheet_perc_gen" header="COMPLE. PRESTATION GÉNÉRALE %" class="justify-content-end w-full">
                            <template #body="slotProps">{{ formatPercent(slotProps.data.timesheet_perc_gen) }} %</template>
                        </Column>
                        <Column :sortable="true" style="width: 90px" field="career_data_comp_perc" header="COMPLE. INTERNE CARRIÈRE %" class="justify-content-end w-full">
                            <template #body="slotProps">{{ formatPercent(slotProps.data.career_data_comp_perc) }} %</template>
                        </Column>
                        <Column :sortable="true" style="width: 90px" field="timesheet_com_int_perc" header="COMPLE. INTERNE PRESTATION %" class="justify-content-end w-full">
                            <template #body="slotProps">{{ formatPercent(slotProps.data.timesheet_com_int_perc) }} %</template>
                        </Column>

                        <Column :sortable="true" field="perfomance_bonus_com_timesheet" header="PRIME" class="text-info justify-content-end font-bold w-full">
                            <template #body="slotProps">{{ formatUSD(slotProps.data.perfomance_bonus_com_timesheet) }}</template>
                        </Column>
                        <Column :sortable="true" style="width: 90px" field="perfomance_bonus_com_career" header="PRIME" class="text-info justify-content-end font-bold w-full">
                            <template #body="slotProps">{{ formatUSD(slotProps.data.perfomance_bonus_com_career) }}</template>
                        </Column>
                        <Column :sortable="true" field="perfomance_bonus_com_int_timesheet" header="PRIME" class="text-info flex justify-content-end font-bold w-full">
                            <template #body="slotProps">{{ formatUSD(slotProps.data.perfomance_bonus_com_int_timesheet) }}</template>
                        </Column>
                        <Column :sortable="true" field="perfomance_bonus_total" header="PRIME" class="justify-content-end font-bold w-full">
                            <template #body="slotProps">{{ formatUSD(slotProps.data.perfomance_bonus_total) }}</template>
                        </Column>
                    </DataTable>

                    <br /><br />
                    <h5 style="text-center">PRIME D’ACCOMPAGNEMENT DES ZS PAR LA DPS ET IPS</h5>
                    <br />

                    <DataTable
                        :value="subdata"
                        stripedRows
                        showGridlines
                        class="p-datatable-sm"
                        :paginator="false"
                        :rows="40"
                        responsiveLayout="scroll"
                        :scrollable="true"
                        dataKey="no"
                        filterDisplay="menu"
                        scrollHeight="600px"
                        :loading="loading"
                        :resizableColumns="true"
                        columnResizeMode="fit"
                        ref="dt"
                    >
                        <ColumnGroup type="header">
                            <Row>
                                <Column header="No" field="no" :rowspan="3" style="width: 30px" />
                                <Column header="INDICATEURS" field="indicator" :rowspan="3" style="width: 449px" />
                                <Column header="TAUX" field="perc" :rowspan="3" style="text-align: center; width: 120px" />
                                <Column header="PRIME (IPS)" field="ips" :colspan="2" style="text-align: center" />
                                <Column header="PRIME (DPS)" field="dps" :colspan="2" style="text-align: center" />
                            </Row>
                            <Row>
                                <Column header="PROPORTION (100$)" style="text-align: center" />
                                <Column header="MONTANT" style="text-align: center" />
                                <Column header="PROPORTION (200$)" style="text-align: center" />
                                <Column header="MONTANT" style="text-align: center" />
                            </Row>
                        </ColumnGroup>

                        <Column :sortable="true" field="no" style="max-width: 30px" />
                        <Column :sortable="true" field="indicator" style="min-width: 450px">
                            <template #body="slotProps">
                                <b v-if="slotProps.data.tag != ''">{{ slotProps.data.tag }}:</b>
                                {{ slotProps.data.indicator }}
                            </template>
                        </Column>
                        <Column :sortable="true" field="perc" class="justify-content-center" style="max-width: 120px">
                            <template #body="slotProps">{{ formatPercent(slotProps.data.perc) }} %</template>
                        </Column>
                        <Column :sortable="true" field="prop" class="justify-content-center" style="max-width: 178px">
                            <template #body="slotProps">{{ slotProps.data.prop }} %</template>
                        </Column>
                        <Column :sortable="true" field="ips" class="justify-content-center text-info" style="max-width: 178px">
                            <template #body="slotProps">{{ formatUSD(slotProps.data.ips) }}</template>
                        </Column>
                        <Column :sortable="true" field="prop" class="justify-content-center" style="max-width: 178px">
                            <template #body="slotProps">{{ slotProps.data.prop }} %</template>
                        </Column>
                        <Column :sortable="true" field="dps" class="justify-content-center text-info" style="max-width: 178px">
                            <template #body="slotProps">{{ formatUSD(slotProps.data.dps) }}</template>
                        </Column>

                        <ColumnGroup type="footer">
                            <Row>
                                <Column footer="TOTAL:" :colspan="3" footerStyle="text-align:right" style="width: 600px" />
                                <Column footer="100 %" footerStyle="text-align:center" />
                                <Column :footer="formatUSD(Number(subDataSum(1)))" footerStyle="text-align:center" class="text-info" />
                                <Column footer="100 %" footerStyle="text-align:center" />
                                <Column :footer="formatUSD(Number(subDataSum(2)))" footerStyle="text-align:center" class="text-info" />
                            </Row>
                        </ColumnGroup>
                    </DataTable>
                </div>
            </div>
        </div>
    </div>
</template>
