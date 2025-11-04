<script setup>
import { ref } from 'vue';
import apiService from '@/service/ApiService';

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
        default: '---'
    },
    subtitle: {
        default: '---'
    },
    filter: {
        type: String,
        default: null
    },
    loading: {
        type: Boolean,
        default: false
    },
    footer: {
        type: String,
        default: '--'
    },
    subfooter: {
        // eslint-disable-next-line vue/require-valid-default-prop
        default: '--'
    },
    meter: {
        type: Number,
        default: 0
    },
    meter1: {
        type: Number,
        default: null
    }
});

const downloading = ref(false);
const exportFileName = () => {
    let name = '';
    if (props.currentFacility) name += props.currentFacility.label;
    if (props.currentHA) name += props.currentHA.label;
    if (props.currentTR) name += ' - ' + props.currentTR.label;
    if (props.currentPR) name += ' - ' + props.currentPR.label;
    if (name == '') name = 'NATIONAL';
    return name.toUpperCase();
};

function getCurrentNode(nodes) {
    const c = nodes.filter((n) => n != '0');
    return c.length > 0 ? c[c.length - 1] : '0';
}

const download = (key) => {
    downloading.value = true;
    let currentProvince_id = props.currentPR != null ? props.currentPR.key : '0';
    let currentTerritory_id = props.currentTR != null ? props.currentTR.key : '0';
    let currentHealtharia_id = props.currentHA != null ? props.currentHA.key : '0';
    let currentFacility = props.currentFacility != null ? props.currentFacility.key : '0';
    const currentNode = getCurrentNode([currentProvince_id, currentTerritory_id, currentHealtharia_id, currentFacility]);

    let url = `/people/download?org_unit_id=${currentNode}&filter=${props.filter}&title=${exportFileName()}`;

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
        })
        .catch((err) => {
            downloading.value = false;
            console.log(err);
        })
        .finally(() => {
            downloading.value = false;
        });
};
const formatCurrency = (value) => {
    if (value != null) return value.toLocaleString('fr-FR');
    return '--- ---';
};
</script>
<template>
    <div class="card mb-0">
        <div class="flex justify-content-between mb-2">
            <div>
                <span class="block online text-500 font-semibold mb-3">{{ props.title }}</span>
                <div v-if="!loading" class="text-primary font-bold text-lg">{{ formatCurrency(props.subtitle) }}</div>
                <Skeleton v-if="loading" class="mb-0" width="100%" height="22px" />
            </div>
            <div class="flex align-items-center justify-content-center border-round">
                <Button :disabled="props.filter == null || loading == true" :loading="downloading" @click="download()" size="small" rounded aria-label="Télécharger la liste" icon="pi pi-download" v-tooltip.top="'Télécharger'"></Button>
            </div>
        </div>
        <MeterGroup v-if="props.meter1 == null" :value="[{ label: '', value: (props.subtitle / props.meter) * 100, color: '#96b7ec' }]" />
        <MeterGroup
            v-if="props.meter1 != null"
            :value="[
                { label: 'M', value: (props.meter / props.subtitle) * 100, color: '#96b7ec' },
                { label: 'F', value: (props.meter1 / props.subtitle) * 100, color: '#fbbf24' }
            ]"
        />
        <Skeleton v-if="loading" class="mt-2" width="100%" height="11px" />
    </div>
</template>
