<script>
import { defineComponent } from 'vue';
import NotifyService from '@/service/Notify.service';
import UtilService from '@/service/UtilService';
import readXlsxFile, { readSheetNames } from 'read-excel-file';

export default defineComponent({
    name: 'ImportUnitsModal',
    props: {
        close: Function,
        display: {
            type: Boolean,
            default: false
        }
    },
    data() {
        return {
            submitted: false,
            selectedLocation: {},
            server: '/',
            validationErrors: {},
            loading: false,
            data: {
                file: {}
            }
        };
    },
    watch: {
        display(newVal) {
            if (newVal) {
                this.server = this.$store.state.server;
            }
        }
    },
    methods: {
        closeDialog() {
            this.submitted = false;
            this.data = {
                file: {}
            };
            this.close(false);
        },

        readCSV(input) {
            function formatCol(val) {
                if (val) {
                    return val.replace('\r', '').trim();
                }
                return val;
            }
            const reader = new FileReader();
            const self = this;
            reader.onload = (e) => {
                const text = e.target.result;
                const rows = text.split('\n');
                const result = [];
                if (rows.length > 0) {
                    const headers = rows[0].split(',');
                    let i = 0;
                    for (const row of rows) {
                        if (i > 0) {
                            const lines = row.split(',');
                            let j = 0;
                            let obj = {};
                            for (const line of lines) {
                                if (headers[j]) {
                                    obj[formatCol(headers[j])] = formatCol(line);
                                    j++;
                                }
                            }
                            result.push(obj);
                        }
                        i++;
                    }
                }
                self.close(result);
            };
            reader.readAsText(input);
        },

        async submit() {
            if (this.loading) return;
            this.submitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }

            try {
                if (this.data.file.type === 'text/csv') {
                    this.readCSV(this.data.file);
                } else {
                    const sheetNames = await readSheetNames(this.data.file);
                    let result = [];
                    for (const sheet of sheetNames) {
                        const jsonData = await readXlsxFile(this.data.file, { sheet });
                        if (jsonData || Array.isArray(jsonData)) {
                            const headers = jsonData[0] || {};
                            for (let i = 1; i < jsonData.length; i++) {
                                let row = {};
                                for (let j = 0; j < headers.length; j++) {
                                    row[headers[j]] = jsonData[i][j];
                                }
                                result.push(row);
                            }
                        }
                    }
                    this.close(result);
                }
            } catch (ex) {
                console.log(ex);
            }
        },
        fileSelected(event) {
            const f = event.target.files[0];
            if (f) {
                this.data.file = f;
                return;
            }
        },
        setLocation() {
            this.data.office_uuid = this.selectedLocation.uuid;
            this.validate();
        },

        validate() {
            if (!this.submitted) return;
            return !!this.data.file.name;
        },
        injectFile(file, v, key) {
            const reader = new FileReader();
            reader.onload = (e) => {
                v[key] = {
                    base64: e.target.result,
                    name: file.name,
                    type: file.type
                };
            };
            reader.readAsDataURL(file);
        },
        sampleData() {
            UtilService.csvTemplate('organization_units.csv', ['id', 'name', 'code', 'parent', 'level']);
        }
    }
});
</script>

<template>
    <Dialog v-if="display" :header="$t('TREE.CLASSIFICATIONS')+' / '+ $t('FORM.BUTTONS.IMPORT')" :closable="false" position="top" :style="{ width: '30vw' }" :modal="true" :visible="display" footer="Footer">
        <div class="col-p12" style="margin-top: 10px">
            <div class="download-template">
                <i class="pi pi-cloud-download"></i>
                <a href @click="sampleData()" download="download">
                    {{ $t('FORM.BUTTONS.DOWNLOAD_TEMPLATE') }}
                </a>
            </div>
            <br />
            <label>{{ $t('FORM.LABELS.SELECT_FILE') }}</label>
            <div class="button-wrapper p-button-label">
                <div class="filename">
                    <span>{{ data.file.name }}</span>
                </div>

                <input type="file" id="updaload" name="myFile" @change="fileSelected($event)" />

                <div class="btn p-button p-component">
                    <i class="pi pi-cloud-upload"></i>
                </div>
            </div>
        </div>
        <template #footer>
            <Button :label="$t('FORM.BUTTONS.CANCEL')" @click="closeDialog" class="p-button-text" />
            <Button type="submit" @click="submit()" :label="$t('FORM.BUTTONS.IMPORT')" :disabled="loading" />
        </template>
    </Dialog>
</template>
<style scoped>
.p-field {
    padding-top: 20px;
}

.button-wrapper {
    position: relative;
    width: 100%px;
    background: #fff;
    border: 1px solid rgba(0, 0, 0, 0.2);
    border-radius: 2px;
    cursor: pointer;
    margin-top: 10px;
    height: 38px;
}

.button-wrapper .btn {
    float: right;
    background: gray;
    border: none !important;
    padding: 10px;
}

.filename {
    float: left;
    padding: 7px;
    padding-top: 12px;
    width: 90%;
    color: #2196f3;
    font-size: 13px;
    overflow: hidden;
}

#updaload {
    display: inline-block;
    position: absolute;
    z-index: 1;
    width: 100%;
    height: 20px;
    top: 0;
    left: 0;
    opacity: 0;
    cursor: pointer;
}

.download-template {
    text-align: center;
}
</style>
