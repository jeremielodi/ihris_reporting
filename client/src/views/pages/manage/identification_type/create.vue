<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import Identification_typeService from './identification_type.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'identification_typeCreateView',
    data() {
        return {
            formSubmitted: false,
            identification_typeId: null,
            identification_type: { code: null, name: null }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.identification_typeId = id;
            Identification_typeService.read(id).then((identification_type) => {
                setTimeout(() => {
                    this.identification_type = identification_type;
                    this.identification_type.i2ce_hidden = !!identification_type.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText
    },
    methods: {
        reset() {
            this.identification_type = {};
            this.formSubmitted = false;
            if (this.identification_typeId) {
                this.$router.push('/manage/identification_type_registry');
            }
        },
        validate() {
            const options = { name: this.identification_type.name };
            let validKey = true;
            for (const key of Object.keys(options)) {
                if (!options[key]) {
                    validKey = false;
                    break;
                }
            }

            return validKey;
        },
        createIdentification_type() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.identification_typeId ? Identification_typeService.update(this.identification_typeId, this.identification_type) : Identification_typeService.create(this.identification_type);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/identification_type_registry?id=${response.id}`);
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
        <h4>{{ identification_typeId ? $t('TREE.IDENTIFICATION_TYPE_UPDATE') : $t('TREE.IDENTIFICATION_TYPE_NEW') }}</h4>

        <form @submit.prevent="createIdentification_type" style="width: 100%">
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
                        v-model="identification_type.code"
                        label="FORM.LABELS.CODE"
                        :required="false"
                        @onChange="
                            (value) => {
                                identification_type.code = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="name"
                        v-model="identification_type.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                identification_type.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="identification_typeId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="identification_type.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
