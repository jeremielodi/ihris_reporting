<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import ContactService from './contact.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'contactCreateView',
    data() {
        return {
            formSubmitted: false,
            contactId: null,
            contact: { name: null, address: null, mobile_phone: null, telephone: null, alt_telephone: null, email: null, fax: null, notes: null }
        };
    },
    created() {
        const { id, personId, typeId } = this.$route.query;
        this.contact.person_id = personId;
        this.contact.contact_type = typeId;
        if (id) {
            this.contactId = id;
            ContactService.read(id).then((contact) => {
                setTimeout(() => {
                    this.contact = contact;
                    this.contact.i2ce_hidden = !!contact.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText
    },
    methods: {
        reset() {
            this.contact = {};
            this.formSubmitted = false;
            if (this.contactId) {
                window.history.back();
            }
        },
        validate() {
            const options = {
                address: this.contact.address,
                mobile_phone: this.contact.mobile_phone,
            };
            console.log(options);
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
        createContact() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.contactId ? ContactService.update(this.contactId, this.contact) : ContactService.create(this.contact);
            operation
                .then(() => {
                    NotifyService.success(this, '', null);
                    window.history.back();
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
        <h4>{{ contactId ? $t('TREE.CONTACT_UPDATE') : $t('TREE.CONTACT_NEW') }}</h4>

        <form @submit.prevent="createContact" style="width: 100%">
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
                        id="address"
                        v-model="contact.address"
                        label="FORM.LABELS.ADDRESS"
                        :required="true"
                        @onChange="
                            (value) => {
                                contact.address = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="mobile_phone"
                        v-model="contact.mobile_phone"
                        label="FORM.LABELS.MOBILE_PHONE"
                        :required="true"
                        @onChange="
                            (value) => {
                                contact.mobile_phone = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="telephone"
                        v-model="contact.telephone"
                        label="FORM.LABELS.PHONE"
                        :required="false"
                        @onChange="
                            (value) => {
                                contact.telephone = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="alt_telephone"
                        v-model="contact.alt_telephone"
                        label="FORM.LABELS.ALT_PHONE"
                        :required="false"
                        @onChange="
                            (value) => {
                                contact.alt_telephone = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">


                    <MyInputText
                        id="email"
                        v-model="contact.email"
                        label="FORM.LABELS.EMAIL"
                        type="email"
                        :required="false"
                        @onChange="
                            (value) => {
                                contact.email = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="fax"
                        v-model="contact.fax"
                        label="FORM.LABELS.FAX"
                        :required="false"
                        @onChange="
                            (value) => {
                                contact.fax = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="notes"
                        v-model="contact.notes"
                        label="FORM.LABELS.NOTES"
                        :required="false"
                        @onChange="
                            (value) => {
                                contact.notes = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <div v-if="contactId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="contact.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
