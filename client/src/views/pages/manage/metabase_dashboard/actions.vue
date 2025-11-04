<script>
import { defineComponent } from 'vue';
import NotifyService from '@/service/Notify.service';
import ConfirmModal from '@/components/ConfirmModal.vue';

export default defineComponent({
    name: 'RegionAction',
    props: {
        entity: Object,
        actionId: String
    },
    data() {
        return {
            items: [],
            display: false,
            displayConfirm: false,
        };
    },
    emits: ['reloadRegionList'],
    setup() {},
    methods: {
        toggle(event) {
            this.$refs.menu.toggle(event);
            this.setItems();
        },

        closeDialog(result) {
            if (result) {
                this.$emit('reloadRegionList', true);
            }
            this.display = false;
            this.displayConfirm = false;
        },
        HideModal() {
            this.display = false;
            this.displayConfirm = false;
        },
        setItems() {
            this.items = [
                {
                    label: this.entity.label,
                    items: [
                        {
                            label: this.$t('FORM.BUTTONS.EDIT'),
                            icon: 'pi pi-fw pi-pencil',
                            command: () => {
                                this.$router.push(`/manage/dashboard_create?uuid=${this.entity.uuid}`);
                            }
                        }
                    ]
                }
            ];
        }
    },
    components: {
        ConfirmModal
    }
});
</script>

<template>
    <div style="text-align: right" :data-testid="actionId" :id="actionId">
        <div @click="toggle" class="link">
            <span style="font-size: 14px">Actions</span>
            <i class="link pi pi-chevron-down" style="fontsize: 1rem"> </i>
        </div>
        <Menu ref="menu" :model="items" :popup="true" />
        <ConfirmModal :region="entity" :close="DeleteConfirmDialog" :display="displayConfirm"> </ConfirmModal>
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
