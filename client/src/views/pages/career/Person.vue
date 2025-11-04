<script setup>
import { ref, onMounted } from 'vue';
import apiService from '@/service/ApiService';
import VuePdfEmbed from 'vue-pdf-embed';

const pdfSource = ref(null);

const props = defineProps({
    person: {
        type: Object,
        default: null
    },
    show: {
        type: Boolean,
        default: false
    }
});

onMounted(() => {
    loadingError.value = null;
    visible.value = props.show;
});
const visible = ref(false);
const progress = ref(true);
const loadingError = ref(null);
const pdf = ref(null);
const canDownload = ref(false);

const loadingFailed = (res) => {
    progress.value = false;
    loadingError.value = res;
    console.log(res.message);
};
const download = () => {
    pdf.value.download();
};
const showDialog = () => {
    // loadingError.value = null;
    // visible.value = true;
    // progress.value = true;

    // canDownload.value = false;
    // setTimeout(() => {
    //     pdfSource.value = apiService.defaults.baseURL + 'files/person?id=' + props.person.id;
    // }, 200);   
};
const loaded = () => {
    loadingError.value = null;
    canDownload.value = true;
    progress.value = false;
};
defineExpose({
    showDialog
});
</script>
<template>
    <div v-if="props.person != null">
        <Dialog v-model:visible="visible" maximizable modal position="top" :header="props.person.fullname" :style="{ width: '70vw' }">
            <div cl v-if="loadingError != null">
                <Message severity="error"
                    ><b> Échec du chargement du document PDF :</b>
                    {{ loadingError }}
                </Message>
            </div>
            <div v-if="progress" class="p-4 text-center">
                Chargement, veuillez patienter... <br />
                <br />
                <ProgressBar mode="indeterminate" style="height: 6px"></ProgressBar>
            </div>

            <div style="min-height: 50vw">
                <VuePdfEmbed v-if="pdfSource != null" ref="pdf" @loaded="loaded()" @rendering-failed="(a) => loadingFailed(a)" @loading-failed="(a) => loadingFailed(a)" annotation-layer text-layer :source="pdfSource" />
            </div>
            <template #footer>
                <div class="mt-3 surface-50">
                    <Button label="TELECHARGER" icon="pi pi-download" :disabled="!canDownload" class="mr-3" @click="download()" />
                    <Button label="FERMER" icon="pi pi-times" @click="visible = false" autofocus />
                </div>
            </template>
        </Dialog>
    </div>
</template>
