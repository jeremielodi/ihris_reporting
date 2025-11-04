<script lang="ts">
import { defineComponent } from 'vue';
import Dropdown from 'primevue/dropdown';
import employment_statuservice from '@/views/pages/manage/employment_status/employment_status.service';

export default defineComponent({
    name: 'employment_statuserviceSelect',
    components: { Dropdown },
    props: {
        id: { type: String, required: true },
        value: { type: String, default: null },
        label: { type: String, required: true },
        onChange: { type: Function, required: true },
        required: { type: Boolean, default: false },
        validationTrigger: { type: Boolean, default: false }
    },
    data() {
        return {
            employment_status: [],
            dropdownValue: null
        };
    },
    computed: {
        showInvalidMsg() {
            return this.required && this.validationTrigger && !this.dropdownValue;
        }
    },
    watch: {
        // When numeric value changes, fetch the selected classification object
        value(newVal) {
            if (newVal !== null && newVal !== undefined) {
                const result = this.employment_status.filter((r) => r.id === newVal)[0];
                this.dropdownValue = result;
            } else {
                this.dropdownValue = null;
            }
        }
    },
    async mounted() {
        const result = await employment_statuservice.read(null, {});
        this.employment_status = result || [];
    },
    methods: {
        onSelect(e) {
            const classification = e.value || this.dropdownValue;
            this.dropdownValue = classification;
            this.onChange(classification);
        }
    }
});
</script>

<template>
    <div class="field" style="margin-top:10px">
        <label :for="id" :class="showInvalidMsg ? 'text-danger' : ''">
            <b>{{ $t(label) }}</b>
        </label>
        <span v-if="required" class="text-danger">*</span>

        <div class="col-12" style="padding: 0px">
            <Dropdown :id="id" v-model="dropdownValue" filter :options="employment_status" optionLabel="name" style="width: 100%" placeholder="Select" @change="onSelect" :class="{ 'p-invalid': showInvalidMsg }" />
        </div>
        <span v-if="showInvalidMsg" class="has-error text-danger">
            {{ $t('FORM.ERRORS.REQUIRED') }}
        </span>
    </div>
</template>

<style scoped>
.text-danger {
    color: #dc3545;
}
.has-error {
    font-size: 0.875rem;
}
</style>

