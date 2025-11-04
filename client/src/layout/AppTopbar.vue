<script>
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useLayout } from '@/layout/composables/layout';
import SwitchLanguage from '../components/SwitchLanguage.vue';
import SettingService from '@/views/pages/manage/setting/setting.service';
import ChangePasswordModal from '@/views/pages/manage/user/change_pwd.vue';

export default {
    name: 'Topbar',
    components: { SwitchLanguage, ChangePasswordModal },
    props: {
        moduleName: { type: String, default: 'iHRIS Reporting' },
        topbar_button: { type: Boolean, default: true }
    },
    emits: ['language-changed'],

    data() {
        return {
            displayChangePwdModal: false,
            outsideClickListener: null,
            topbarMenuActive: false,
            username: null,
            appSetting: null,
            items: [
                {
                    label: 'Options',
                    items: [
                        {
                            label: this.$t('FORM.BUTTONS.UPDATE_PASSWORD'),
                            icon: 'pi pi-pencil',
                            command: () => {
                                this.displayChangePwdModal = true;
                            }
                        }
                    ]
                }
            ]
        };
    },

    computed: {
        server() {
            return import.meta.env.VITE_SERVER_URL;
        },
        topbarMenuClasses() {
            return { 'layout-topbar-menu-mobile-active': this.topbarMenuActive };
        }
    },

    created() {
        // hooks not available in Options API, so we grab composables here
        this.layout = useLayout();
        this.router = useRouter();
        this.i18n = useI18n();
    },

    mounted() {
        this.bindOutsideClickListener();
        this.username = localStorage.getItem('_ihris_username');
        SettingService.read(1).then((res) => {
            this.appSetting = res;
        });
    },

    beforeUnmount() {
        this.unbindOutsideClickListener();
    },

    methods: {
         onMenuToggle () {
        const { onMenuToggle } = useLayout();
          onMenuToggle();
         },
        closeChangePasswordModal() {
            this.displayChangePwdModal = false;
        },
        onTopBarMenuButton() {
            this.topbarMenuActive = !this.topbarMenuActive;
        },
        onSettingsClick() {
            this.topbarMenuActive = false;
            this.router.push('/documentation');
        },
        bindOutsideClickListener() {
            if (!this.outsideClickListener) {
                this.outsideClickListener = (event) => {
                    if (this.isOutsideClicked(event)) this.topbarMenuActive = false;
                };
                document.addEventListener('click', this.outsideClickListener);
            }
        },
        unbindOutsideClickListener() {
            if (this.outsideClickListener) {
                document.removeEventListener('click', this.outsideClickListener);
                this.outsideClickListener = null;
            }
        },
        isOutsideClicked(event) {
            if (!this.topbarMenuActive) return false;
            const sidebarEl = document.querySelector('.layout-topbar-menu');
            const topbarEl = document.querySelector('.layout-topbar-menu-button');
            if (!sidebarEl || !topbarEl) return false;
            return !(sidebarEl.contains(event.target) || topbarEl.contains(event.target));
        },
        goTo(url) {
            this.topbarMenuActive = !this.topbarMenuActive;
            setTimeout(() => window.open(url, '_blank'), 300);
        },
        onLanguageChange() {
            this.$emit('language-changed');
        },
        toggle(event) {
            this.$refs.menu.toggle(event);
        },
        logout() {
            this.topbarMenuActive = !this.topbarMenuActive;
            ['_ihris_token', '_ihris_username', '_access_facility_id', '_access_facility_name', '_access_facility_type', '_access_facility_target', '_access_facility_parents', 'validator'].forEach((k) => localStorage.removeItem(k));
            setTimeout(() => window.location.reload(), 600);
        }
    }
};
</script>

<template>
    <div class="layout-topbar">
        <router-link to="/" class="layout-topbar-logo" v-if="appSetting">
            <img :src="server + 'uploads/' + appSetting.logo" alt="logo" />
            <span class="font-normal">{{ appSetting.app_name }}</span>
        </router-link>
        <button v-if="topbar_button" class="p-link layout-menu-button layout-topbar-button" @click="onMenuToggle()">
            <i class="pi pi-bars"></i>
        </button>
        <button class="p-link layout-topbar-menu-button layout-topbar-button" @click="onTopBarMenuButton()">
            <i class="pi pi-ellipsis-v"></i>
        </button>
        <div class="layout-topbar-menu" :class="topbarMenuClasses">
            <div>
                <SwitchLanguage class="p-link layout-topbar-button" @language-changed="onLanguageChange()" />
            </div>

            <div>
                <Button class="p-button-text p-button-secondary p-button-rounded float-right" :label="username" icon="pi pi-user" @click="toggle" />
                <Menu ref="menu" id="overlay_menu" :model="items" :popup="true" />
            </div>
            <button @click="logout()" class="p-link layout-topbar-button" title="déconnexion">
                <i class="pi pi-sign-out"></i>
                <span>déconnexion</span>
            </button>
        </div>

        <ChangePasswordModal :close="closeChangePasswordModal" :display="displayChangePwdModal"></ChangePasswordModal>
    </div>
</template>

<style lang="scss" scoped></style>
