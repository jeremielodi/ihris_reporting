<script>
import DashboardManageService from '../../manage/metabase_dashboard/dashboard.service';

export default {
    name: 'DashboardSelector',
    data() {
        return {
            loading: false,
            dashboards: [],
            selectedDashboard: null
        };
    },
    async mounted() {
        await this.loadDashboards();
    },
    methods: {
        async loadDashboards() {
            this.loading = true;
            try {
                // Replace with your actual API call
                const response = await DashboardManageService.assigned();
                this.dashboards = response.map((dashboard) => ({
                    ...dashboard,
                    isNew: this.isNewDashboard(dashboard.createdAt)
                }));
                if (this.dashboards.length == 1) {
                    this.selectDashboard(this.dashboards[0]);
                }
            } catch (error) {
                console.error('Failed to load dashboards:', error);
                // Fallback mock data
            } finally {
                this.loading = false;
            }
        },

        getMockDashboards() {
            return [];
        },

        async selectDashboard(dashboard) {
            this.selectedDashboard = dashboard;
            await this.$nextTick();
            this.openDashboard();
        },

        openDashboard() {
            if (this.selectedDashboard) {
                // Navigate using query parameters
                this.$router.push({
                    name: 'metabase_dashboard',
                    query: { id: this.selectedDashboard.mb_dashboard_id }
                });
            }
        },
        isNewDashboard(createdAt) {
            const created = new Date(createdAt);
            const now = new Date();
            const diffTime = Math.abs(now - created);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            return diffDays <= 7; // New if created within last 7 days
        },

        formatDate(dateString) {
            if (!dateString) return 'Never';
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            });
        }
    }
};
</script>

<template>
    <div class="dashboard-container">
        <!-- Header -->
        <div class="dashboard-header" v-if="dashboards.length > 0">
            <h1 class="dashboard-title">{{ $t('FORM.LABELS.MY_DASHBOARDS') }} </h1>
            <p class="dashboard-subtitle">{{ $t('FORM.LABELS.SELECT_DASHBOARDS') }}</p>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>Loading dashboards...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="dashboards.length === 0" class="empty-state">
            <div class="empty-icon">📊</div>
            <h3>{{$t('FORM.LABELS.NO_DASHBOARD_AVAILABLE')}}</h3>
            <p>{{$t('FORM.LABELS.CONTACT_ADMIN_DASHBOARD')}}</p>
        </div>

        <!-- Dashboard Grid -->
        <div v-else class="dashboard-grid">
            <div v-for="dashboard in dashboards" :key="dashboard.mb_dashboard_id" class="dashboard-card" :class="{ 'dashboard-card-active': selectedDashboard?.mb_dashboard_id === dashboard.mb_dashboard_id }" @click="selectDashboard(dashboard)">
                <div class="dashboard-card-header">
                    <div class="dashboard-icon">📈</div>
                    <div class="dashboard-badge" v-if="dashboard.isNew">New</div>
                </div>

                <div class="dashboard-card-content">
                    <h3 class="dashboard-label">{{ dashboard.label }}</h3>
                    <p class="dashboard-description" v-if="dashboard.description">
                        {{ dashboard.description }}
                    </p>
                    <p class="dashboard-meta" v-else>No description available</p>
                </div>

                <div class="dashboard-card-footer">
                    <div class="dashboard-stats">
                        <span class="stat">
                            <i class="stat-icon">👁️</i>
                            {{ dashboard.viewCount || 0 }}
                        </span>
                        <span class="stat">
                            <i class="stat-icon">📅</i>
                            {{ formatDate(dashboard.updatedAt) }}
                        </span>
                    </div>
                    <div class="dashboard-arrow">
                        <i class="arrow-icon">→</i>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.dashboard-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Header */
.dashboard-header {
    text-align: center;
    margin-bottom: 3rem;
}

.dashboard-title {
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
}

.dashboard-subtitle {
    font-size: 1.1rem;
    color: #6b7280;
    margin: 0;
}

/* Loading State */
.loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem;
    color: #6b7280;
}

.loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #e5e7eb;
    border-top: 4px solid #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

/* Empty State */
.empty-state {
    text-align: center;
    padding: 4rem;
    color: #6b7280;
}

.empty-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
}

.empty-state h3 {
    color: #374151;
    margin-bottom: 0.5rem;
}

/* Dashboard Grid */
.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

/* Dashboard Card */
.dashboard-card {
    background: white;
    border: 2px solid #f3f4f6;
    border-radius: 16px;
    padding: 1.5rem;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.dashboard-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    transform: scaleX(0);
    transition: transform 0.3s ease;
}

.dashboard-card:hover {
    transform: translateY(-4px);
    border-color: #667eea;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.dashboard-card:hover::before {
    transform: scaleX(1);
}

.dashboard-card-active {
    border-color: #667eea;
    background: linear-gradient(135deg, #f8faff 0%, #f0f4ff 100%);
}

.dashboard-card-active::before {
    transform: scaleX(1);
}

/* Card Header */
.dashboard-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.dashboard-icon {
    font-size: 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
}

.dashboard-badge {
    background: #10b981;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}

/* Card Content */
.dashboard-card-content {
    margin-bottom: 1.5rem;
}

.dashboard-label {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1f2937;
    margin: 0 0 0.5rem 0;
    line-height: 1.4;
}

.dashboard-description {
    color: #6b7280;
    font-size: 0.9rem;
    line-height: 1.5;
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.dashboard-meta {
    color: #9ca3af;
    font-size: 0.85rem;
    font-style: italic;
    margin: 0;
}

/* Card Footer */
.dashboard-card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.dashboard-stats {
    display: flex;
    gap: 1rem;
}

.stat {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.8rem;
    color: #6b7280;
}

.stat-icon {
    font-size: 0.9rem;
}

.dashboard-arrow {
    color: #667eea;
    font-weight: bold;
    transition: transform 0.3s ease;
}

.dashboard-card:hover .dashboard-arrow {
    transform: translateX(4px);
}

/* Selected Preview */
.selected-preview {
    background: white;
    border: 2px solid #667eea;
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 2rem;
}

.preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.preview-header h3 {
    margin: 0;
    color: #1f2937;
}

.open-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.open-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

/* Responsive Design */
@media (max-width: 768px) {
    .dashboard-container {
        padding: 1rem;
    }

    .dashboard-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
    }

    .dashboard-title {
        font-size: 2rem;
    }

    .preview-header {
        flex-direction: column;
        gap: 1rem;
        align-items: flex-start;
    }

    .open-btn {
        width: 100%;
    }
}

@media (max-width: 480px) {
    .dashboard-card {
        padding: 1rem;
    }

    .dashboard-stats {
        flex-direction: column;
        gap: 0.5rem;
    }
}
</style>
