<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import Contact_typeService from './contact_type.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'contact_typeCreateView',
    data() {
        return {
            formSubmitted: false,
            contact_typeId: null,
            contact_type: { name: null, code: null }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.contact_typeId = id;
            Contact_typeService.read(id).then((contact_type) => {
                setTimeout(() => {
                    this.contact_type = contact_type;
                    this.contact_type.i2ce_hidden = !!contact_type.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText
    },
    methods: {
        reset() {
            this.contact_type = {};
            this.formSubmitted = false;
            if (this.contact_typeId) {
                this.$router.push('/manage/contact_type_registry');
            }
        },
        validate() {
            const options = { name: this.contact_type.name };
            let validKey = true;
            for (const key of Object.keys(options)) {
                if (!options[key]) {
                    validKey = false;
                    break;
                }
            }

            return validKey;
        },
        createContact_type() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.contact_typeId ? Contact_typeService.update(this.contact_typeId, this.contact_type) : Contact_typeService.create(this.contact_type);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/contact_type_registry?id=${response.id}`);
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
        <h4>{{ contact_typeId ? $t('TREE.CONTACT_TYPE_UPDATE') : $t('TREE.CONTACT_TYPE_NEW') }}</h4>

        <form @submit.prevent="createContact_type" style="width: 100%">
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
                        v-model="contact_type.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                contact_type.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="code"
                        v-model="contact_type.code"
                        label="FORM.LABELS.CODE"
                        :required="false"
                        @onChange="
                            (value) => {
                                contact_type.code = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="contact_typeId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="contact_type.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
