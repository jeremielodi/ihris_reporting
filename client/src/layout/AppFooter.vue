<script setup>
import { computed, ref, onMounted } from 'vue';
import { useLayout } from '@/layout/composables/layout';
import SettingService from '@/views/pages/manage/setting/setting.service';

const { layoutConfig } = useLayout();
const appSetting = ref(null);

const server = computed(() => {
    return import.meta.env.VITE_SERVER_URL;
});

onMounted(() => {
    SettingService.read(1).then((res) => {
       appSetting.value = res;
    })
});


</script>

<template>
    <div class="layout-footer"  v-if="appSetting">
        <img  :src="server + 'uploads/'+appSetting.logo"  alt="Logo" height="80" style="padding-right: 10px; border-right: 4px solid #ccc" class="mr-2" />

        <div>
            <span class="font-medium ml-2">
                {{ appSetting.responsible_name }}</span>
            <br>
            <span>{{ appSetting.responsible_number}}</span>
        </div>
    </div>
</template>
<style lang="scss" scoped></style>
