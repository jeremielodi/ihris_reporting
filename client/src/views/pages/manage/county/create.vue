<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import DistrictSelect from '@/components/DistrictSelect.vue';
import CountyService from './county.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'countyCreateView',
    data() {
        return {
            formSubmitted: false,
            countyId: null,
            county: { name: null, code: null, district: null }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.countyId = id;
            CountyService.read(id).then((county) => {
                setTimeout(() => {
                    this.county = county;
                    this.county.i2ce_hidden = !!county.i2ce_hidden;
                }, 1000);
            });
        }
    },
    components: {
        MyInputText,
        DistrictSelect
    },
    methods: {
        reset() {
            this.county = {};
            this.formSubmitted = false;
            if (this.countyId) {
                this.$router.push('/manage/county_registry');
            }
        },
        validate() {
            const options = { 
                name: this.county.name,
                disctrict: this.county.district };
            let validKey = true;
            for (const key of Object.keys(options)) {
                if (!options[key]) {
                    validKey = false;
                    break;
                }
            }

            return validKey;
        },
        createCounty() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.countyId ? CountyService.update(this.countyId, this.county) : CountyService.create(this.county);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/county_registry?id=${response.id}`);
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
        <h4>{{ countyId ? $t('TREE.COUNTY_UPDATE') : $t('TREE.COUNTY_NEW') }}</h4>

        <form @submit.prevent="createCounty" style="width: 100%">
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
                        v-model="county.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                county.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="code"
                        v-model="county.code"
                        label="FORM.LABELS.CODE"
                        :required="false"
                        @onChange="
                            (value) => {
                                county.code = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <DistrictSelect
                        id="disctrict"
                        :value="county.district"
                        label="TREE.DISTRICT"
                        :required="true"
                        :onChange="
                            (value) => {
                                county.district = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="countyId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="county.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
