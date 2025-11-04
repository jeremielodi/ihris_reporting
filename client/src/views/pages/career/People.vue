<script setup>
import { ref } from 'vue';
import dateFormat from 'dateformat';
import { FilterMatchMode } from '@primevue/core/api';
import apiService from '@/service/ApiService';
import Person from './Person.vue';
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
const data = ref([]);
const loadingReport = ref(false);
const total_records = ref(0);
const showPersonDetails = ref(false);
const selectedPerson = ref(null);
const reportUrl = ref(null);
const downloading = ref(false);
var d = new Date(2012, 7, 25);
d.setFullYear(d.getFullYear() - 1);

const filters1 = ref({
    fullname: { value: null, matchMode: FilterMatchMode.CONTAINS },
    birthdate: { value: null, matchMode: FilterMatchMode.CONTAINS },
    matricule: { value: null, matchMode: FilterMatchMode.CONTAINS }
});

const onclickGetReport = (page = 1, search = null, matricule = null, birth_date = null) => {
    currentNode.value = _AppCache.getCurrentNode();
    if (!currentNode.value) return;

    if (loadingReport.value) return;
    reportUrl.value = '/people/list?' + 'org_unit_id=' + currentNode.value + '&page=' + page + '&limit=' + 50 + '&search=' + search + '&matricule=' + matricule + '&birth_date=' + birth_date;

    loadingReport.value = true;
    error.value = null;
    apiService
        .get(reportUrl.value)
        .then((res) => {
            error.value = null;
            var y = 0;

            total_records.value = res.data.total_records;

            res.data.data.forEach((elt) => {
                y++;
                elt.mid = res.data.page * res.data.limit - res.data.limit + y;
                elt.birth_date = elt.birth_date != null && !elt.birth_date.includes('0000') ? dateFormat(new Date(elt.birth_date), 'dd-mm-yyyy') : '';
                elt.year_of_appointment = elt.year_of_appointment != null && !elt.year_of_appointment.includes('0000') ? dateFormat(new Date(elt.year_of_appointment), 'dd-mm-yyyy') : '';
                elt.gender = elt.gender != null ? elt.gender.replace('gender|', '') : '';
            });
            data.value = res.data.data;
            loadingReport.value = false;
        })
        .catch((err) => {
            error.value = err;
            console.log(err);
            loadingReport.value = false;
        })
        .finally(() => {
            loadingReport.value = false;
        });
};
const onPage = (page) => {
    onclickGetReport(page.page + 1, '');
};
const onFilter = (f, download = 0) => {
    let _berth_date = '';
    if (filters1.value['birthdate'].value != null) {
        _berth_date = dateFormat(filters1.value['birthdate'].value, 'yyyy-mm-dd');
    }
    onclickGetReport(1, filters1.value['fullname'].value, filters1.value['matricule'].value, _berth_date, download);
};
const onSort = (ev) => {
    console.log(ev);
};
const openManage = (id) => {
    window.open(`${import.meta.env.VITE_RECORD_VIEW_URL}?id=${id}`, '_blank');
};
const onRemoveFilter = () => {
    filters1.value['fullname'].value = null;
    filters1.value['matricule'].value = null;
    filters1.value['birthdate'].value = null;
    onFilter('', 0);
};
const onshowPersonDerails = (person) => {
    selectedPerson.value = person;
    showPersonDetails.value = true;
    showPersonDialog();
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
const download = () => {
    downloading.value = true;
    apiService
        .get(reportUrl.value + '&download_xlsx=1&filename=' + exportFileName(), {
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
            downloading.value = false;
        })
        .catch((err) => {
            downloading.value = false;
            console.log(err);
            alert(err);
        });
};

const updateReport = (node) => {
    currentNode.value = node;
    onclickGetReport();
};

defineExpose({
    updateReport
});
const personDialog = ref(null);
const showPersonDialog = () => {
    personDialog.value.showDialog();
};
</script>
<template>
    <div>
     <div style="margin-bottom: 10px;">
        <PyarmidPath :reload="onclickGetReport"/>
    </div>
    <div className="card">
        <h4>LISTE DU PERSONNEL</h4>
        <div>
            <div>
                <h5>
                    Agent(s) :
                    <span v-if="!loadingReport"> {{ (data || []).length }}</span>
                    <small class="text-primary" v-if="loadingReport">chargement en cours ...</small>
                </h5>

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
                    :value="data"
                    v-if="error == null"
                    stripedRows
                    scrollable
                    scrollHeight="100%"
                    :resizableColumns="true"
                    columnResizeMode="fit"
                    showGridlines
                    class="mt-4 p-datatable-sm"
                    paginator
                    :rows="25"
                    ref="dt"
                    dataKey="id"
                    :totalRecords="(data || []).length"
                    :loading="loadingReport"
                    @page="onPage($event)"
                    @sort="onSort($event)"
                    @filter="onFilter($event)"
                    lazy="true"
                    filterDisplay="row"
                >
                    <template #header>
                        <div class="flex justify-content-end text-right">
                            <div class="flex justify-content-end text-right">
                                <span class="pt-2 pr-2">Filtres:</span>
                                <IconField iconPosition="left" class="mx-2">
                                    <InputIcon class="pi pi-search"> </InputIcon>
                                    <InputText v-model="filters1['fullname'].value" v-on:input="onFilter($event)" class="w-full" placeholder="Rechercher nom post prenom ..." />
                                </IconField>
                                <FloatLabel class="mx-2">
                                    <InputText id="Matricule" v-model="filters1['matricule'].value" v-on:input="onFilter($event)" class="w-full" />
                                    <label for="Matricule">Matricule</label>
                                </FloatLabel>
                                <Button
                                    label="Rechercher"
                                    class="mx-2"
                                    icon="pi pi-search"
                                    :loading="loadingReport == true && (filters1['birthdate'].value != null || filters1['matricule'].value != null || filters1['fullname'].value != null)"
                                    @click="onFilter()"
                                    raised
                                />
                                <Button @click="onclickGetReport()" label="VISUALISER" :loading="loadingReport" icon="pi pi-refresh" class="p-button-primary" />

                                <Button
                                    label=""
                                    title="Suppimer les filtres"
                                    class="mx-2 p-button-danger"
                                    @click="onRemoveFilter()"
                                    :disabled="loadingReportDetails"
                                    icon="pi pi-times"
                                    severity="danger"
                                    raised
                                    v-if="filters1['birthdate'].value != null || filters1['matricule'].value != null || filters1['fullname'].value != null"
                                />
                                <Button @click="download()" :loading="downloading" :disabled="reportUrl == null" icon="pi pi-download" label="TELECHARGER" class="p-button-success p-button-sm mx-2" />
                            </div>
                        </div>
                    </template>
                    <Column field="mid" header="id" frozen style="max-width: 45px"></Column>
                    <Column sortable field="fullname" frozen header="NOM COMPET" footer="NOM COMPET" style="min-width: 300px; background: #f8f9fa; left: 50px !important">
                        <template #body="slotProps">
                            <a class="text-blue-500" @click="onshowPersonDerails(slotProps.data)"
                                ><b>{{ slotProps.data.fullname }}</b>
                                <i v-if="slotProps.data.validation == 1" class="pi pi-verified pl-2" style="font-size: 0.8rem"></i>
                            </a>
                        </template>
                    </Column>
                    <Column field="id" frozen header="LIEN" footer="LIEN" style="max-width: 40px">
                        <template #body="slotProps">
                            <a class="text-blue-500" @click="openManage(slotProps.data.id)">
                                <i class="pi pi-external-link float-right" id="slotProps.data.id"> </i>
                            </a>
                        </template>
                    </Column>
                    <Column field="district_name" header="PROVINCE" footer="PROVINCE" style="min-width: 200px"></Column>
                    <Column field="health_area_name" header="ZONE DE SANTE" footer="ZONE DE SANTE"></Column>
                    <Column field="facility_name" header="STRUCTURE" footer="STRUCTURE"></Column>
                    <Column field="firstname" header="NOM" footer="NOM" style="min-width: 100px"></Column>
                    <Column field="surname" header="POSTNOM" footer="POST NOM" style="min-width: 100px"></Column>
                    <Column field="othername" header="PRENOM" footer="PRENOM" style="min-width: 100px"></Column>
                    <Column field="birth_date" header="D. NAISSANCE" footer="D. NAISSANCE" style="max-width: 100px"></Column>
                    <Column field="gender" header="GENRE" footer="GENRE" style="max-width: 100px"></Column>
                    <Column field="marital_status" header="ETAT CIVIL" footer="ETAT CIVIL" style="min-width: 100px"></Column>
                    <Column field="matricule" header="MATRICULE" footer="MATRICULE" style="max-width: 100px">
                        <template #body="slotProps">
                            <b>{{ slotProps.data.matricule }}</b>
                        </template>
                    </Column>
                    <Column sortable field="dependents" header="ENF. EN CHARGE" footer="ENF. EN CHARGE"></Column>
                    <Column field="degree" header="NIVEAU D'ETUDE" footer="NIVEAU D'ETUDE" style="max-width: 90px"></Column>
                    <Column field="position" header="POSITION" footer="POSITION" style="max-width: 130px"></Column>
                    <Column field="cadre" header="CATEGORIE" footer="CATEGORIE" style="min-width: 200px"></Column>
                    <Column field="classification" header="PROFESSION" footer="PROFESSION" style="min-width: 200px"></Column>
                    <Column field="job" header="FONCTION" footer="FONCTION" style="min-width: 200px"></Column>
                    <Column field="salary_grade" header="GRADE" footer="GRADE" style="min-width: 200px"></Column>
                    <Column field="salaire" header="SALAIRE" footer="GRADE" style="max-width: 80px"></Column>
                    <Column field="prime" header="PRIME" footer="PRIME" style="max-width: 80px"></Column>
                    <Column field="year_of_appointment" header="DATE D'ENGAGEMENT" footer="DATE D'ENGAGEMENT" style="max-width: 150px"></Column>
                    <Column field="ref_on_employment" header=" REF. COMMISIION D'AFFECTATION" footer="REF. COMMISIION D'AFFECTATION" style="min-width: 400px"></Column>
                    <Column field="ref_engagement" header="REF. ARRETE D'ADMISSION SOUS STATUT" footer="REF ARRETE D'ADMISSION SOUS STATUT" style="min-width: 300px"></Column>
                    <Column field="mobile_phone" header="TELEPHONE" footer="TELEPHONE" style="min-width: 100px"></Column>
                    <Column field="address" header="ADRESSE" footer="ADRESSE" style="min-width: 200px"></Column>
                    <Column field="validation" header="VALIDATION" class="p-0">
                        <template #body="slotProps">
                            <Tag v-if="slotProps.data.validation == 1" severity="success" value="Validé" rounded></Tag>
                            <Tag v-if="slotProps.data.validation == 0" severity="warning" value="En attente" rounded></Tag>
                        </template>
                    </Column>
                </DataTable>
            </div>

            <Person ref="personDialog" :person="selectedPerson"> </Person>
        </div>
    </div>
    </div>
</template>

<style scoped>
.p-datepicker {
    padding: 0px !important;
}
</style>