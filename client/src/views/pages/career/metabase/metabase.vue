<script>
import { defineComponent, nextTick } from 'vue';
import VegaChart from '@/components/ReportView.vue';
import PyarmidPath from '../PyarmidPath.vue';
import MetabaseService from './metabase.service';
import DashboardManageService from '../../manage/metabase_dashboard/dashboard.service';

export default defineComponent({
    name: 'metabase',
    components: { VegaChart, PyarmidPath },

    data() {
        return {
            cardList: [],
            dashbordName: '',
            wrapperKey: 'ke1',
            loadingDashboard: false,
            orgUnitId: null,
            chartRefs: [], // Track chart refs
            dashboardData: null,
            gridBounds: null
        };
    },

    expose: ['updateReport', 'forceReload'],

    watch: {
        '$store.state.blockReportPreview': function (newVal) {
            if (!newVal) {
                this.updateReport(this.$store.state.currentNode);
            }
        }
    },

    computed: {
        /**
         * Get sorted and positioned cards for grid layout
         */
        positionedCards() {
            if (!this.dashboardData?.dashcards) return [];

            const cards = this.sortDashcardsByPosition(this.dashboardData.dashcards.filter((c) => c?.card?.type === 'question'));

            return cards.map((item) => ({
                key: `chart_${item.card.id}_${item.id}`,
                id: item.card.id,
                name: item.card.name,
                mark: this.chartType(item.card.display),
                display: item.card.display === 'table' ? 'table' : 'chart',
                // Position properties
                col: item.col,
                row: item.row,
                size_x: item.size_x,
                size_y: item.size_y,
                // Adjusted position for grid (removes empty top space)
                adjustedRow: this.getAdjustedRow(item.row),
                // Style properties for grid
                gridStyle: this.getCardGridStyle(item)
            }));
        },

        /**
         * Calculate grid container style with proper responsive behavior
         */
        gridContainerStyle() {
            return {
                // Use responsive grid columns
                gridTemplateColumns: 'repeat(24, 1fr)',
                // Auto rows for true responsiveness
                gridAutoRows: 'minmax(auto, max-content)',
                // Ensure grid fits container
                width: '100%',
                minWidth: '100%',
                maxWidth: '100%'
            };
        },

        /**
         * Get the minimum row to calculate proper offset
         */
        minRow() {
            return this.gridBounds?.minRow || 0;
        }
    },
    mounted() {
        this.loadData();
    },
    methods: {
        forceReload() {
            this.$route.meta.shouldRefresh = true;
        },

        updateReport(code) {
            this.cardList = [];
            this.orgUnitId = code;
            this.loadData();
        },

        chartType(v) {
           
            const key = String(v || '')
                .toLowerCase()
                .replace(/[\s_-]+/g, ''); // normalize: "single_value" -> "singlevalue"

            const map = {
                // Core
                bar: 'bar',
                column: 'bar',
                row: 'bar',
                barstacked: 'bar',

                line: 'line',
                area: 'area',

                scatter: 'scatter',
                bubble: 'scatter', // fallback to scatter

                pie: 'pie',
                donut: 'donut',
                doughnut: 'donut',

                heatmap: 'heatmap',
                treemap: 'treemap',

                // Extras to mimic Metabase
                funnel: 'funnel',

                gauge: 'gauge',
                radialbar: 'gauge',
                radial: 'gauge',

                number: 'number',
                scalar: 'number',
                singlevalue: 'number',
                metric: 'number',
                kpi: 'number',

                progress: 'progress',
                goal: 'progress',
                target: 'progress',

                // Optional/legacy
                radar: 'radar',
                polararea: 'pie', // treat as rose/pie variant
            };
            return map[key] || 'bar';
        },

        /**
         * Sort dashcards by position (row then column)
         */
        sortDashcardsByPosition(dashcards) {
            return [...dashcards].sort((a, b) => {
                // First sort by row
                if (a.row !== b.row) {
                    return a.row - b.row;
                }
                // If same row, sort by column
                return a.col - b.col;
            });
        },

        /**
         * Adjust row position to remove empty top space
         */
        getAdjustedRow(originalRow) {
            return originalRow - this.minRow;
        },

        /**
         * Get grid style for a card based on its position and size
         * Ensures cards don't exceed container width
         */
        getCardGridStyle(dashcard) {
            const adjustedRow = this.getAdjustedRow(dashcard.row);

            // Ensure card doesn't exceed grid boundaries
            const effectiveSizeX = Math.min(dashcard.size_x, 24 - dashcard.col);

            return {
                gridColumnStart: dashcard.col + 1,
                gridRowStart: adjustedRow + 1, // +1 because CSS grid is 1-based
                gridColumnEnd: `span ${effectiveSizeX}`,
                gridRowEnd: `span ${dashcard.size_y}`,
                // Ensure card fits within container
                width: '100%',
                minWidth: '0', // Important for grid item shrinking
                maxWidth: '100%'
            };
        },

        /**
         * Calculate dashboard bounds for grid layout
         */
        calculateGridBounds(dashcards) {
            if (!dashcards.length) return null;

            const bounds = {
                minRow: Infinity,
                maxRow: -Infinity,
                minCol: Infinity,
                maxCol: -Infinity
            };

            dashcards.forEach((dashcard) => {
                bounds.minRow = Math.min(bounds.minRow, dashcard.row);
                bounds.maxRow = Math.max(bounds.maxRow, dashcard.row + dashcard.size_y);
                bounds.minCol = Math.min(bounds.minCol, dashcard.col);
                bounds.maxCol = Math.max(bounds.maxCol, dashcard.col + dashcard.size_x);
            });

            return bounds;
        },

        async loadData() {
            try {
                if (this.loadingDashboard) return;
                this.loadingDashboard = true;
                const { id } = this.$route.query;
                if (!id) {
                    window.location.href = '/#/auth/login';
                    return;
                }
                const response = await DashboardManageService.assigned();
                const idAssigned = response.filter((r) => r.mb_dashboard_id == id).length;
                if (!idAssigned) {
                    window.location.href = '/#/auth/login';
                    return;
                }
                const result = await MetabaseService.getDashboadDetails(id);
                this.dashboardData = result;
                this.dashbordName = result?.name || '';

                // Calculate grid bounds for layout
                if (result?.dashcards) {
                    const questionCards = result.dashcards.filter((c) => c?.card?.type === 'question');
                    this.gridBounds = this.calculateGridBounds(questionCards);
                }

                // Wait for next tick to ensure components are rendered
                await nextTick();
                this.refreshAllCharts();
            } catch (e) {
                console.error('loadData failed:', e);
            }
            this.loadingDashboard = false;
        },

        // Method to refresh all chart components
        refreshAllCharts() {
            if (this.$refs.charts) {
                this.$refs.charts.forEach((chart) => {
                    if (chart && chart.refresh) {
                        chart.refresh();
                    }
                });
            }
        }
    }
});
</script>

<template>
    <div class="metabase-dashboard">
        <PyarmidPath :reload="loadData"/>
        <!-- Dashboard Header -->
        <div class="dashboard-header">
            <span class="dashboard-title">{{ dashbordName }}</span>
        </div>

        <!-- Loading State -->
        <template v-if="loadingDashboard">
            <div class="loading-skeletons">
                <div v-for="i in [1, 2, 3, 4, 5, 6, 7, 8, 9]" :key="i" class="card-skeleton">
                    <div class="skeleton-content">
                        <div class="skeleton-chart"></div>
                    </div>
                </div>
            </div>
        </template>

        <!-- Empty State -->
        <div v-else-if="positionedCards.length === 0 && !loadingDashboard" class="empty-dashboard">
            <div class="empty-state">
                <div class="empty-icon" @click="loadData()" style="color: blue;">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="currentcolor" viewBox="0 0 16 16" class="play-icon"
                        role="img" aria-label="play icon">
                        <path
                            d="M3.624 3.351a.75.75 0 0 1 .748-.002l7 4a.75.75 0 0 1 0 1.302l-7 4A.75.75 0 0 1 3.25 12V4a.75.75 0 0 1 .374-.649z">
                        </path>
                    </svg>
                </div>
                <h3>No Dashboard Loaded</h3>
                <p>Click the play button to load the Metabase dashboard</p>
            </div>
        </div>

        <!-- Dashboard Grid -->
        <div v-else class="dashboard-grid" :style="gridContainerStyle">
            <div v-for="card in positionedCards" :key="card.key" class="grid-card" :style="card.gridStyle">
                <VegaChart :ref="`chart_${card.id}`" :orgUnitId="$store.state.currentNode" :map-id="card.id"
                    :display="card.display" theme="light" :mark="card.mark" :horizontal="false" :show-legend="true"
                    legend-pos="top" />
            </div>
        </div>
    </div>
</template>

<style lang="css" scoped>
@import './style.css';

</style>
