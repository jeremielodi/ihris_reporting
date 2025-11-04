<script>
import DashboardSelector from './dashbard_selector.vue';

export default {
    components: {
        DashboardSelector
    },
    methods: {
        handleDashboardSelect(dashboard) {
            console.log('Dashboard selected:', dashboard);
            // Handle selection logic
        },
        handleOpenDashboard(dashboard) {
            // Navigate to dashboard or open in modal
            this.$router.push(`/dashboard/${dashboard.id}`);
        }
    }
};
</script>

<template>
    <div>
        <DashboardSelector @dashboard-selected="handleDashboardSelect" @open-dashboard="handleOpenDashboard" />
    </div>
</template>
