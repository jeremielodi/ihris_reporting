<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import CountrySelect from '@/components/CountrySelect.vue';
import RegionService from './region.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'regionCreateView',
    data() {
        return {
            formSubmitted: false,
            regionId: null,
            region: { name: null, code: null, country: null }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.regionId = id;
            RegionService.read(id).then((region) => {
                setTimeout(() => {
                    this.region = region;
                    this.region.i2ce_hidden = !!region.i2ce_hidden;
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
            this.region = {};
            this.formSubmitted = false;
            if (this.regionId) {
                this.$router.push('/manage/region_registry');
            }
        },
        validate() {
            const options = { 
                name: this.region.name,
                country: this.region.country
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
        createRegion() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.regionId ? RegionService.update(this.regionId, this.region) : RegionService.create(this.region);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/region_registry?id=${response.id}`);
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
        <h4>{{ regionId ? $t('TREE.REGION_UPDATE') : $t('TREE.REGION_NEW') }}</h4>

        <form @submit.prevent="createRegion" style="width: 100%">
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
                        v-model="region.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                region.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="code"
                        v-model="region.code"
                        label="FORM.LABELS.CODE"
                        :required="false"
                        @onChange="
                            (value) => {
                                region.code = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <CountrySelect
                        id="parent"
                        :value="region.parent"
                        label="FORM.LABELS.COUNTRY"
                        :required="false"
                        :onChange="
                            (value) => {
                                region.country = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="regionId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="region.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
