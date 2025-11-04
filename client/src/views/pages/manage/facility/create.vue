<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import HealthAreaSelect from '@/components/HealthAreaSelect.vue';
import FacilityTypeSelect from '@/components/FacilityTypeSelect.vue';
import FacilityService from './facility.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'facilityCreateView',
    data() {
        return {
            formSubmitted: false,
            facilityId: null,
            facility: { name: null, code: null, location: null, facility_type: null }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.facilityId = id;
            FacilityService.read(id).then((facility) => {
                setTimeout(() => {
                    this.facility = facility;
                    this.facility.i2ce_hidden = !!facility.i2ce_hidden;
                }, 2000);
            });
        }
    },
    components: {
        MyInputText,
        HealthAreaSelect,
        FacilityTypeSelect,
    },
    methods: {
        reset() {
            this.facility = {};
            this.formSubmitted = false;
            if (this.facilityId) {
                this.$router.push('/manage/facility_registry');
            }
        },
        validate() {
            const options = {
                name: this.facility.name,
                location: this.facility.location,
                facility_type: this.facility.facility_type
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
        createFacility() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.facilityId ? FacilityService.update(this.facilityId, this.facility) : FacilityService.create(this.facility);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/facility_registry?id=${response.id}`);
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
        <h4>{{ facilityId ? $t('TREE.FACILITY_UPDATE') : $t('TREE.FACILITY_NEW') }}</h4>

        <form @submit.prevent="createFacility" style="width: 100%">
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
                        v-model="facility.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                facility.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="code"
                        v-model="facility.code"
                        label="FORM.LABELS.CODE"
                        :required="false"
                        @onChange="
                            (value) => {
                                facility.code = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <HealthAreaSelect
                        id="location"
                        :value="facility.location"
                        label="TREE.HEALTH_AREA"
                        :required="false"
                        :onChange="
                            (value) => {
                                facility.location = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <FacilityTypeSelect
                        id="facility_type"
                        :value="facility.facility_type"
                        label="TREE.FACILITY_TYPE"
                        :required="true"
                        :onChange="
                            (value) => {
                                facility.facility_type = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <div v-if="facilityId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="facility.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
