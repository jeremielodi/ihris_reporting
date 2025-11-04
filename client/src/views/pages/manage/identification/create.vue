<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import IdentificationTypeSelect from '@/components/IdentificationTypeSelect.vue';
import IdentificationService from './identification.service';
import NotifyService from '@/service/Notify.service';
import UtilService from '@/service/UtilService.js';
import CountrySelect from '@/components/CountrySelect.vue';
export default defineComponent({
    name: 'identificationCreateView',
    data() {
        return {
            formSubmitted: false,
            personId: null,
            identificationId: null,
            identification: { number: null, expiration_date: null, acquisition_date: null, type: null }
        };
    },
    created() {
        const { id, personId } = this.$route.query;
        this.personId = personId;
        this.identification.person_id = personId;
        if (id) {
            this.identificationId = id;
            IdentificationService.read(id).then((identification) => {
                setTimeout(() => {
                    this.identification = identification;
                    this.identification.i2ce_hidden = !!identification.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText,
        IdentificationTypeSelect,
        CountrySelect
    },
    methods: {
        reset() {
            this.identification = {};
            this.formSubmitted = false;
            if (this.identificationId) {
                window.history.back();
            }
        },
        validate() {
            const options = {
                number: this.identification.number,
                type_id: this.identification.type_id
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
        createIdentification() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }

            const formated = Object.assign({}, this.identification);
            formated.acquisition_date = UtilService.formatDate(new Date(formated.acquisition_date), 'YYYY-MM-DD');
            formated.expiration_date = UtilService.formatDate(new Date(formated.expiration_date), 'YYYY-MM-DD');
            delete formated.created;
            const service = IdentificationService;
            const operation = this.identificationId ? service.update(this.identificationId, formated) : service.create(formated);
            operation
                .then(() => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/people_record_view?id=${this.personId}`);
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
        <h4>{{ identificationId ? $t('TREE.IDENTIFICATION_UPDATE') : $t('TREE.IDENTIFICATION_NEW') }}</h4>

        <form @submit.prevent="createIdentification" style="width: 100%">
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
                     <IdentificationTypeSelect
                        id="type"
                        v-model="identification.type_id"
                        label="FORM.LABELS.TYPE"
                        :required="true"
                        :onChange="
                            (value) => {
                                identification.type_id = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    
                    <MyInputText
                        id="number"
                        v-model="identification.number"
                        label="FORM.LABELS.NUMBER"
                        :required="true"
                        @onChange="
                            (value) => {
                                identification.number = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="expiration_date"
                        v-model="identification.expiration_date"
                        label="FORM.LABELS.EXPIRATION_DATE"
                        :required="false"
                        type="date"
                        @onChange="
                            (value) => {
                                identification.expiration_date = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">

                    <MyInputText
                        id="acquisition_date"
                        v-model="identification.acquisition_date"
                        type="date"
                        label="FORM.LABELS.ACQUISITION_DATE"
                        :required="false"
                        :maxVal="new Date()"
                        @onChange="
                            (value) => {
                                identification.acquisition_date = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <CountrySelect
                        id="country"
                        :value="identification.country"
                        label="FORM.LABELS.COUNTRY"
                        :required="true"
                        :onChange="
                            (value) => {
                                identification.country = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <div v-if="identificationId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="identification.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
