<script lang="ts">
import { defineComponent } from 'vue';
import Dropdown from 'primevue/dropdown';
import orgUnitService from '@/views/pages/manage/organization_level/level.service';

export default defineComponent({
    name: 'orgUnitSelect',
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
            orgUnits: [],
            dropdownValue: null
        };
    },
    computed: {
        showInvalidMsg() {
            return this.required && this.validationTrigger && !this.dropdownValue;
        }
    },
    watch: {
        // When numeric value changes, fetch the selected orgUnit object
        value(newVal) {
            if (newVal !== null && newVal !== undefined) {
                const result = this.orgUnits.filter((r) => r.id === newVal)[0];
                this.dropdownValue = result;
            } else {
                this.dropdownValue = null;
            }
        }
    },
    async mounted() {
        const result = await orgUnitService.read(null, {});
        this.orgUnits = result || [];
    },
    methods: {
        onSelect(e) {
            const orgUnit = e.value || this.dropdownValue;
            this.dropdownValue = orgUnit;
            this.onChange(orgUnit);
        }
    }
});
</script>

<template>
    <div class="field">
        <label :for="id" :class="showInvalidMsg ? 'text-danger' : ''">
            <b>{{ $t(label) }}</b>
        </label>
        <span v-if="required" class="text-danger">*</span>

        <div class="col-12" style="padding: 0px">
            <Dropdown :id="id" v-model="dropdownValue" filter :options="orgUnits" optionLabel="name" style="width: 100%" placeholder="Select" @change="onSelect" :class="{ 'p-invalid': showInvalidMsg }" />
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
