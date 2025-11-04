
<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import CountrySelect from '@/components/CountrySelect.vue';
import CountryService from './country.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'countryCreateView',
    data() {
        return {
            formSubmitted: false,
            countryId: null,
            country: {name: null,code: null,}
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.countryId = id;
            CountryService.read(id).then((country) => {
                setTimeout(() => {
                    this.country = country;
                    this.country.i2ce_hidden = !!country.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText,
        CountrySelect
    },
    methods: {
        reset() {
            this.country = {};
            this.formSubmitted = false;
            if (this.countryId) {
                this.$router.push('/manage/country_registry');
            }
        },
        validate() {
            const options = {name: this.country.name,
parentError: this.countryId ? this.countryId == this.country.parent : true
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
        createCountry() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.countryId ? CountryService.update(this.countryId, this.country) : CountryService.create(this.country);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/country_registry?id=${response.id}`);
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
        <h4>{{ countryId ? $t('TREE.COUNTRY_UPDATE') : $t('TREE.COUNTRY_NEW') }}</h4>

        <form @submit.prevent="createCountry" style="width: 100%">
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
                                v-model="country.name"
                                label="FORM.LABELS.NAME"
                                :required="true"
                                @onChange="
                                    (value) => {
                                        country.name = value;
                                    }
                                "
                                :validationTrigger="formSubmitted"
                            />
                            <MyInputText
                                id="code"
                                v-model="country.name"
                                label="FORM.LABELS.CODE"
                                :required="false"
                                @onChange="
                                    (value) => {
                                        country.code = value;
                                    }
                                "
                                :validationTrigger="formSubmitted"
                            />
                            <CountrySelect
                        id="parent"
                        :value="country.parent"
                        label="FORM.LABELS.PARENT"
                        :required="true"
                        :onChange="
                            (value) => {
                                country.parent = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="countryId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="country.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
