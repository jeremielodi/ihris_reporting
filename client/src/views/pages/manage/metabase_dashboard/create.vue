<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import dashboardService from './dashboard.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'DashbordCreateView',
    data() {
        return {
            formSubmitted: false,
            dashboardId: null,
            dashboard: { name: null, mb_dashboard_id: null, }
        };
    },
    created() {
        const { uuid } = this.$route.query;
        if (uuid) {
            this.dashboardId = uuid;
            dashboardService.read(uuid).then((dashboard) => {
                setTimeout(() => {
                    this.dashboard = dashboard;
                    this.dashboard.i2ce_hidden = !!dashboard.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText,
    },
    methods: {
        reset() {
            this.dashboard = {};
            this.formSubmitted = false;
            if (this.dashboardId) {
                this.$router.push('/manage/dashboard_registry');
            }
        },
        validate() {
            const options = { 
                id: this.dashboard.mb_dashboard_id,
                label: this.dashboard.label,
            };
            let validKey = true;
            for (const key of Object.keys(options)) {
                if (!options[key]) {
                    validKey = false;
                    break;
                }
            }

            return validKey;
        },
        createdashboard() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.dashboardId ? dashboardService.update(this.dashboardId, this.dashboard) : dashboardService.create(this.dashboard);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/dashboard_registry?uuid=${response.id}`);
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
        <h4>{{ dashboardId ? $t('TREE.METABASE_DASHBOARD_UPDATE') : $t('TREE.METABASE_DASHBOARD_NEW') }}</h4>

        <form @submit.prevent="createdashboard" style="width: 100%">
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
                        id="mb_dashboard_id"
                        v-model="dashboard.mb_dashboard_id"
                        label="FORM.LABELS.ID"
                        :required="true"
                        @onChange="
                            (value) => {
                                dashboard.mb_dashboard_id = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="label"
                        v-model="dashboard.label"
                        label="FORM.LABELS.LABEL"
                        :required="false"
                        @onChange="
                            (value) => {
                                dashboard.label = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="dashboardId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="dashboard.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
