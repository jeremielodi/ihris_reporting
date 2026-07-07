<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import employee_statusService from './employee_status.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'Employee_statusCreateView',
    data() {
        return {
            formSubmitted: false,
            employee_statusId: null,
            employee_status: {
                id: null,
                name: null,
                translate_key: null,
                parent: '|',
                remap: null,
                i2ce_hidden: 0
            }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.employee_statusId = id;
            employee_statusService.read(id)
                .then((employee_status) => {
                    this.employee_status = employee_status;
                    // Convertir i2ce_hidden en boolean pour le checkbox
                    this.employee_status.i2ce_hidden = !!employee_status.i2ce_hidden;
                })
                .catch((error) => {
                    console.error('Error loading employee status:', error);
                    NotifyService.danger(this, 'EMPLOYEE_STATUS.LOAD_ERROR', null);
                });
        }
    },
    components: {
        MyInputText
    },
    methods: {
        reset() {
            this.employee_status = {
                id: null,
                name: null,
                translate_key: null,
                parent: '|',
                remap: null,
                i2ce_hidden: 0
            };
            this.formSubmitted = false;
            if (this.employee_statusId) {
                this.$router.push('/manage/employee_status_registry');
            }
        },

        validate() {
            const requiredFields = {
                id: this.employee_status.id,
                name: this.employee_status.name
            };
            
            for (const [key, value] of Object.entries(requiredFields)) {
                if (!value || value.trim() === '') {
                    return false;
                }
            }
            return true;
        },

        createEmployee_status() {
            this.formSubmitted = true;
            
            if (!this.validate()) {
                NotifyService.danger(this, 'FORM.ERRORS.INVALID', null);
                return;
            }

            // Préparer les données pour l'API
            const data = {
                ...this.employee_status,
                i2ce_hidden: this.employee_status.i2ce_hidden ? 1 : 0
            };

            const operation = this.employee_statusId 
                ? employee_statusService.update(this.employee_statusId, data) 
                : employee_statusService.create(data);

            operation
                .then((response) => {
                    NotifyService.success(this, 'EMPLOYEE_STATUS.SAVE_SUCCESS', null);
                    this.$router.push(`/manage/employee_status_registry?id=${response.id}`);
                })
                .catch((error) => {
                    console.error('Save error:', error);
                    const errorMessage = error.response?.data?.detail || 'FORM.ERRORS.SAVE_FAILED';
                    NotifyService.danger(this, errorMessage, null);
                });
        }
    }
});
</script>

<template>
    <div class="card manage-container">
        <h4>{{ employee_statusId ? $t('TREE.EMPLOYEE_STATUS_UPDATE') : $t('TREE.EMPLOYEE_STATUS_NEW') }}</h4>

        <form @submit.prevent="createEmployee_status" style="width: 100%">
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

                <div class="col-12 lg:col-6 xl:col-6 p-field">
                    <MyInputText
                        id="id"
                        v-model="employee_status.id"
                        label="FORM.LABELS.ID"
                        :required="true"
                        :disabled="!!employee_statusId"
                        @onChange="
                            (value) => {
                                employee_status.id = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <MyInputText
                        id="name"
                        v-model="employee_status.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                employee_status.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                </div>

                <div class="col-12 lg:col-6 xl:col-6 p-field">
                    <MyInputText
                        id="parent"
                        v-model="employee_status.parent"
                        label="FORM.LABELS.PARENT"
                        :required="false"
                        @onChange="
                            (value) => {
                                employee_status.parent = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />


                    <div v-if="employee_statusId" class="p-field-checkbox">
                        <Checkbox 
                            id="i2ce_hidden" 
                            :binary="true" 
                            name="i2ce_hidden" 
                            variant="filled" 
                            v-model="employee_status.i2ce_hidden" 
                        />
                        <label for="i2ce_hidden">{{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>

                    <div v-else class="p-field-checkbox">
                        <Checkbox 
                            id="i2ce_hidden" 
                            :binary="true" 
                            name="i2ce_hidden" 
                            variant="filled" 
                            v-model="employee_status.i2ce_hidden" 
                        />
                        <label for="i2ce_hidden">{{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>