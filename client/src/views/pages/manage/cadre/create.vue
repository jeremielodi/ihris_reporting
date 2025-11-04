<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import CadreSelect from '@/components/CadreSelect.vue';
import CadreService from './cadre.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'cadreCreateView',
    data() {
        return {
            formSubmitted: false,
            cadreId: null,
            cadre: { name: null, translate_key: null }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.cadreId = id;
            CadreService.read(id).then((cadre) => {
                setTimeout(() => {
                    this.cadre = cadre;
                    this.cadre.i2ce_hidden = !!cadre.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText,
        CadreSelect
    },
    methods: {
        reset() {
            this.cadre = {};
            this.formSubmitted = false;
            if (this.cadreId) {
                this.$router.push('/manage/cadre_registry');
            }
        },
        validate() {
            const options = {
                name: this.cadre.name
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
        createCadre() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.cadreId ? CadreService.update(this.cadreId, this.cadre) : CadreService.create(this.cadre);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/cadre_registry?id=${response.id}`);
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
        <h4>{{ cadreId ? $t('TREE.CADRE_UPDATE') : $t('TREE.CADRE_NEW') }}</h4>

        <form @submit.prevent="createCadre" style="width: 100%">
            <div class="grid">
                <div class="col-12">
                    <hr />
                    <button type="submit" class="p-button p-component p-button-primary">
                        <span class="p-button-label">
                            {{ $t('FORM.BUTTONS.SUBMIT') }}
                        </span>
                    </button>
                    <button type="reset" @click="reset" class="p-button p-component p-button-secondary" style="margin-left: 10px">
                        <span class="p-button-label">{{ $t('FORM.BUTTONS.CANCEL') }}</span>
                    </button>
                    <hr />
                </div>
                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <MyInputText
                        id="name"
                        v-model="cadre.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                cadre.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <MyInputText
                        id="code"
                        v-model="cadre.code"
                        label="FORM.LABELS.CODE"
                        :required="false"
                        @onChange="
                            (value) => {
                                cadre.code = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <MyInputText
                        id="description"
                        v-model="cadre.description"
                        label="FORM.LABELS.DESCRIPTION"
                        :required="false"
                        @onChange="
                            (value) => {
                                cadre.description = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
        
        
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="cadreId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="cadre.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
