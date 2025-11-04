<script>
import AppCache from '../service/appCache';

export default {
    name: 'SwitchLocale',
    props: {
        dottes: {
            Type: Boolean,
            Default: false
        }
    },
    data() {
        return {
            items: []
        };
    },

    methods: {
        toggle(event) {
            this.$refs.menu.toggle(event);
            this.setItems();
        },

        setItems() {
            this.items = ['en', 'fr'].map((lg) => {
                let session = AppCache.getSession() || {};
                const langs = { fr: 'Français', en: 'English' };
                return {
                    label: langs[lg],
                    icon: session.lg === lg ? 'pi pi-check' : '',
                    command: () => {
                        session.lg = lg;
                        localStorage.setItem('lg', lg);
                        this.$i18n.locale = lg;
                        this.$emit('language-changed');
                        // this.$router.go();
                    }
                };
            });
        }
    }
};
</script>

<template>
    <div style="text-align: right">
        <i :class="dottes ? 'link pi pi-ellipsis-v' : 'link pi pi-globe'" style="fontsize: 1.5rem" label="Toggle" @click="toggle"></i>
        <Menu ref="menu" :model="items" :popup="true" />
    </div>
</template>

<style>
select {
    width: 150px;
    line-height: 49px;
    height: 38px;
    font-size: 22px;
    outline: 0;
    margin-bottom: 15px;
}
.link {
    cursor: pointer;
}
</style>
