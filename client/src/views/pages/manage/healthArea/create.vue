<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import CountySelect from '@/components/CountySelect.vue';
import HealthAreaService from './healtharea.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'healthareaCreateView',
    data() {
        return {
            formSubmitted: false,
            healthareaId: null,
            healtharea: { name: null, code: null, county: null }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.healthareaId = id;
            HealthAreaService.read(id).then((healtharea) => {
                setTimeout(() => {
                    this.healtharea = healtharea;
                    this.healtharea.i2ce_hidden = !!healtharea.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText,
        CountySelect
    },
    methods: {
        reset() {
            this.healtharea = {};
            this.formSubmitted = false;
            if (this.healthareaId) {
                this.$router.push('/manage/health_area_registry');
            }
        },
        validate() {
            const options = {
                name: this.healtharea.name,
                county: this.healtharea.county
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
        createHealthArea() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.healthareaId ? HealthAreaService.update(this.healthareaId, this.healtharea) : HealthAreaService.create(this.healtharea);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/healtha_rea_registry?id=${response.id}`);
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
        <h4>{{ healthareaId ? $t('TREE.HEALTH_AREA_UPDATE') : $t('TREE.HEALTH_AREA_NEW') }}</h4>

        <form @submit.prevent="createHealthArea" style="width: 100%">
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
                        v-model="healtharea.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                healtharea.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="code"
                        v-model="healtharea.code"
                        label="FORM.LABELS.CODE"
                        :required="false"
                        @onChange="
                            (value) => {
                                healtharea.code = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <CountySelect
                        id="county"
                        :value="healtharea.county"
                        label="TREE.HEALTH_AREA"
                        :required="false"
                        :onChange="
                            (value) => {
                                healtharea.county = value.id;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="healthareaId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="healtharea.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
