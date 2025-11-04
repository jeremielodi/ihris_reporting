<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import orgUnitService from './orgUnit.service';
import NotifyService from '@/service/Notify.service';
import PyramidSelect from '@/components/pyramidSelect/pyramidSelect.vue';
import OrganizationLevelSelect from '@/components/OrganizationLevelSelect.vue';

export default defineComponent({
    name: 'OrgUnitCreateCreateView',
    data() {
        return {
            formSubmitted: false,
            orgUnitId: null,
            orgUnit: {
                name: null,
                level: null,
                parnet: null
            }
        };
    },
    created() {
        const { id, parent } = this.$route.query;
        if (id) {
            this.orgUnitId = id;
            orgUnitService.read(id).then((orgUnit) => {
                setTimeout(() => {
                    this.orgUnit = orgUnit;
                    this.orgUnit.i2ce_hidden = !!orgUnit.i2ce_hidden;
                }, 400);
            });
        }
        if (parent) {
            setTimeout(() => {
                this.orgUnit.parent = parent;
            }, 1000);
        }
    },
    components: {
        MyInputText,
        PyramidSelect,
        OrganizationLevelSelect
    },
    methods: {
        reset() {
            this.orgUnit = {};
            this.formSubmitted = false;
            this.$router.push('/manage/org_unit_registry');
        },
        validate() {
            const options = {
                name: this.orgUnit.name,
                level: this.orgUnit.level
            };
            let validKey = true;
            for (const key of Object.keys(options)) {
                if (!options[key]) {
                    console.log(key);
                    validKey = false;
                    break;
                }
            }

            return validKey;
        },
        createorgUnit() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.orgUnitId ? orgUnitService.update(this.orgUnitId, this.orgUnit) : orgUnitService.create(this.orgUnit);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/org_unit_registry?id=${response.id}`);
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
        <h4>{{ orgUnitId ? $t('TREE.ORG_UNIT_UPDATE') : $t('TREE.ORG_UNIT_NEW') }}</h4>

        <form @submit.prevent="createorgUnit" style="width: 100%">
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
                        v-model="orgUnit.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                orgUnit.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <OrganizationLevelSelect
                        id="level"
                        :value="this.orgUnit.level"
                        label="FORM.LABELS.LEVEL"
                        :required="true"
                        :onChange="
                            (value) => {
                                this.orgUnit.level = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                     <PyramidSelect
                        id="parent"
                        :value="{ key: this.orgUnit.parent }"
                        label="FORM.LABELS.PARENT"
                        :onChange="
                            (value) => {
                                this.orgUnit.parent = value.key;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="orgUnitId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="orgUnit.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
