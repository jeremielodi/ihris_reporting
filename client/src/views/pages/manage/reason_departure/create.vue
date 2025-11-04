<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import ReasonDepartureService from './reason_departure.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'reason_departureCreateView',
    data() {
        return {
            formSubmitted: false,
            reason_departureId: null,
            reason_departure: { code: null, name: null }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.reason_departureId = id;
            ReasonDepartureService.read(id).then((reason_departure) => {
                setTimeout(() => {
                    this.reason_departure = reason_departure;
                    this.reason_departure.i2ce_hidden = !!reason_departure.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText
    },
    methods: {
        reset() {
            this.reason_departure = {};
            this.formSubmitted = false;
            if (this.reason_departureId) {
                this.$router.push('/manage/reason_departure_registry');
            }
        },
        validate() {
            const options = { name: this.reason_departure.name };
            let validKey = true;
            for (const key of Object.keys(options)) {
                if (!options[key]) {
                    validKey = false;
                    break;
                }
            }

            return validKey;
        },
        createReason_departure() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.reason_departureId ? ReasonDepartureService.update(this.reason_departureId, this.reason_departure) : ReasonDepartureService.create(this.reason_departure);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/reason_departure_registry?id=${response.id}`);
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
        <h4>{{ reason_departureId ? $t('TREE.REASON_DEPARTURE_UPDATE') : $t('TREE.REASON_DEPARTURE_NEW') }}</h4>

        <form @submit.prevent="createReason_departure" style="width: 100%">
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
                        v-model="reason_departure.code"
                        label="FORM.LABELS.CODE"
                        :required="false"
                        @onChange="
                            (value) => {
                                reason_departure.code = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="name"
                        v-model="reason_departure.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                reason_departure.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="reason_departureId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="reason_departure.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
