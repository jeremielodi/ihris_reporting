<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import SpecialityService from './specialityService';
import NotifyService from '../../../../service/Notify.service';

export default defineComponent({
    name: 'specialityCreateView',
    data() {
        return {
            formSubmitted: false,
            specialityId: null,
            speciality: {
                code: null,
                name: null,
                description: null
            }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.specialityId = id;
            SpecialityService.read(id).then((speciality) => {
                setTimeout(() => {
                    this.speciality = speciality;
                    this.speciality.i2ce_hidden = !!speciality.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText,
    },
    methods: {
        reset() {
            this.speciality = {};
            this.formSubmitted = false;

            if (this.specialityId) {
                this.$router.push('/manage/speciality_registry');
            }
        },
        validate() {
            const options = {
                name: this.speciality.name
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
        createSpeciality() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.specialityId ? SpecialityService.update(this.specialityId, this.speciality) : SpecialityService.create(this.speciality);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/speciality_registry?id=${response.id}`);
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
        <h4>{{ specialityId ? $t('TREE.SPECIALITY_UPDATE') : $t('TREE.SPECIALITY_NEW') }}</h4>

        <form @submit.prevent="createSpeciality" style="width: 100%">
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
                        id="code"
                        v-model="speciality.code"
                        label="FORM.LABELS.CODE"
                        :required="false"
                        @onChange="
                            (value) => {
                                speciality.code = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="name"
                        v-model="speciality.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                speciality.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="specialityId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="speciality.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>