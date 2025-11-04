<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import Payment_frequencyService from './payment_frequency.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'payment_frequencyCreateView',
    data() {
        return {
            formSubmitted: false,
            payment_frequencyId: null,
            payment_frequency: { code: null, name: null }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.payment_frequencyId = id;
            Payment_frequencyService.read(id).then((payment_frequency) => {
                setTimeout(() => {
                    this.payment_frequency = payment_frequency;
                    this.payment_frequency.i2ce_hidden = !!payment_frequency.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText
    },
    methods: {
        reset() {
            this.payment_frequency = {};
            this.formSubmitted = false;
            if (this.payment_frequencyId) {
                this.$router.push('/manage/payment_frequency_registry');
            }
        },
        validate() {
            const options = { name: this.payment_frequency.name };
            let validKey = true;
            for (const key of Object.keys(options)) {
                if (!options[key]) {
                    validKey = false;
                    break;
                }
            }

            return validKey;
        },
        createPayment_frequency() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.payment_frequencyId ? Payment_frequencyService.update(this.payment_frequencyId, this.payment_frequency) : Payment_frequencyService.create(this.payment_frequency);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/payment_frequency_registry?id=${response.id}`);
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
        <h4>{{ payment_frequencyId ? $t('TREE.PAYMENT_FREQUENCY_UPDATE') : $t('TREE.PAYMENT_FREQUENCY_NEW') }}</h4>

        <form @submit.prevent="createPayment_frequency" style="width: 100%">
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
                        v-model="payment_frequency.code"
                        label="FORM.LABELS.CODE"
                        :required="false"
                        @onChange="
                            (value) => {
                                payment_frequency.code = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="name"
                        v-model="payment_frequency.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                payment_frequency.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="payment_frequencyId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="payment_frequency.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
