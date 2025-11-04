<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import Educational_levelService from './educational_level.service';
import NotifyService from '@/service/Notify.service';

export default defineComponent({
    name: 'educational_levelCreateView',
    data() {
        return {
            formSubmitted: false,
            educational_levelId: null,
            educational_level: { name: null, code: null }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.educational_levelId = id;
            Educational_levelService.read(id).then((educational_level) => {
                setTimeout(() => {
                    this.educational_level = educational_level;
                    this.educational_level.i2ce_hidden = !!educational_level.i2ce_hidden;
                }, 400);
            });
        }
    },
    components: {
        MyInputText
    },
    methods: {
        reset() {
            this.educational_level = {};
            this.formSubmitted = false;
            if (this.educational_levelId) {
                this.$router.push('/manage/educational_level_registry');
            }
        },
        validate() {
            const options = { name: this.educational_level.name };
            let validKey = true;
            for (const key of Object.keys(options)) {
                if (!options[key]) {
                    validKey = false;
                    break;
                }
            }

            return validKey;
        },
        createEducational_level() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.educational_levelId ? Educational_levelService.update(this.educational_levelId, this.educational_level) : Educational_levelService.create(this.educational_level);
            operation
                .then((response) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/educational_level_registry?id=${response.id}`);
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
        <h4>{{ educational_levelId ? $t('TREE.EDUCATIONAL_LEVEL_UPDATE') : $t('TREE.EDUCATIONAL_LEVEL_NEW') }}</h4>

        <form @submit.prevent="createEducational_level" style="width: 100%">
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
                        id="name"
                        v-model="educational_level.name"
                        label="FORM.LABELS.NAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                educational_level.name = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="code"
                        v-model="educational_level.code"
                        label="FORM.LABELS.CODE"
                        :required="false"
                        @onChange="
                            (value) => {
                                educational_level.code = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <div v-if="educational_levelId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="educational_level.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
