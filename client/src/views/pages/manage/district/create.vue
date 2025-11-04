<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import RegionSelect from '@/components/RegionSelect.vue';
import DistrictService from './district.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'districtCreateView',
    data() {
        return {
            formSubmitted: false,
            districtId: null,
            district: { name: null, code: null, region: null }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.districtId = id;
            DistrictService.read(id).then((district) => {
                setTimeout(() => {
                    this.district = district;
                    this.district.i2ce_hidden = !!district.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText,
        RegionSelect
    },
    methods: {
        reset() {
            this.district = {};
            this.formSubmitted = false;
            if (this.districtId) {
                this.$router.push('/manage/district_registry');
            }
        },
        validate() {
            const options = { 
                name: this.district.name,
                region: this.district.region
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
        createDistrict() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.districtId ? DistrictService.update(this.districtId, this.district) : DistrictService.create(this.district);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/district_registry?id=${response.id}`);
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
        <h4>{{ districtId ? $t('TREE.DISTRICT_UPDATE') : $t('TREE.DISTRICT_NEW') }}</h4>

        <form @submit.prevent="createDistrict" style="width: 100%">
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
                        v-model="district.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                district.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="code"
                        v-model="district.code"
                        label="FORM.LABELS.CODE"
                        :required="false"
                        @onChange="
                            (value) => {
                                district.code = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <RegionSelect
                        id="region"
                        :value="district.region"
                        label="TREE.REGION"
                        :required="true"
                        :onChange="
                            (value) => {
                                district.region = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="districtId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="district.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
