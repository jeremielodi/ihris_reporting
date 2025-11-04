<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';

import Facility_typeService from './facility_type.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'facility_typeCreateView',
    data() {
        return {
            formSubmitted: false,
            facility_typeId: null,
            facility_type: { name: null, code: null }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.facility_typeId = id;
            Facility_typeService.read(id).then((facility_type) => {
                setTimeout(() => {
                    this.facility_type = facility_type;
                    this.facility_type.i2ce_hidden = !!facility_type.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText,
    },
    methods: {
        reset() {
            this.facility_type = {};
            this.formSubmitted = false;
            if (this.facility_typeId) {
                this.$router.push('/manage/facility_type_registry');
            }
        },
        validate() {
            const options = { name: this.facility_type.name, parentError: this.facility_typeId ? this.facility_typeId == this.facility_type.parent : true };
            let validKey = true;
            for (const key of Object.keys(options)) {
                if (!options[key]) {
                    validKey = false;
                    break;
                }
            }

            return validKey;
        },
        createFacilityType() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.facility_typeId ? Facility_typeService.update(this.facility_typeId, this.facility_type) : Facility_typeService.create(this.facility_type);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/facility_type_registry?id=${response.id}`);
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
        <h4>{{ facility_typeId ? $t('TREE.FACILITY_TYPE_UPDATE') : $t('TREE.FACILITY_TYPE_NEW') }}</h4>

        <form @submit.prevent="createFacilityType" style="width: 100%">
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
                        v-model="facility_type.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                facility_type.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="code"
                        v-model="facility_type.code"
                        label="FORM.LABELS.CODE"
                        :required="false"
                        @onChange="
                            (value) => {
                                facility_type.code = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="facility_typeId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="facility_type.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
