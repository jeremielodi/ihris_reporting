<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import DocumentTypeService from './document_type.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'documenttypeCreateView',
    data() {
        return {
            formSubmitted: false,
            documenttypeId: null,
            documenttype: { name: null, }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.documenttypeId = id;
            DocumentTypeService.read(id).then((documenttype) => {
                setTimeout(() => {
                    this.documenttype = documenttype;
                    this.documenttype.i2ce_hidden = !!documenttype.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText,
    },
    methods: {
        reset() {
            this.documenttype = {};
            this.formSubmitted = false;
            if (this.documenttypeId) {
                this.$router.push('/manage/document_type_registry');
            }
        },
        validate() {
            const options = {
                name: this.documenttype.name
            };
            let validKey = true;
            for (const key of Object.keys(options)) {
                if (!options[key]) {
                    validKey = false;
                    break;
                }
            }

            return validKey;
        },
        createDocumentType() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.documenttypeId ? DocumentTypeService.update(this.documenttypeId, this.documenttype) : DocumentTypeService.create(this.documenttype);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/document_type_registry?id=${response.id}`);
                })
                .catch(() => {
                    NotifyService.danger(this, '', null);
                })
                .finally(() => {
                    this.loading = false;
                });
        }
    }
});
</script>

<template>
    <div class="card manage-container">
        <h4>{{ documenttypeId ? $t('TREE.DOCUMENT_TYPE_UPDATE') : $t('TREE.DOCUMENT_TYPE_NEW') }}</h4>

        <form @submit.prevent="createDocumentType" style="width: 100%">
            <div class="grid">
                <div class="col-12">
                    <hr />
                    <button type="submit" class="p-button p-component p-button-primary">
                        <span class="p-button-label">
                            {{ $t('FORM.BUTTONS.SUBMIT') }}
                        </span>
                    </button>
                    <button type="reset" @click="reset" class="p-button p-component p-button-secondary"
                        style="margin-left: 10px">
                        <span class="p-button-label">{{ $t('FORM.BUTTONS.CANCEL') }}</span>
                    </button>
                    <hr />
                </div>
                <div class="col-12 lg:col-5 xl:col-5 p-field">

                    <MyInputText id="name" v-model="documenttype.name" label="FORM.LABELS.NAME" :required="true"
                        @onChange="
                            (value) => {
                                documenttype.name = value;
                            }
                        " :validationTrigger="formSubmitted" />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="documenttypeId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled"
                            v-model="documenttype.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
