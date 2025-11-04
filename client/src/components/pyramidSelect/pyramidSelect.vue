<script>
import { defineComponent } from 'vue';
import Modal from './modal.vue';
import OrgUnitService from '@/views/pages/manage/organization_units/orgUnit.service';

export default defineComponent({
    name: 'iHRISPyramidSelect',
    props: {
        id: { type: String, required: true },
        validationTrigger: { type: Boolean, default: false },
        required: { type: Boolean, default: false },
        label: { type: String, required: true },
        value: { type: Object, default: null },
        getAllNodes:  { type: Boolean, default: false },
        onChange: { type: Function, default: () => {} }
    },
    data() {
        return {
            displayModal: false,
            currentNode: {}
        };
    },
    computed: {
        showInvalidMsg() {
            return this.required && this.validationTrigger && !this.currentNode.key;
        }
    },
    components: {
        Modal
    },
    watch: {
        value(newVal) {
            if (newVal) {
                if (newVal.key === this.currentNode.key) return;
                
                if(!newVal.name) {
                    OrgUnitService.read(newVal.key)
                        .then(res => {
                        this.currentNode = {
                            id: res.id,
                            key: res.id,
                            label: res.name
                        };
                    });
                }
                else {
                    this.currentNode = {
                    id: newVal.id,
                    key: newVal.key || newVal.id,
                    label: newVal.name
                };
                }
            } else {
                this.currentNode = {};
            }
        }
    },
    methods: {
        closeDialog(node) {
            if (node) {
                this.onChange(node);
                this.currentNode = node || {};
            }
            this.displayModal = false;
        },
        openModal() {
            this.displayModal = true;
        }
    }
});
</script>

<template>
    <div class="grid" style="padding: 10px; margin-top: 5px">
        <div class="col-12" style="padding: 0px; padding-bottom: 4px; font-size: 15px">
            <label :for="id"> {{ $t(label) }} <span v-if="required" style="color: red">*</span></label>
        </div>
        <div class="col-12 p-link" style="padding: 0px">
            <InputGroup>
                <InputText type="text" placeholder="Select an organisation unit" :id="id" :disabled="displayModal" v-model="this.currentNode.label" @click="displayModal = true" :class="{ 'p-invalid': showInvalidMsg }" />
                <Button icon="pi pi-search" severity="secondary" @click="openModal()" />
            </InputGroup>

            <small v-if="showInvalidMsg && validationTrigger" class="p-error">
                {{ $t('FORM.ERRORS.REQUIRED') }}
            </small>
        </div>
        <Modal :display="displayModal" :getAllNodes="getAllNodes" :close="closeDialog" />
    </div>
</template>

<style scoped>
.p-inputtext {
    width: 100% !important;
}
</style>
