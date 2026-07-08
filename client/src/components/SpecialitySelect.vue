<script>
import { defineComponent } from 'vue';
import SpecialityService from '@/views/pages/manage/speciality/specialityService';

export default defineComponent({
    name: 'SpecialitySelect',
    props: {
        label: {
            type: String,
            default: 'FORM.LABELS.PARENT'
        },
        required: {
            type: Boolean,
            default: false
        },
        value: {
            type: String,
            default: null
        },
        onChange: {
            type: Function,
            required: true
        },
        validationTrigger: {
            type: Boolean,
            default: false
        }
    },
    data() {
        return {
            specialities: [],
            selectedSpeciality: null,
            showError: false
        };
    },
    watch: {
        value: {
            immediate: true,
            handler(newVal) {
                if (newVal) {
                    this.selectedSpeciality = this.specialities.find(s => s.id === newVal) || null;
                }
            }
        },
        validationTrigger() {
            if (this.required && !this.selectedSpeciality) {
                this.showError = true;
            } else {
                this.showError = false;
            }
        }
    },
    created() {
        this.loadSpecialities();
    },
    methods: {
        loadSpecialities() {
            SpecialityService.read().then(specialities => {
                this.specialities = specialities;
                if (this.value) {
                    this.selectedSpeciality = this.specialities.find(s => s.id === this.value) || null;
                }
            });
        },
        handleChange(event) {
            this.selectedSpeciality = event.value;
            this.showError = false;
            this.onChange(this.selectedSpeciality);
        }
    }
});
</script>

<template>
    <div class="p-field">
        <label :for="id" class="p-label">
            {{ $t(label) }}
            <span v-if="required" class="p-required">*</span>
        </label>
        <Dropdown
            :id="id"
            v-model="selectedSpeciality"
            :options="specialities"
            optionLabel="name"
            optionValue="id"
            :placeholder="$t('FORM.PLACEHOLDERS.SELECT_SPECIALITY')"
            @change="handleChange"
            :class="{ 'p-invalid': showError }"
            filter
            showClear
        />
        <small v-if="showError" class="p-error">
            {{ $t('FORM.ERRORS.REQUIRED') }}
        </small>
    </div>
</template>