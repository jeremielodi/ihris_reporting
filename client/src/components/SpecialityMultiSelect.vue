<script>
import { defineComponent } from 'vue';
import SpecialityService from '@/views/pages/manage/speciality/specialityService';

export default defineComponent({
    name: 'SpecialityMultiSelect',
    props: {
        id: {                          // ✅ FIXED: Added missing id prop
            type: String,
            default: () => `speciality-multiselect-${Math.random().toString(36).substr(2, 9)}`
        },
        label: {
            type: String,
            default: 'FORM.LABELS.SPECIALITIES'
        },
        required: {
            type: Boolean,
            default: false
        },
        value: {
            type: Array,
            default: () => []
        },
        onChange: {
            type: Function,
            required: true
        },
        validationTrigger: {
            type: Boolean,
            default: false
        },
        placeholder: {
            type: String,
            default: 'FORM.PLACEHOLDERS.SELECT_SPECIALITIES'
        },
        disabled: {
            type: Boolean,
            default: false
        },
        showFilter: {
            type: Boolean,
            default: true
        },
        filterPlaceholder: {
            type: String,
            default: 'FORM.PLACEHOLDERS.SEARCH_SPECIALITIES'
        },
        maxSelectedLabels: {
            type: Number,
            default: 2
        },
        selectionLimit: {
            type: Number,
            default: null
        },
        display: {
            type: String,
            default: 'comma',
            validator: (value) => ['comma', 'chip', 'badge'].includes(value)
        },
        optionLabel: {
            type: String,
            default: 'name'
        },
        optionValue: {
            type: String,
            default: 'id'
        },
        appendTo: {
            type: String,
            default: 'body'
        }
    },
    data() {
        return {
            specialities: [],
            selectedSpecialities: [],    // Now stores OBJECTS (full speciality items)
            showError: false,
            isLoading: false
        };
    },
    watch: {
        value: {
            immediate: true,
            deep: true,
            handler(newVal) {
                if (!newVal || !Array.isArray(newVal)) {
                    this.selectedSpecialities = [];
                    return;
                }
                // ✅ FIXED: Use optionValue prop for matching, not hardcoded .id
                this.selectedSpecialities = this.specialities.filter(s => 
                    newVal.includes(this.resolveValue(s))
                );
            }
        },
        validationTrigger() {
            this.validate();
        },
        selectedSpecialities: {
            deep: true,
            handler() {
                this.validate();
            }
        }
    },
    created() {
        this.loadSpecialities();
    },
    methods: {
        // ✅ FIXED: Helper to safely get a property using optionValue/optionLabel
        resolveValue(item) {
            return item?.[this.optionValue] ?? item;
        },
        resolveLabel(item) {
            return item?.[this.optionLabel] ?? item;
        },

        async loadSpecialities() {
            this.isLoading = true;
            try {
                const specialities = await SpecialityService.read();
                this.specialities = specialities;
                
                // ✅ FIXED: Sync with value prop using optionValue
                if (this.value && Array.isArray(this.value)) {
                    this.selectedSpecialities = this.specialities.filter(s => 
                        this.value.includes(this.resolveValue(s))
                    );
                }
            } catch (error) {
                console.error('Error loading specialities:', error);
            } finally {
                this.isLoading = false;
            }
        },

        validate() {
            if (this.required && (!this.selectedSpecialities || this.selectedSpecialities.length === 0)) {
                this.showError = true;
            } else {
                this.showError = false;
            }
        },

        handleChange(event) {
            // event.value contains full objects because we do NOT bind optionValue on v-model
            this.selectedSpecialities = event.value || [];
            this.showError = false;
            
            // ✅ FIXED: Emit IDs using optionValue prop
            const selectedIds = this.selectedSpecialities.map(s => this.resolveValue(s));
            this.onChange(selectedIds);
        },

        handleRemove(removedSpeciality) {
            this.selectedSpecialities = this.selectedSpecialities.filter(
                s => this.resolveValue(s) !== this.resolveValue(removedSpeciality)
            );
            this.showError = false;
            
            const selectedIds = this.selectedSpecialities.map(s => this.resolveValue(s));
            this.onChange(selectedIds);
        },

        handleClear() {
            this.selectedSpecialities = [];
            this.showError = false;
            this.onChange([]);
        },

        selectAll() {
            let toSelect = [...this.specialities];
            if (this.selectionLimit) {
                toSelect = toSelect.slice(0, this.selectionLimit);
            }
            this.selectedSpecialities = toSelect;
            
            const selectedIds = toSelect.map(s => this.resolveValue(s));
            this.onChange(selectedIds);
        },

        clearAll() {
            this.handleClear();
        },

        isSelected(speciality) {
            return this.selectedSpecialities.some(s => 
                this.resolveValue(s) === this.resolveValue(speciality)
            );
        },

        getSelectedNames() {
            return this.selectedSpecialities.map(s => this.resolveLabel(s)).join(', ');
        },

        isSelectionLimitReached() {
            if (!this.selectionLimit) return false;
            return this.selectedSpecialities.length >= this.selectionLimit;
        },

        getRemainingCount() {
            if (!this.selectionLimit) return null;
            return this.selectionLimit - this.selectedSpecialities.length;
        },

        // ✅ FIXED: Safe translation helper
        $t(key, fallback = '') {
            if (this.$i18n?.t) {
                return this.$i18n.t(key);
            }
            return fallback || key;
        }
    },
    computed: {
        // ✅ FIXED: Always show all options; let MultiSelect handle disabled state
        availableSpecialities() {
            return this.specialities;
        },

        displayText() {
            if (this.selectedSpecialities.length === 0) {
                return this.$t(this.placeholder, this.placeholder);
            }
            if (this.display === 'comma') {
                return this.getSelectedNames();
            }
            return `${this.selectedSpecialities.length} ${this.$t('FORM.LABELS.SELECTED', 'selected')}`;
        },

        hasValue() {
            return this.selectedSpecialities && this.selectedSpecialities.length > 0;
        }
    }
});
</script>

<template>
    <div class="p-field speciality-multiselect">
        <label :for="id" class="p-label">
            {{ $t(label, label) }}
            <span v-if="required" class="p-required">*</span>
            <span v-if="selectionLimit" class="p-field-info">
                ({{ $t('FORM.LABELS.MAX', 'Max') }} {{ selectionLimit }})
            </span>
        </label>

        <!-- ✅ FIXED: Removed :optionValue from MultiSelect so v-model gets full objects -->
        <MultiSelect
            :id="id"
            v-model="selectedSpecialities"
            :options="availableSpecialities"
            :optionLabel="optionLabel"
            :placeholder="$t(placeholder, placeholder)"
            :disabled="disabled || isSelectionLimitReached()"
            :filter="showFilter"
            :filterPlaceholder="$t(filterPlaceholder, filterPlaceholder)"
            :maxSelectedLabels="maxSelectedLabels"
            :display="display"
            :appendTo="appendTo"
            :class="{ 'p-invalid': showError, 'p-disabled': disabled }"
            @change="handleChange"
            @remove="handleRemove"
            :loading="isLoading"
            :showClear="true"
            :selectionLimit="selectionLimit"
            class="w-full"
        >
            <template #header>
                <div v-if="specialities.length > 0" class="p-d-flex p-jc-between p-ai-center p-p-2">
                    <span class="p-text-secondary p-text-sm">
                        {{ $t('FORM.LABELS.TOTAL', 'Total') }}: {{ specialities.length }}
                    </span>
                
                </div>
            </template>

            <template #option="slotProps">
                <div class="p-d-flex p-ai-center speciality-option">
                    <span class="speciality-name">{{ slotProps.option[optionLabel] }}</span>
                    <span v-if="slotProps.option.code" class="speciality-code p-text-secondary p-ml-2">
                        ({{ slotProps.option.code }})
                    </span>
                    <span v-if="isSelected(slotProps.option)" class="p-ml-auto">
                        <i class="pi pi-check" style="color: var(--primary-color)"></i>
                    </span>
                </div>
            </template>

            <template #empty>
                <div class="p-text-center p-p-3">
                    <i class="pi pi-inbox p-mb-2" style="font-size: 2rem; opacity: 0.5;"></i>
                    <p class="p-text-secondary p-m-0">
                        {{ $t('FORM.MESSAGES.NO_SPECIALITIES_FOUND', 'No specialities found') }}
                    </p>
                </div>
            </template>

            <template #loadingicon>
                <i class="pi pi-spin pi-spinner"></i>
            </template>
        </MultiSelect>

        <small v-if="showError" class="p-error">
            {{ $t('FORM.ERRORS.REQUIRED', 'This field is required') }}
        </small>

        <small v-else-if="selectionLimit && getRemainingCount() !== null && getRemainingCount() > 0" class="p-text-secondary">
            {{ $t('FORM.MESSAGES.REMAINING', 'Remaining') }}: {{ getRemainingCount() }}
        </small>

     

        <div v-if="display === 'chip' && hasValue" class="selected-chips p-mt-2">
            <Chip
                v-for="speciality in selectedSpecialities"
                :key="resolveValue(speciality)"
                :label="resolveLabel(speciality)"
                removable
                @remove="handleRemove(speciality)"
                class="p-mr-1 p-mb-1"
                :class="{ 'p-chip-disabled': disabled }"
            />
        </div>
    </div>
</template>

<style scoped>
.speciality-multiselect {
    margin-bottom: 1rem;
}

.p-label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.p-required {
    color: #f44336;
    margin-left: 0.25rem;
}

.p-field-info {
    font-weight: normal;
    font-size: 0.85rem;
    color: var(--text-secondary);
}

.speciality-option {
    padding: 0.25rem 0;
    width: 100%;
}

.speciality-name {
    font-weight: 500;
}

.speciality-code {
    font-size: 0.85rem;
}

.selected-count {
    display: flex;
    justify-content: flex-end;
}

.selected-chips {
    display: flex;
    flex-wrap: wrap;
}

.p-chip-disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .speciality-multiselect :deep(.p-multiselect) {
        width: 100% !important;
    }
}

/* Custom scrollbar for dropdown */
:deep(.p-multiselect-panel .p-multiselect-items-wrapper) {
    max-height: 200px;
    overflow-y: auto;
}

:deep(.p-multiselect-panel .p-multiselect-items-wrapper::-webkit-scrollbar) {
    width: 8px;
}

:deep(.p-multiselect-panel .p-multiselect-items-wrapper::-webkit-scrollbar-track) {
    background: #f1f1f1;
    border-radius: 4px;
}

:deep(.p-multiselect-panel .p-multiselect-items-wrapper::-webkit-scrollbar-thumb) {
    background: #c1c1c1;
    border-radius: 4px;
}

:deep(.p-multiselect-panel .p-multiselect-items-wrapper::-webkit-scrollbar-thumb:hover) {
    background: #a8a8a8;
}

/* Selection limit indicator */
.selection-limit-indicator {
    color: #f59e0b;
    font-size: 0.85rem;
    padding: 0.25rem 0.5rem;
    background: #fef3c7;
    border-radius: 4px;
    margin-top: 0.25rem;
}

/* Header styling */
:deep(.p-multiselect .p-multiselect-label) {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.25rem;
}

:deep(.p-multiselect .p-multiselect-label .p-multiselect-token) {
    margin: 0.125rem;
}

/* Loading state */
:deep(.p-multiselect.p-multiselect-loading .p-multiselect-label) {
    color: var(--text-secondary);
}

/* Error state */
.p-invalid :deep(.p-multiselect) {
    border-color: #f44336;
}

.p-invalid :deep(.p-multiselect.p-focus) {
    box-shadow: 0 0 0 2px rgba(244, 67, 54, 0.2);
    border-color: #f44336;
}
</style>