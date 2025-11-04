<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import InstitutionTypeService from './institution_type.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'institution_typeCreateView',
    data() {
        return {
            formSubmitted: false,
            institution_typeId: null,
            institution_type: { name: null, code: null }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.institution_typeId = id;
            InstitutionTypeService.read(id).then((institution_type) => {
                setTimeout(() => {
                    this.institution_type = institution_type;
                    this.institution_type.i2ce_hidden = !!institution_type.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText
    },
    methods: {
        reset() {
            this.institution_type = {};
            this.formSubmitted = false;
            if (this.institution_typeId) {
                this.$router.push('/manage/institution_type_registry');
            }
        },
        validate() {
            const options = { name: this.institution_type.name };
            let validKey = true;
            for (const key of Object.keys(options)) {
                if (!options[key]) {
                    validKey = false;
                    break;
                }
            }

            return validKey;
        },
        createInstitution_type() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.institution_typeId ? InstitutionTypeService.update(this.institution_typeId, this.institution_type) : InstitutionTypeService.create(this.institution_type);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/institution_type_registry?id=${response.id}`);
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
        <h4>{{ institution_typeId ? $t('TREE.INSTITUTION_TYPE_UPDATE') : $t('TREE.INSTITUTION_TYPE_NEW') }}</h4>

        <form @submit.prevent="createInstitution_type" style="width: 100%">
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
                        v-model="institution_type.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                institution_type.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="code"
                        v-model="institution_type.code"
                        label="FORM.LABELS.CODE"
                        :required="false"
                        @onChange="
                            (value) => {
                                institution_type.code = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="institution_typeId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="institution_type.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
