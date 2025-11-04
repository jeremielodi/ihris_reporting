<script>
import DashboardLayout from './dashboadLayout.vue';
import MetabaseService from './metabase.service';

export default {
  data() {
    return {
      metabaseDashboardData: {} // Your actual API response here
    };
  },
  components : {DashboardLayout},
  methods: {
    handleCardSelect(card) {
      console.log('Selected card:', card);
      // Handle card selection
    },
    async loadData() {
        this.metabaseDashboardData = await MetabaseService.getDashboadDetails(2);
    }
  },
  async mounted() {
    this.loadData();
  }
};
</script>

<template>
  <DashboardLayout 
    :dashboard-id="2"
    :dashboard-name="'Tableau de bord 1'"
    :dashboard-data="metabaseDashboardData"
    @card-selected="handleCardSelect"
  />
</template>