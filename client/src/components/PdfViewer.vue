<script>
import { defineComponent } from 'vue';
import { saveAs } from 'file-saver';

export default defineComponent({
    name: 'PrdfViewerModal',
    props: {
        fileName: String,
        downloadFunction: Function,
        header: String,
        close: Function,
        display: {
            type: Boolean,
            default: false
        }
    },
    data() {
        return {
            content: '',
            file: null,
            showLoader: true
        };
    },

    watch: {
        display(newVal) {
            if (newVal) {
                this.downloadFunction()
                    .then((buffer) => {
                        if (!buffer) return;
                        const blob = new Blob([buffer], { type: 'application/pdf' });
                        this.content = URL.createObjectURL(blob);
                        this.file = blob;
                    })
                    .finally(() => {
                        this.showLoader = false;
                    });
            }
        }
    },
    methods: {
        closeDialog() {
            this.reset();
            this.close(false);
        },
        submit() {
            this.reset();
            this.close(true);
        },
        reset() {
            this.content = '';
            this.showLoader = true;
            this.file = null;
        },
        downloadURI() {
            saveAs(this.file, this.fileName || 'file.pdf');
        }
    }
});
</script>

<template>
    <Dialog v-if="display" :closable="false" position="top" :style="{ width: '80vw' }" :modal="true" :visible="display" footer="Footer">
        <div style="height: 85vw; padding: 0px">
            <div class="loader" v-if="showLoader"></div>
            <div class="centered" v-if="showLoader">{{ $t('FORM.INFO.LOADING') }}..</div>
            <embed :src="content" v-if="!showLoader" style="width: 100%; height: 100%" />
        </div>

        <template #footer>
            <span class="p-button" v-if="file" @click="downloadURI()">{{ $t('FORM.BUTTONS.DOWNLOAD') }}</span>
            <Button id="closeButton" :label="$t('FORM.BUTTONS.CLOSE')" class="p-button-text" @click="closeDialog" />
        </template>
    </Dialog>
</template>
<style scoped>
.loader {
    width: 120px;
    height: 120px;
    animation: spin 2s linear infinite;
    margin: auto;
    margin-top: 150px;
    border: 16px solid #f3f3f3;
    /* Light grey */
    border-radius: 50%;
    border-top: 16px solid #2296f3;
    border-right: 16px solid green;
    border-bottom: 16px solid #fe7009;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

.centered {
    text-align: center;
    width: 100%;
    margin: auto !important;
}
</style>
