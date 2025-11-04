<script>
import { defineComponent } from 'vue';
import ConfirmModal from '@/components/ConfirmModal.vue';

export default defineComponent({
    name: 'Education_majourAction',
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
    emits: ['reloadEducation_majourList'],
    setup() {},
    methods: {
        toggle(event) {
            this.$refs.menu.toggle(event);
            this.setItems();
        },

        closeDialog(result) {
            if (result) {
                this.$emit('reloadEducation_majourList', true);
            }
            this.display = false;
            this.displayConfirm = false;
        },
        HideModal() {
            this.display = false;
            this.displayConfirm = false;
        },

        DeleteConfirmDialog(result) {
            if (!result) {
                this.HideModal();
                return;
            }
        },

        setItems() {
            this.items = [
                {
                    label: this.entity.name,
                    items: [
                        {
                            label: this.$t('FORM.BUTTONS.EDIT'),
                            icon: 'pi pi-fw pi-pencil',
                            command: () => {
                                this.$router.push(`/manage/educational_major_create?id=${this.entity.id}`);
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
        <ConfirmModal :education_majour="entity" :close="DeleteConfirmDialog" :display="displayConfirm"> </ConfirmModal>
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
