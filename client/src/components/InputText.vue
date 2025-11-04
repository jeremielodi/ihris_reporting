<script>
import { defineComponent, ref, watch, computed } from 'vue';

export default defineComponent({
    name: 'iHRISInputText',
    props: {
        id: { type: String, required: true },
        validationTrigger: { type: Boolean, default: false },
        required: { type: Boolean, default: false },
        label: { type: String, required: true },
        modelValue: { type: String, default: '' },
        minVal: { default: null },
        maxVal: { default: null },
        type: { type: String, default: 'text' },
        placeholder: { type: String, default: '' },
    },
    emits: ['onChange'],
    setup(props, { emit }) {
        const textValue = ref(props.modelValue);
        const minValue = ref(props.minVal);
        const maxValue = ref(props.maxVal);
        const isDefined = (value) => {
            if (props.type === 'number' && value == 0) return true;
            return value;
        };
        watch(
            () => props.modelValue,
            (newVal) => {
                textValue.value = newVal || '';
            }
        );

        const showInvalidMsg = computed(() => {
            let length = true;
            if (minValue.value) {
                if (props.type == 'text' || props.type == 'password') {
                    length = (textValue.value || '').length >= minValue.value;
                }
            }
            if (maxValue.value) {
                if (props.type == 'text' || props.type == 'password') {
                    length = (textValue.value || '').length <= maxValue.value;
                }
            }
            console.log(props.id, minValue.value, maxValue.value, length);
            return (props.required && props.validationTrigger && !isDefined(textValue.value)) ||
                (props.required && props.validationTrigger && isDefined(textValue.value) && !length);
        });

        function onChangeInput(event) {
            const target = event.target;
            textValue.value = target.value;
            emit('onChange', target.value);
        }
        function onChangeNumberInput(event) {
            textValue.value = event.value;
            emit('onChange',  event.value);
        }

        function onDateChanged() {
            emit('onChange', textValue.value);
        }
        return { textValue, showInvalidMsg,onChangeNumberInput, onChangeInput, onDateChanged };
    }
});
</script>

<template>
    <div class="grid" style="padding: 10px; margin-top: 5px">
        <div class="col-12" style="padding: 0px; padding-bottom: 4px; font-size: 15px">
            <label :for="id">{{ $t(label) }}<span v-if="required" style="color: red">*</span></label>
        </div>
        <div class="col-12" style="padding: 0px">
            <template v-if="type === 'password'">
                <Password v-model="textValue" :id="id" :invalid="showInvalidMsg" toggleMask @input="onChangeInput" :feedback="false" :showIcon="true" :inputStyle="{ width: '100%' }" />
            </template>

            <template v-if="type === 'number'">
                <InputNumber :id="id" :class="{ 'p-invalid': showInvalidMsg }" :type="type" @input="onChangeNumberInput" v-model="textValue" style="width: 100%" />
            </template>
            <template v-if="type === 'text' || type === 'email'">
                <InputText :id="id" :class="{ 'p-invalid': showInvalidMsg }" :type="type" @input="onChangeInput" v-model="textValue" :placeholder="placeholder"/>
            </template>
            <template v-if="type === 'date'">
                <Calendar :id="id" v-model="textValue" @update:modelValue="onDateChanged" :maxDate="maxVal" :inputId="id" :showIcon="true" style="width: 100%" placeholder="dd/mm/yyyy" dateFormat="dd/mm/yy"  :class="{ 'p-invalid': showInvalidMsg }"/>
            </template>

            <small v-if="showInvalidMsg && validationTrigger" class="p-error">{{ $t('FORM.ERRORS.REQUIRED') }}</small>
        </div>
    </div>
</template>

<style scoped>
.p-inputtext,
.p-password,
.p-password input {
    width: 100% !important;
}
.p-datepicker {
    padding: 0px !important;
    width: 100% !important;
}
.p-datepicker .inputtext {
    width: 100% !important;
}
</style>
