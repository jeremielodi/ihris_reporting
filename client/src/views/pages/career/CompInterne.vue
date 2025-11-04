<script setup>
import { ref } from 'vue';
import apiService from '@/service/ApiService';
import { FilterMatchMode } from '@primevue/core/api';
import xlsx from 'json-as-xlsx';
import dateFormat from 'dateformat';
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
    submenu_position: {
        type: Number,
        default: 0
    }
});

const error = ref(null);
const currentNode = ref(null);
const detail_error = ref(null);
const person_list = ref([]);
const zsFilter = ref(false);
const total_records = ref(0);
const loading = ref(false);
const showDetailDialog = ref(false);
const loadingReportDetails = ref(false);
const column_filter = ref(null);
const showPersonDetails = ref(false);
const selectedPerson = ref(null);
const detailReportLabel = ref(null);
const detailReportLocation = ref(null);
const detailReportEffectif = ref(0);
const detailReportLocationId = ref(null);
const filters2 = ref({
    LOCATION: { value: null, matchMode: FilterMatchMode.CONTAINS }
});
const filters1 = ref({
    fullname: { value: null, matchMode: FilterMatchMode.CONTAINS },
    birthdate: { value: null, matchMode: FilterMatchMode.CONTAINS },
    matricule: { value: null, matchMode: FilterMatchMode.CONTAINS }
});
const products = ref([]);

const breadcrumbItems = () => {
    var res = [];
    if (props.currentPR != null) res.push({ label: props.currentPR.label });

    if (props.currentTR != null) res.push({ label: props.currentTR.label });

    if (props.currentHA != null) res.push({ label: props.currentHA.label });
    // if (elt != null) {
    //         res.push({ label: elt })
    // }
    return res;
};
const onshowPersonDerails = (person) => {
    selectedPerson.value = person;
    showPersonDetails.value = true;
    showPersonDialog();
};
const showReportDetails = (v, label = '', data) => {
    showDetailDialog.value = true;
    column_filter.value = v;
    detailReportLabel.value = label;
    detailReportLocation.value = data.location;
    detailReportEffectif.value = data.agent_number;
    detailReportLocationId.value = data.location_id;
    getReportDetails(1, '');
};

const onclickGetReport = () => {
    currentNode.value = _AppCache.getCurrentNode();
    if (!currentNode.value) return;
    if (loading.value) return;
    loading.value = true;

    apiService
        .get('/reports/comp/internal?org_unit_id=' + currentNode.value + '&filter=' + (zsFilter.value ? 1 : 0))
        .then((res) => {
            error.value = null;
            products.value = [];

            var y = 0;
            res.data.data.forEach((elt) => {
                var line = {
                    id: (y += 1),
                    agent_number: elt.agent_number,
                    location: elt.location,
                    location_id: elt.location_id,
                    firstname: elt.firstname,
                    surname: elt.surname,
                    othername: elt.othername,
                    gender: elt.gender,
                    birth_date: elt.birth_date,
                    dependents: elt.dependents,
                    marital_status: elt.marital_status,
                    mobile_phone: elt.mobile_phone,
                    address: elt.address,
                    ref_on_employment: elt.ref_on_employment,
                    matricule: elt.matricule,
                    ref_engagement: elt.ref_engagement,
                    year_of_appointment: elt.year_of_appointment,
                    degree: elt.degree,
                    position: elt.position,
                    cadre: elt.cadre,
                    salary_grade: elt.salary_grade,
                    classification: elt.classification,
                    salaire: elt.salaire,
                    prime: elt.prime,
                    job: elt.job,
                    identifie: elt.identifie,
                    TOTAL: elt.total,
                    TAUX: elt.rate.toFixed(2)
                };

                products.value.push(line);
            });
        })
        .catch((err) => {
            error.value = err;
            loading.value = false;
        })
        .finally(() => {
            loading.value = false;
        });
};

const currrentTreePosition = ref(null);
const updateReport = (node) => {
    currentNode.value = node;
    if (currrentTreePosition.value != exportFileName() || person_list.value.lenght == 0) onclickGetReport();
    currrentTreePosition.value = exportFileName();
};

defineExpose({
    updateReport
});

const exportFileName = () => {
    let name = '';
    if (props.currentFacility) name += ' - ' + props.currentFacility.label;
    if (props.currentHA) name += ' - ' + props.currentHA.label;
    if (props.currentTR) name += ' - ' + props.currentTR.label;
    if (props.currentPR) name += ' - ' + props.currentPR.label;
    if (name == '') name = 'NATIONAL';
    return name.toUpperCase();
};
const getReportDetails = (page = 1, search = null, matricule = null, birth_date = null, download = 0) => {
    let url = `/people/list?org_unit_id=${detailReportLocationId.value}&matricule=${matricule}&birth_date=${birth_date}&page=${page}&limit=${20}&search=${search}&column_filter=${column_filter.value}&download_xlsx=${download}`;

    if (download == 1) {
        window.open(url, '_blank');
        return false;
    }

    detail_error.value = null;
    loadingReportDetails.value = true;
    person_list.value = [];
    apiService
        .get(url)
        .then((res) => {
            person_list.value = [];
            var y = 1;
            total_records.value = res.data.total_records;
            res.data.data.forEach((elt) => {
                elt.index = elt.index + 1;
                elt.birth_date = elt.birth_date != null && !elt.birth_date.includes('0000') ? dateFormat(new Date(elt.birth_date), 'dd-mm-yyyy') : '';
                elt.year_of_appointment = elt.year_of_appointment != null && !elt.year_of_appointment.includes('0000') ? dateFormat(new Date(elt.year_of_appointment), 'dd-mm-yyyy') : '';
                elt.gender = elt.gender != null ? elt.gender.replace('gender|', '') : '';
                y = y + 1;
                person_list.value.push(elt);
            });

            loadingReportDetails.value = false;
        })
        .catch((err) => {
            console.log(err);
            detail_error.value = err;
            loadingReportDetails.value = false;
        })
        .finally(() => {
            loadingReportDetails.value = false;
        });
};
const openManage = (id) => {
    window.open(`${import.meta.env.VITE_RECORD_VIEW_URL}?id=${id}`, '_blank');
};
const onPage = (page) => {
    getReportDetails(page.page + 1);
};
const onFilter = (f, download = 0) => {
    let _berth_date = '';
    if (filters1.value['birthdate'].value != null) {
        _berth_date = dateFormat(filters1.value['birthdate'].value, 'yyyy-mm-dd');
    }

    getReportDetails(1, filters1.value['fullname'].value, filters1.value['matricule'].value, _berth_date, download);
};
const onRemoveFilter = () => {
    filters1.value['fullname'].value = null;
    filters1.value['matricule'].value = null;
    filters1.value['birthdate'].value = null;
    onFilter('', 0);
};
const onSort = (ev) => {
    console.log(ev);
};

const downloadExcelFile = () => {
    let settings = {
        fileName: 'COMPLETUDE DE INTERNE - ' + exportFileName() + ' - ' + new Date().toLocaleString(),
        writeMode: 'writeFile',
        RTL: false
    };
    let data = [
        {
            sheet: 'Complétude interne  ',
            columns: [
                { label: 'No', value: 'id' },
                { label: 'LIEU', value: 'location' },
                { label: 'EFFECTIF', value: 'agent_number' },
                { label: 'NOM', value: 'firstname' },
                { label: 'POSTNOM', value: 'surname' },
                { label: 'PRENOM', value: 'othername' },
                { label: 'SEXE', value: 'gender' },
                { label: 'DATE DE NAISSANCE', value: 'birth_date' },
                { label: 'ENFANTS EN CHARGE', value: 'dependents' },
                { label: 'ETAT CIVIL', value: 'marital_status' },
                { label: 'TELEPHONE', value: 'mobile_phone' },
                { label: 'ADRESSE', value: 'address' },
                { label: 'REF. COM. AFFECTATION', value: 'ref_on_employment' },
                { label: 'MATRICULE', value: 'matricule' },
                { label: 'PRIME', value: 'prime' },
                { label: 'SALAIRE', value: 'salaire' },
                { label: "NIVEAU D'ETUDE", value: 'degree' },
                { label: 'POSITION ADM.', value: 'position' },
                { label: 'REF. ARR ADMIN:', value: 'ref_engagement' },
                { label: 'CATEGORIE PROF.', value: 'cadre' },
                { label: 'PROFESSION', value: 'classification' },
                { label: 'FONCTION', value: 'job' },
                { label: 'GRADE', value: 'salary_grade' },
                { label: 'SALAIRE', value: 'salaire' },
                { label: 'PRIME', value: 'prime' },
                { label: 'IDENTIFIE', value: 'identifie' },
                { label: 'TOTAL DE VALIABLES VIDE', value: 'TOTAL' },
                { label: 'TAUX %', value: 'TAUX' }
            ],
            content: products.value
        }
    ];

    xlsx(data, settings);
};
const personDialog = ref(null);
const showPersonDialog = () => {
    personDialog.value.showDialog();
};
</script>
<template>
    <div>
         <PyarmidPath :reload="onclickGetReport"/>
       
    
    <div className="card">
       
       

        <h5>COMPLÉTUDE INTERNE DES DONNÉES DE CARRIÈRE</h5>
        <hr />
        <div class="text-right">
            <label for="switch1">Filtrer les ZS</label>
            <InputSwitch v-model="zsFilter" @change="onclickGetReport()" inputId="switch1" class="ml-2" />
            <Button @click="onclickGetReport()" label="ACTUALISER" :loading="loading" icon="pi pi-refresh" class="p-button-sm p-button-primary ml-4" />
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

                <DataTable
                    v-if="products.length > 0 && error == null"
                    :value="products"
                    stripedRows
                    class="p-datatable-sm internal-table align-items-rignt"
                    :paginator="true"
                    :rows="30"
                    responsiveLayout="scroll"
                    :scrollable="true"
                    dataKey="id"
                    v-model:filters="filters2"
                    filterDisplay="menu"
                    scrollHeight="80%"
                    :loading="loading"
                    :globalFilterFields="['fosa']"
                    :resizableColumns="true"
                    columnResizeMode="fit"
                    showGridlines
                    ref="dt"
                >
                    <template #header>
                        <div class="grid">
                            <div class="col-6 pb-0">
                                <IconField iconPosition="left">
                                    <InputIcon class="pi pi-search"> </InputIcon>
                                    <InputText v-model="filters2['LOCATION'].value" placeholder="Rechercher ..." />
                                </IconField>
                            </div>
                            <div class="col-6 text-right pb-0">
                                <Button @click="downloadExcelFile()" label="EXCEL" icon="pi pi-download" class="p-button-success p-button-sm p-button-outlined p-button" iconPos="right" />
                            </div>
                        </div>
                    </template>
                    <Column :sortable="true" field="location" frozen header="LIEU" class="fosa_col"></Column>
                    <Column :sortable="true" field="agent_number"  header="EFFECTIF" class="font-semibold"></Column>
                    <Column :sortable="true" field="firstname" class="text-right" header="NOM">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.firstname == 0">{{ slotProps.data.firstname }}</span>
                            <a v-if="slotProps.data.firstname != 0" class="link" @click="showReportDetails('firstname', 'nom', slotProps.data)">{{ slotProps.data.firstname }}</a>
                        </template>
                    </Column>
                    <Column :sortable="true" field="surname" header="POST NOM">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.surname == 0">{{ slotProps.data.surname }}</span>
                            <a v-if="slotProps.data.surname != 0" class="link" @click="showReportDetails('surname', 'postnom', slotProps.data)">{{ slotProps.data.surname }}</a>
                        </template>
                    </Column>
                    <Column :sortable="true" field="othername" class="w100 text-right" header="PRENOM">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.othername == 0">{{ slotProps.data.othername }}</span>
                            <a v-if="slotProps.data.othername != 0" class="link" @click="showReportDetails('othername', 'prenom', slotProps.data)">{{ slotProps.data.othername }}</a>
                        </template>
                    </Column>

                    <Column :sortable="true" field="birth_date" header="DATE NAIS.">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.birth_date == 0">{{ slotProps.data.birth_date }}</span>
                            <a v-if="slotProps.data.birth_date != 0" class="link" @click="showReportDetails('birth_date', 'date de naissance', slotProps.data)">{{ slotProps.data.birth_date }}</a>
                        </template>
                    </Column>
                    <Column :sortable="true" field="gender" header="SEXE.">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.gender == 0">{{ slotProps.data.gender }}</span>
                            <a v-if="slotProps.data.gender != 0" class="link" @click="showReportDetails('gender', 'genre', slotProps.data)">{{ slotProps.data.gender }}</a>
                        </template>
                    </Column>
                    <Column :sortable="true" field="dependents" header="ENF. EN CHARGE">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.dependents == 0">{{ slotProps.data.dependents }}</span>
                            <a v-if="slotProps.data.dependents != 0" class="link" @click="showReportDetails('dependents', 'enfant en charge', slotProps.data)">{{ slotProps.data.dependents }}</a>
                        </template>
                    </Column>
                    <Column :sortable="true" field="marital_status" header="ETAT CIVIL">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.marital_status == 0">{{ slotProps.data.marital_status }}</span>
                            <a v-if="slotProps.data.marital_status != 0" class="link" @click="showReportDetails('marital_status', 'état civil', slotProps.data)">{{ slotProps.data.marital_status }}</a>
                        </template>
                    </Column>

                    <Column :sortable="true" field="mobile_phone" header="TELEPHONE">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.mobile_phone == 0">{{ slotProps.data.mobile_phone }}</span>
                            <a v-if="slotProps.data.mobile_phone != 0" class="link" @click="showReportDetails('mobile_phone', 'téléphone', slotProps.data)">{{ slotProps.data.mobile_phone }}</a>
                        </template>
                    </Column>
                    <Column :sortable="true" field="address" header="ADRESSE">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.address == 0">{{ slotProps.data.address }}</span>
                            <a v-if="slotProps.data.address != 0" class="link" @click="showReportDetails('address', 'adresse', slotProps.data)">{{ slotProps.data.address }}</a>
                        </template>
                    </Column>
                    <Column :sortable="true" field="matricule" header="MATRICULE">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.matricule == 0">{{ slotProps.data.matricule }}</span>
                            <a v-if="slotProps.data.matricule != 0" class="link" @click="showReportDetails('matricule', 'Matricule', slotProps.data)">{{ slotProps.data.matricule }}</a>
                        </template>
                    </Column>
                    <Column :sortable="true" field="prime" header="PRIME">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.prime == 0">{{ slotProps.data.prime }}</span>
                            <a v-if="slotProps.data.prime != 0" class="link" @click="showReportDetails('prime', 'prime', slotProps.data)">{{ slotProps.data.prime }}</a>
                        </template>
                    </Column>
                    <Column :sortable="true" field="salaire" header="SALAIRE">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.salaire == 0">{{ slotProps.data.salaire }}</span>
                            <a v-if="slotProps.data.salaire != 0" class="link" @click="showReportDetails('salaire', 'salaire', slotProps.data)">{{ slotProps.data.salaire }}</a>
                        </template>
                    </Column>
                    <Column :sortable="true" field="ref_on_employment" header="REF. COM. AFFECATION">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.ref_on_employment == 0">{{ slotProps.data.ref_on_employment }}</span>
                            <a v-if="slotProps.data.ref_on_employment != 0" class="link" @click="showReportDetails('ref_on_employment', 'ref ar. adm. status', slotProps.data)">{{ slotProps.data.ref_on_employment }}</a>
                        </template>
                    </Column>
                    <Column :sortable="true" field="ref_engagement" header="REF. ARRÂTÉ ADM.STATUS">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.ref_engagement == 0">{{ slotProps.data.ref_engagement }}</span>
                            <a v-if="slotProps.data.ref_engagement != 0" class="link" @click="showReportDetails('ref_engagement', 'ref ar. adm. status', slotProps.data)">{{ slotProps.data.ref_engagement }}</a>
                        </template>
                    </Column>

                    <Column :sortable="true" field="year_of_appointment" header="DATE ENG">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.year_of_appointment == 0">{{ slotProps.data.year_of_appointment }}</span>
                            <a v-if="slotProps.data.year_of_appointment != 0" class="link" @click="showReportDetails('year_of_appointment', 'date d\'engagement', slotProps.data)">{{ slotProps.data.year_of_appointment }}</a>
                        </template>
                    </Column>

                    <Column :sortable="true" field="position" header="POSITION ADMIN">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.position == 0">{{ slotProps.data.position }}</span>
                            <a v-if="slotProps.data.position" class="link" @click="showReportDetails('position', 'position d\'admn.', slotProps.data)">{{ slotProps.data.position }}</a>
                        </template>
                    </Column>

                    <Column :sortable="true" field="degree" header="NIVEAU ETUDE">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.degree == 0">{{ slotProps.data.degree }}</span>
                            <a v-if="slotProps.data.degree != 0" class="link" @click="showReportDetails('degree', 'niveau d\étude', slotProps.data)">{{ slotProps.data.degree }}</a>
                        </template>
                    </Column>

                    <Column :sortable="true" field="cadre" header="CATEGORIE">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.cadre == 0">{{ slotProps.data.cadre }}</span>
                            <a v-if="slotProps.data.cadre != 0" class="link" @click="showReportDetails('cadre', 'catégorie', slotProps.data)">{{ slotProps.data.cadre }}</a>
                        </template>
                    </Column>
                    <Column :sortable="true" field="salary_grade" header="GRADE">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.salary_grade == 0">{{ slotProps.data.salary_grade }}</span>
                            <a v-if="slotProps.data.salary_grade != 0" class="link" @click="showReportDetails('salary_grade', 'Grage', slotProps.data)">{{ slotProps.data.salary_grade }}</a>
                        </template>
                    </Column>
                    <Column :sortable="true" field="classification" header="PROFFESION">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.classification == 0">{{ slotProps.data.classification }}</span>
                            <a v-if="slotProps.data.classification != 0" class="link" @click="showReportDetails('classification', 'Profession', slotProps.data)">{{ slotProps.data.classification }}</a>
                        </template>
                    </Column>

                    <Column :sortable="true" field="job" header="FONCTION">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.job == 0">{{ slotProps.data.job }}</span>
                            <a v-if="slotProps.data.job != 0" class="link" @click="showReportDetails('job', 'fonction', slotProps.data)">{{ slotProps.data.job }}</a>
                        </template>
                    </Column>
                    <Column :sortable="true" field="identifie" header="IDENTIFIER">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.identifie == 0">{{ slotProps.data.identifie }}</span>
                            <a v-if="slotProps.data.identifie != 0" class="link" @click="showReportDetails('identifie', 'identifier', slotProps.data)">{{ slotProps.data.identifie }}</a>
                        </template>
                    </Column>

                    <Column :sortable="true" field="TOTAL" header="TOTAL" class="text-red-300 font-semibold"></Column>
                    <Column :sortable="true" field="TAUX" header="TAUX %" class="text-green-500 font-semibold"></Column>
                </DataTable>
            </div>
        </div>
        <Dialog v-model:visible="showDetailDialog" position="top" maximizable modal header="Complétude Interne des données de carrière" :style="{ width: '90vw' }">
            <Breadcrumb class="mb-2 p-menuitem-text" :model="breadcrumbItems(detailReportLocation)">
                <template #item="{ item }">
                    <a :href="'#' + item.label">{{ item.label }}</a>
                </template>
            </Breadcrumb>
            <span>
                Effectif total:
                <b v-if="!loadingReportDetails">{{ detailReportEffectif }}</b>
                <b v-if="loadingReportDetails"> -- </b>
            </span>
            |
            <span class="text-success">
                Effectif avec la variable({{ detailReportLabel }}) renseignée:
                <b v-if="!loadingReportDetails"
                    >{{ detailReportEffectif - total_records }} ou

                    <span v-if="detailReportEffectif > 0">{{ (((detailReportEffectif - total_records) / detailReportEffectif) * 100).toFixed(2) }}% </span>
                </b>
                <span v-if="loadingReportDetails"> --- </span>
            </span>
            |

            <span class="text-danger">
                Effectif avec la variable({{ detailReportLabel }}) non renseignée:

                <b v-if="!loadingReportDetails"
                    >{{ total_records }} ou
                    <span v-if="detailReportEffectif > 0">{{ ((total_records / detailReportEffectif) * 100).toFixed(2) }}% </span>
                </b>

                <span v-if="loadingReportDetails"> --- </span>
            </span>

            <span v-if="loadingReportDetails"> Chargement en cours ... </span>
            <div v-if="detail_error != null && !loadingReportDetails" class="row">
                <div class="col-sm-3"></div>
                <div class="col-sm-6 text-center m-4">
                    <div class="alert alert-danger text-center" role="alert">
                        <h4>Echec de connexion</h4>
                        <p>{{ error }}</p>
                        <hr />
                        <Button @click="getReportDetails()" label="Réessayer" class="p-button-danger p-button-sm" />
                    </div>
                </div>
            </div>
            <div v-if="detail_error == null">
                <hr />
                <div class="flex pt-2">
                    <IconField iconPosition="left" class="mr-3">
                        <InputIcon class="pi" :class="loadingReportDetails ? 'pi-spinner pi-spin' : 'pi-search'"> </InputIcon>
                        <InputText v-model="filters1['fullname'].value" v-on:input="onFilter($event)" placeholder="Rechercher nom, post prenom ..." />
                    </IconField>

                    <FloatLabel class="mr-3">
                        <InputText id="matricule" v-model="filters1['matricule'].value" v-on:input="onFilter($event)" />

                        <label for="matricule">Matricule</label>
                    </FloatLabel>
                    
                    <Button label="Rechercher" class="ml-3" icon="pi pi-search" :loading="loadingReportDetails" @click="onFilter()" raised />

                    <Button
                        label="Suppimer les filters"
                        class="ml-3 p-button-danger"
                        @click="onRemoveFilter()"
                        :disabled="loadingReportDetails"
                        icon="pi pi-times"
                        severity="danger"
                        raised
                        v-if="filters1['birthdate'].value != null || filters1['matricule'].value != null || filters1['fullname'].value != null"
                    />
                </div>

                <DataTable
                    :value="person_list"
                    stripedRows
                    scrollable
                    scrollHeight="100%"
                    :resizableColumns="true"
                    columnResizeMode="fit"
                    showGridlines
                    class="mt-4 p-datatable-sm"
                    paginator
                    lazy
                    :rows="20"
                    v-model:filters="filters1"
                    ref="dt"
                    dataKey="id"
                    :totalRecords="total_records"
                    :loading="loadingReportDetails"
                    @page="onPage($event)"
                    @sort="onSort($event)"
                    @filter="onFilter($event)"
                    filterDisplay="row"
                >
                    <template #header>
                        <div class="flex justify-content-end text-right">
                            <Button @click="getReportDetails()" icon="pi pi-refresh" :loading="loadingReportDetails" label="VISUALISER" class="p-button-primary p-button-sm mb-4" />
                            <Button @click="onFilter('', 1)" label="TELECHARGER" icon="pi pi-download" class="p-button-success p-button-sm ml-2 mb-4" />
                        </div>
                    </template>

                    <Column field="index" header="NO" frozen style="max-width: 35px; background: #f8f9fa"></Column>
                    <Column sortable field="fullname" class="text-primary" frozen header="NOM COMPET" footer="NOM COMPET" style="min-width: 300px; background: #f8f9fa">
                        <template #body="slotProps">
                            <a class="link" @click="onshowPersonDerails(slotProps.data)"
                                ><b>{{ slotProps.data.fullname }}</b></a
                            >
                        </template>
                    </Column>
                    <Column field="id" frozen header="LIEN" footer="LIEN" style="max-width: 40px">
                        <template #body="slotProps">
                            <a class="text-primary" @click="openManage(slotProps.data.id)">
                                <i class="pi pi-external-link float-right" id="slotProps.data.id"> </i>
                            </a>
                        </template>
                    </Column>

                    <Column field="facility_name" header="STRUCTURE" footer="STRUCTURE" style="min-width: 140px"></Column>
                    <Column field="health_area_name" header="ZONE DE SANTE" footer="ZONE DE SANTE" style="min-width: 140px"></Column>
                    <Column field="district_name" header="PROVINCE" footer="PROVINCE" style="min-width: 200px"></Column>
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
                    <Column field="ref_on_employment" header=" REF. COMMISION D'AFFECTATION" footer="REF. COMMISIION D'AFFECTATION" style="min-width: 400px"></Column>
                    <Column field="ref_engagement" header="REF. ARRETE D'ADMISSION SOUS STATUT" footer="REF ARRETE D'ADMISSION SOUS STATUT" style="min-width: 300px"></Column>
                    <Column field="mobile_phone" header="TELEPHONE" footer="TELEPHONE" style="min-width: 100px"></Column>
                    <Column field="address" header="ADRESSE" footer="ADRESSE" style="min-width: 200px"></Column>
                </DataTable>
            </div>
        </Dialog>
        <Person ref="personDialog" :person="selectedPerson"> </Person>
    </div>
</div>
</template>

<style lang="scss" scoped>
thead {
    font-size: smaller;
}
.internal-table .vtitle {
    writing-mode: vertical-rl;
    transform: rotate(180deg);
    text-align: left;
    max-height: 150px;
}

.p-datepicker {
    padding: 0px !important;
}
</style>
