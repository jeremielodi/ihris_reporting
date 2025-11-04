<script>
import { defineComponent } from 'vue';
import MyInputText from '@/components/InputText.vue';
import PyramidSelect from '@/components/pyramidSelect/pyramidSelect.vue';
import UserService from './user.service';
import NotifyService from '../../../../service/Notify.service';
import util from '../../../../service/UtilService';

export default defineComponent({
    name: 'UserCreate',
    data() {
        return {
            formSubmitted: false,
            userId: null,
            user: {
                username: null,
                email: null,
                firstname: null,
                lastname: null,
            }
        };
    },
    created() {
        const { id } = this.$route.query;
        if (id) {
            this.userId = id;
            UserService.read(id).then((user) => {
                setTimeout(() => {
                    this.user = user;
                    this.user.i2ce_hidden = !!user.i2ce_hidden;
                    this.user.facility_id = user.access_facility_id;
                    this.user.facility = {
                        id: user.access_facility_id,
                        name: user.access_facility_name
                    };
                }, 400);
            });
        }
    },
    components: {
        MyInputText,
        PyramidSelect,
    },
    methods: {
        reset() {
            this.user = {};
            this.formSubmitted = false;
            this.$router.back();
        },
        validate() {
            const options = {
                firstname: this.user.firstname,
                lastname: this.user.lastname,
                email: util.isEmail(this.user.email),
                username: this.user.username,
                facility_id: this.user.facility_id,
                password: this.user.password && (this.user.password.length >= 5 ? this.user.password : null),
            };

            if (!this.userId) {
                options.password = this.user.password;
            }

            let validKey = true;
            for (const key of Object.keys(options)) {
                if (!options[key]) {
                    validKey = false;
                    break;
                }
            }

            return validKey;
        },
        createUser() {
            this.formSubmitted = true;
            const isValid = this.validate();
            if (!isValid) {
                NotifyService.danger(this, '', 'FORM.ERRORS.INVALID');
                return;
            }
            const operation = this.userId ? UserService.update(this.userId, this.user) : UserService.create(this.user);
            operation
                .then((createUser) => {
                    NotifyService.success(this, '', null);
                    this.$router.push(`/manage/user_registry?id=${createUser.id}`);
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
        <h4>{{ userId ? $t('TREE.USER_UPDATE') : $t('TREE.USER_REGISTRATION') }}</h4>

        <form @submit.prevent="createUser" style="width: 100%">
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
                        id="firstname"
                        v-model="user.firstname"
                        label="FORM.LABELS.FIRSTNAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                user.firstname = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="lastname"
                        v-model="user.lastname"
                        label="FORM.LABELS.LASTNAME"
                        :required="true"
                        @onChange="
                            (value) => {
                                user.lastname = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
                    <MyInputText
                        id="email"
                        v-model="user.email"
                        type="email"
                        label="FORM.LABELS.EMAIL"
                        :required="true"
                        @onChange="
                            (value) => {
                                user.email = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />
    
                </div>
                <div class="col-12 lg:col-1 xl:col-1 p-field"></div>

                <div class="col-12 lg:col-5 xl:col-5 p-field">
                    <PyramidSelect
                        id="access"
                        :value="this.user.facility"
                        label="FORM.LABELS.ACCESS_LEVEL"
                        :required="true"
                        :getAllNodes="true"
                        :onChange="
                            (value) => {
                                if (!value || !value.key) return;
                                this.user.facility_id = value.key;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <MyInputText
                        id="username"
                        v-model="user.username"
                        label="FORM.LABELS.LOGIN"
                        :placeholder="$t('FORM.LABELS.EMAIL')"
                        type="email"
                        :required="true"
                        @onChange="
                            (value) => {
                                user.username = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <MyInputText
                        id="password"
                        v-model="user.password"
                        label="FORM.LABELS.PASSWORD"
                        type="password"
                        :min-val="5"
                        :required="!this.userId"
                        @onChange="
                            (value) => {
                                user.password = value;
                            }
                        "
                        :validationTrigger="formSubmitted"
                    />

                    <div v-if="userId" class="p-field-checkbox">
                        <Checkbox id="i2ce_hidden" :binary="true" name="locked" variant="filled" v-model="user.i2ce_hidden" />
                        <label for="i2ce_hidden"> {{ $t('FORM.LABELS.LOCKED') }}</label>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>
