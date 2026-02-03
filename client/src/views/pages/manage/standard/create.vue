<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import ClassificationService from '@/components/ClassificationSelect.vue';
import OrgUnitTypeSelect from '@/components/OrgUnitTypeSelect.vue';

import StandardService from './standar.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'standardCreateView',
    data() {
        return {
            formSubmitted: false,
            standardId: null,
            standard: { classification_id: null, organization_unit_type_id: null, required: 0 }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.standardId = id;
            StandardService.read(id).then((standard) => {
                setTimeout(() => {
                    this.standard = standard;
                    this.standard.i2ce_hidden = !!standard.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText,
        ClassificationService,
        OrgUnitTypeSelect
    },
    methods: {
        reset() {
            this.standard = {};
            this.formSubmitted = false;
            if (this.standardId) {
                this.$router.push('/manage/org_unit_standards_registry');
            }
        },
        validate() {
            const options = { 
                classification_id: this.standard.classification_id,
                required: this.standard.required,
                organization_unit_type_id: this.standard.organization_unit_type_id
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
        createstandard() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.standardId ? StandardService.update(this.standardId, this.standard) : StandardService.create(this.standard);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/org_unit_standards_registry?id=${response.uuid}`);
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
        <h4>{{ standardId ? $t('TREE.ORG_UNIT_STANDARD_UPDATE') : $t('TREE.ORG_UNIT_STANDARD_NEW') }}</h4>

        <form @submit.prevent="createstandard" style="width: 100%">
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
                    <ClassificationService
                        id="classification_id"
                        :value="standard.classification_id"
                        label="TREE.CLASSIFICATIONS"
                        :required="true"
                        :onChange="
                            (value) => {
                                standard.classification_id = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <OrgUnitTypeSelect
                        id="organization_unit_type_id"
                        :value="standard.organization_unit_type_id"
                        label="TREE.ORG_UNIT_TYPE"
                        :required="true"
                        :onChange="
                            (value) => {
                                standard.organization_unit_type_id = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="required"
                        v-model="standard.required"
                        type="number"
                        label="FORM.LABELS.NUMBER_OF_POSITIONS"
                        :required="false"
                        @onChange="
                            (value) => {
                                standard.required = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="standardId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="standard.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
