<script setup>
import * as echarts from 'echarts';
import { onMounted, onBeforeUnmount, watch, ref, nextTick } from 'vue';

const props = defineProps({
    title: { type: String, default: '' },
    categories: { type: Array, default: () => [] },
    required: { type: Array, default: () => [] },
    actual: { type: Array, default: () => [] },
    missing: { type: Array, default: () => [] },
    excess: { type: Array, default: () => [] }
});

const el = ref(null);
const isFullscreen = ref(false);
let chart = null;

const render = () => {
    if (!chart) return;

    chart.setOption(
        {
            tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
            legend: { top: 40 },
            grid: {
                left: 40,
                right: 30,
                top: 90,
                bottom: 90
            },
            xAxis: {
                type: 'category',
                data: props.categories,
                axisLabel: {
                    rotate: 30,
                    interval: 0
                }
            },
            yAxis: { type: 'value' },
            series: [
                { name: 'Required', type: 'bar', data: props.required },
                { name: 'Actif', type: 'bar', data: props.actual },
                { name: 'Carence', type: 'bar', itemStyle: { color: '#dc2626' }, data: props.missing },
                { name: 'Pletore', type: 'bar', itemStyle: { color: '#f59e0b' }, data: props.excess }
            ]
        },
        true
    );
};

const toggleFullscreen = async () => {
    isFullscreen.value = !isFullscreen.value;
    await nextTick();
    chart?.resize();
};

onMounted(() => {
    chart = echarts.init(el.value);
    render();
    window.addEventListener('resize', () => chart?.resize());
});

onBeforeUnmount(() => {
    window.removeEventListener('resize', () => chart?.resize());
    chart?.dispose();
    chart = null;
});

watch(
    () => [props.categories, props.required, props.actual, props.missing, props.excess],
    () => render(),
    { deep: true }
);
</script>

<template>
    <div :class="['chart-wrapper', { fullscreen: isFullscreen }]">
        <!-- Toolbar -->
        <div class="chart-toolbar">
            <span class="chart-title">{{ title }}</span>

            <button class="chart-btn" @click="toggleFullscreen">
                {{ isFullscreen ? '✖ Quitter' : '⛶ Plein écran' }}
            </button>
        </div>

        <!-- Chart -->
        <div ref="el" class="chart-container"></div>
    </div>
</template>

<style scoped>
/* Wrapper */
.chart-wrapper {
    position: relative;
    background: #ffffff;
    border-radius: 8px;
    padding: 8px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

/* Toolbar */
.chart-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 8px;
}

.chart-title {
    font-weight: 600;
    color: #1f2937;
}

.chart-btn {
    background: #2563eb;
    color: #fff;
    border: none;
    padding: 4px 10px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
}

.chart-btn:hover {
    background: #1d4ed8;
}

/* Chart container */
.chart-container {
    width: 100%;
    height: 360px;
}

/* FULLSCREEN MODE */
.chart-wrapper.fullscreen {
    position: fixed;
    inset: 0;
    z-index: 9999;
    border-radius: 0;
    padding: 12px;
    background: #ffffff;
}

.chart-wrapper.fullscreen .chart-container {
    height: calc(100vh - 60px);
}

.chart-wrapper.fullscreen .chart-toolbar {
    border-bottom: 1px solid #e5e7eb;
}
</style>
