<template>
    <div class="card manage-container" style="padding-top: 100px;">

        <center>



            <div class="p-fluid" style="max-width: 500px;">
                <h4>
                    {{ $t('FORM.LABELS.LOGO') }}
                </h4>
                <hr />
                <br />
                <form @submit.prevent="upload" style="width: 100%">

                    <input type="file" accept="image/*" @change="onFileChange" />
                    <br /> <br />
                    <div v-if="!previewUrl" class="preview">
                        <i class="pi pi-id-card" style="font-size: 16rem"></i>
                    </div>
                    <div v-if="previewUrl" class="preview">
                        <img :src="previewUrl" alt="preview" />
                    </div>


                    <br /> <br />
                    <Button :label="$t('FORM.BUTTONS.SUBMIT')" :disabled="!file || uploading" @click="upload" />

                    <br /> <br />
                    <Button severity="secondary" type="reset" :label="$t('FORM.BUTTONS.RESET')" class="ghost"
                        v-if="file || uploadedUrl" @click="reset" />

                    <p v-if="error" class="error">{{ error }}</p>
                    <p v-if="uploadedUrl">
                        Uploaded: <a :href="uploadedUrl" target="_blank">{{ uploadedUrl }}</a>
                    </p>
                </form>
            </div>
        </center>
    </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import SettingService from './setting.service'
import NotifyService from '@/service/Notify.service'
import Button from 'primevue/button'


export default defineComponent({
    name: 'ImageUploader',
    data() {
        return {
            file: null as File | null,
            previewUrl: null as string | null,
            uploading: false,
            progress: 0,
            error: null as string | null,
            uploadedUrl: null as string | null,
            personId: null,
            person: {}
        }
    },
    created() {
        const { id } = this.$route.query;
    },
    methods: {
        onFileChange(e: Event) {
            const input = e.target as HTMLInputElement
            const f = input.files?.[0] ?? null

            this.error = null
            this.uploadedUrl = null

            if (!f) {
                this.file = null
                this.previewUrl = null
                return
            }
            if (!f.type.startsWith('image/')) {
                this.error = 'Please select an image file.'
                return
            }

            this.file = f
            this.previewUrl = URL.createObjectURL(f)
        },

        async upload() {
            if (!this.file) return
            this.uploading = true
            this.progress = 0
            this.error = null
            try {
                const res = await SettingService.logoUpload(this.file, 1);
                this.uploadedUrl = res.url;
                NotifyService.success(this, '', null);
                window.history.back();
            } catch (err: any) {
                NotifyService.danger(this, '', null);
                console.log(err);
                this.error = err?.response?.data?.detail ?? 'Upload failed'
            } finally {
                this.uploading = false
            }
        },

        reset() {
            this.file = null
            this.previewUrl = null
            this.uploadedUrl = null
            this.progress = 0
            this.error = null
        },
    },
})
</script>

<style scoped>
.uploader {
    display: grid;
    gap: .75rem;
    max-width: 380px;
}

.preview img {
    max-width: 100%;
    border-radius: 8px;
    display: block;
}

button {
    padding: .5rem .9rem;
    border-radius: .5rem;
    border: 1px solid #444;
}

button.ghost {
    background: transparent;
}

.error {
    color: #e33;
}
</style>
