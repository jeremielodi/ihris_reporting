<template>
    <div class="page">
        <div class="card uploader-card">
            <div class="header">
                <h3 class="title">{{ $t('FORM.LABELS.DOCUMENT') }}</h3>
                <p class="subtitle">
                    {{ $t('FORM.LABELS.AGENT') }}:
                    <span class="agent">{{ person.firstname }}, {{ person.lastname }}</span>
                </p>
            </div>

            <div class="content-grid">
                <!-- LEFT: form -->
                <form class="form" @submit.prevent="upload">
                    <label class="dropzone">
                        <input type="file" accept="application/pdf" @change="onFileChange" />
                        <div class="dz-content">
                            <i class="pi pi-upload dz-icon"></i>
                            <div class="dz-text">
                                <div class="dz-title">Glissez / déposez un PDF ici</div>
                                <div class="dz-hint">ou cliquez pour sélectionner</div>
                            </div>
                        </div>
                    </label>

                    <DocumentTypeSelect id="documentType" :value="documentTypeId" label="TREE.DOCUMENT_TYPE"
                        :required="false" :onChange="(value) => {
                                this.documentTypeId = value.id;
                            }
                            " :validationTrigger="false" />

                     <MyInputText
                        id="description"
                        v-model="description"
                        label="FORM.LABELS.DESCRIPTION"
                        type="text"
                        :maxVal="new Date()"
                        :required="true"
                        @onChange="
                            (value) => {
                                this.description = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <div v-if="file" class="file-meta">
                        <i class="pi pi-file-pdf"></i>
                        <div class="file-meta-text">
                            <div class="file-name">{{ file.name }}</div>
                            <div class="file-size">{{ formatBytes(file.size) }}</div>
                        </div>
                    </div>

                    <div class="actions">
                        <Button :label="$t('FORM.BUTTONS.SUBMIT')" :disabled="!file || uploading || !documentTypeId || !description" :loading="uploading"
                            type="submit" />

                        <Button v-if="file || uploadedUrl" severity="secondary" class="p-button-outlined" type="button"
                            :label="$t('FORM.BUTTONS.RESET')" @click="reset" />
                    </div>

                    <p v-if="error" class="error">{{ error }}</p>

                    <p v-if="uploadedUrl" class="uploaded">
                        Uploaded:
                        <a :href="uploadedUrl" target="_blank" rel="noopener">{{ uploadedUrl }}</a>
                    </p>
                </form>

                <!-- RIGHT: preview -->
                <div class="preview">
                    <div v-if="!previewUrl" class="placeholder">
                        <i class="pi pi-file-pdf placeholder-icon"></i>
                        <div class="placeholder-text">Aperçu PDF</div>
                    </div>

                    <div v-else class="pdf-wrap">
                        <object :data="previewUrl" type="application/pdf" class="pdf-viewer">
                            <iframe :src="previewUrl" class="pdf-viewer" />
                        </object>

                        <div class="preview-actions">
                            <a class="link" :href="previewUrl" target="_blank" rel="noopener">
                                Ouvrir dans un nouvel onglet
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            <!-- /content-grid -->
        </div>
    </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import PeopleService from './people.service'
import NotifyService from '@/service/Notify.service'
import Button from 'primevue/button'
import MyInputText from '@/components/InputText.vue';
import DocumentTypeSelect from '@/components/DocumentTypeSelect.vue';

export default defineComponent({
    name: 'PdfUploader',
    components: { Button, DocumentTypeSelect, MyInputText },
    data() {
        return {
            file: null as File | null,
            documentTypeId: null,
            description:null,
            previewUrl: null as string | null,
            uploading: false,
            progress: 0,
            error: null as string | null,
            uploadedUrl: null as string | null,
            personId: null as any,
            person: {} as any,
        }
    },
    created() {
        const { personId } = this.$route.query
        this.personId = personId
        this.getPersonInfo()
    },
    beforeUnmount() {
        // avoid memory leaks
        if (this.previewUrl) URL.revokeObjectURL(this.previewUrl)
    },
    methods: {
        onFileChange(e: Event) {
            const input = e.target as HTMLInputElement
            const f = input.files?.[0] ?? null

            this.error = null
            this.uploadedUrl = null

            // cleanup old preview
            if (this.previewUrl) URL.revokeObjectURL(this.previewUrl)

            if (!f) {
                this.file = null
                this.previewUrl = null
                return
            }

            if (f.type !== 'application/pdf') {
                this.file = null
                this.previewUrl = null
                this.error = 'Veuillez sélectionner un fichier PDF.'
                return
            }

            this.file = f
            this.previewUrl = URL.createObjectURL(f)
        },

        getPersonInfo() {
            PeopleService.read(this.personId).then((person: any) => {
                this.person = person
            })
        },

        async upload() {
            if (!this.file) return
            this.uploading = true
            this.progress = 0
            this.error = null

            try {
                const res = await PeopleService.documents.upload(this.file, this.documentTypeId, this.personId, this.description)
                this.uploadedUrl = res.url
                NotifyService.success(this, '', null)
                this.$router.push(`/manage/people_record_view?id=${this.personId}`)
            } catch (err: any) {
                NotifyService.danger(this, '', null)
                this.error = err?.response?.data?.detail ?? 'Upload failed'
            } finally {
                this.uploading = false
            }
        },

        reset() {
            this.file = null
            if (this.previewUrl) URL.revokeObjectURL(this.previewUrl)
            this.previewUrl = null
            this.uploadedUrl = null
            this.progress = 0
            this.error = null
        },

        formatBytes(bytes: number) {
            if (!bytes && bytes !== 0) return ''
            const sizes = ['B', 'KB', 'MB', 'GB']
            const i = Math.min(
                Math.floor(Math.log(bytes) / Math.log(1024)),
                sizes.length - 1
            )
            const value = bytes / Math.pow(1024, i)
            return `${value.toFixed(i === 0 ? 0 : 1)} ${sizes[i]}`
        },
    },
})
</script>

<style scoped>
.page {

    padding: 0px 16px 24px;
}

.uploader-card {
    width: 95%;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
}

.header {
    display: grid;
    gap: 6px;
    margin-bottom: 14px;
}

.title {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 700;
}

.subtitle {
    margin: 0;
    opacity: 0.9;
}

.agent {
    font-weight: 700;
}

.form {
    display: grid;
    gap: 14px;
}

.dropzone {
    position: relative;
    border: 1px dashed rgba(0, 0, 0, 0.25);
    border-radius: 14px;
    padding: 14px;
    cursor: pointer;
    transition: 0.15s ease;
}

.dropzone:hover {
    border-color: rgba(0, 0, 0, 0.45);
    transform: translateY(-1px);
}

.dropzone input[type='file'] {
    position: absolute;
    inset: 0;
    opacity: 0;
    cursor: pointer;
}

.dz-content {
    display: flex;
    align-items: center;
    gap: 12px;
}

.dz-icon {
    font-size: 1.4rem;
    opacity: 0.85;
}

.dz-title {
    font-weight: 700;
}

.dz-hint {
    font-size: 0.9rem;
    opacity: 0.75;
}

.file-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 12px;
    background: rgba(0, 0, 0, 0.03);
}

.file-meta i {
    font-size: 1.2rem;
}

.file-name {
    font-weight: 700;
    line-height: 1.2;
}

.file-size {
    font-size: 0.9rem;
    opacity: 0.75;
}

.preview {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid rgba(0, 0, 0, 0.12);
    background: rgba(0, 0, 0, 0.02);
    min-height: 320px;
    max-height: 500px;
}

.placeholder {
    height: 320px;
    display: grid;
    place-items: center;
    gap: 8px;
}

.placeholder-icon {
    font-size: 5rem;
    opacity: 0.35;
}

.placeholder-text {
    opacity: 0.7;
    font-weight: 600;
}

.pdf-wrap {
    display: grid;
}

.pdf-viewer {
    width: 100%;
    height: 520px;
    border: 0;
    display: block;
    background: white;
}

.preview-actions {
    padding: 10px 12px;
    display: flex;
    justify-content: flex-end;
    border-top: 1px solid rgba(0, 0, 0, 0.08);
    background: rgba(0, 0, 0, 0.015);
}

.link {
    text-decoration: none;
    font-weight: 700;
}

.actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.error {
    margin: 0;
    color: #d12;
    font-weight: 600;
}

.uploaded {
    margin: 0;
    opacity: 0.9;
}

.content-grid {
    display: grid;
    grid-template-columns: 1fr 1.2fr;
    /* left / right */
    gap: 14px;
    align-items: start;
}

/* Keep form compact */
.form {
    display: grid;
    gap: 14px;
    min-width: 0;
}

/* Preview takes the right column and stays visible */
.preview {
    min-width: 0;
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid rgba(0, 0, 0, 0.12);
    background: rgba(0, 0, 0, 0.02);
    height: 100%;
}

/* Make the viewer fill nicely */
.pdf-viewer {
    width: 100%;
    height: 620px;
    border: 0;
    display: block;
    background: white;
}

/* Responsive: stack on small screens */
@media (max-width: 900px) {
    .content-grid {
        grid-template-columns: 1fr;
    }

    .pdf-viewer {
        height: 520px;
    }
}
</style>
