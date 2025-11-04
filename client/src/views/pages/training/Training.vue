<script setup>
import { ref } from 'vue';
import Dashboard from './Dashboard.vue';
import TrainingCours from './TrainingCours.vue';
import TrainingCategory from './TrainingCategory.vue';

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
const bItems = () => {
    var list = [];
    if (props.currentPR != null) list.push(props.currentPR);
    if (props.currentTR != null) list.push(props.currentTR);
    if (props.currentHA != null) list.push(props.currentHA);
    if (props.currentFacility) list.push(props.currentFacility);
    return list;
};
const dashboard = ref(null);
const trainingCours = ref(null);
const trainingCategory = ref(null);

const treeUpdated = () => {
    switch (props.submenu_position) {
        case 0:
            dashboard.value.updateReport();
            break;
        case 1:
            trainingCours.value.updateReport();
            break;
        case 2:
            trainingCategory.value.updateReport();
            break;
        default:
            break;
    }
};

defineExpose({
    treeUpdated
});
</script>
<template>
    <div class="card p-2 pb-1">
        <div class="grid">
            <div class="col-10 pb-0">
                <Breadcrumb :model="bItems()" class="border-0" />
            </div>
            <div class="col-2 pb-0 text-right">
                <Button label="Actualiser" @click="treeUpdated()" icon="pi pi-refresh" severity="primary" raised />
            </div>
        </div>
    </div>
    <div class="pt-0">
        <Dashboard v-show="props.submenu_position == 0" :currentPR="currentPR" :currentTR="currentTR" :currentHA="currentHA" :currentFacility="currentFacility" ref="dashboard"></Dashboard>
        <TrainingCours v-show="props.submenu_position == 1" :currentPR="currentPR" :currentTR="currentTR" :currentHA="currentHA" :currentFacility="currentFacility" ref="trainingCours"></TrainingCours>
        <TrainingCategory v-show="props.submenu_position == 2" :currentPR="currentPR" :currentTR="currentTR" :currentHA="currentHA" :currentFacility="currentFacility" ref="trainingCategory"></TrainingCategory>
    </div>
</template>
