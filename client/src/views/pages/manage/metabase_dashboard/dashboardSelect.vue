<script>
import { defineComponent } from 'vue';
import Dropdown from 'primevue/dropdown';
import metabaseService from '@/views/pages/career/metabase/metabase.service';
import dashboardService from './dashboard.service';

export default defineComponent({
    name: 'MetabaseDashboardSelect',
    components: { Dropdown },
    props: {
        id: { type: String, required: true },
        modelValue: { default: null },
        label: { type: String, required: true },
        required: { type: Boolean, default: false },
        validationTrigger: { type: Boolean, default: false },
        excludeUuid: { type: String, default: null }
    },
    emits: ['onChange'],
    data() {
        return {
            options: [],
            selected: null,
            loading: false
        };
    },
    computed: {
        showInvalidMsg() {
            return this.required && this.validationTrigger && !this.selected;
        }
    },
    watch: {
        modelValue(newVal) {
            this.applySelectedFromValue(newVal);
        }
    },
    async mounted() {
        this.loading = true;
        try {
            const [mbDashboards, registered] = await Promise.all([metabaseService.listDashboards(), dashboardService.read()]);
            const usedIds = new Set((registered || []).filter((d) => d.uuid !== this.excludeUuid).map((d) => d.mb_dashboard_id));
            this.options = (mbDashboards || []).map((d) => ({ ...d, disabledOption: usedIds.has(d.id) }));
            this.applySelectedFromValue(this.modelValue);
        } finally {
            this.loading = false;
        }
    },
    methods: {
        applySelectedFromValue(value) {
            if (value === null || value === undefined || value === '') {
                this.selected = null;
                return;
            }
            this.selected = this.options.find((o) => o.id === Number(value)) || null;
        },
        onSelect(e) {
            const dashboard = e.value;
            this.selected = dashboard;
            this.$emit('onChange', dashboard);
        }
    }
});
</script>

<template>
    <div class="grid" style="padding: 10px; margin-top: 5px">
        <div class="col-12" style="padding: 0px; padding-bottom: 4px; font-size: 15px">
            <label :for="id">{{ $t(label) }}<span v-if="required" style="color: red">*</span></label>
        </div>
        <div class="col-12" style="padding: 0px">
            <Dropdown
                :id="id"
                v-model="selected"
                :options="options"
                optionLabel="name"
                optionDisabled="disabledOption"
                filter
                :loading="loading"
                :class="{ 'p-invalid': showInvalidMsg }"
                placeholder="Select"
                style="width: 100%"
                @change="onSelect"
            />
            <small v-if="showInvalidMsg && validationTrigger" class="p-error">{{ $t('FORM.ERRORS.REQUIRED') }}</small>
        </div>
    </div>
</template>
