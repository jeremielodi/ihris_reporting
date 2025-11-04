<!-- ApexChart.vue — Single File Component (Options API) using vue-echarts -->
<template>
  <div
    :id="wrapperID"
    :class="['chart-wrapper', theme, { resizable, fullscreen: fullPageLocal }]"
    :style="wrapperStyle"
    ref="wrap"
  >
    <div style="padding: 2px; font-size: 16px; font-weight: 400;">{{ localTitle }}</div>

    <Panel style="width: 100%;" class="styled-panel">
      <!-- HEADER -->
      <template #header>
        <div ref="toolbar" class="controls">
          <label v-if="display !== 'table'">
            <i class="pi pi-chart-bar" style="font-size: 1.5rem" @click="setDisplay('chart')"></i>
            &nbsp;
            <i class="pi pi-table" style="font-size: 1.5rem" @click="setDisplay('table')"></i>
          </label>

          <label v-if="display !== 'table'">
            <Dropdown
              title="Type"
              v-model="markLocal"
              appendTo="body"
              @change="nudgeWrapperWidth()"
              :options="chartTypes"
              optionLabel="label"
              optionValue="value"
              class="w-48"
            >
              <template #option="slotProps">
                <div class="flex items-center gap-2">
                  <i :class="slotProps.option.icon"></i>
                  <span>{{ slotProps.option.label }}</span>
                </div>
              </template>
              <template #value="slotProps">
                <div v-if="slotProps.value" class="flex items-center gap-2">
                  <i :class="chartTypes.find(ct => ct.value === slotProps.value)?.icon"></i>
                  <span>{{ chartTypes.find(ct => ct.value === slotProps.value)?.label }}</span>
                </div>
                <span v-else>Select type</span>
              </template>
            </Dropdown>
          </label>

          <label v-if="display !== 'table'">
            Horizontal&nbsp;
            <input type="checkbox" v-model="horizontalLocal" :disabled="markLocal !== 'bar'" />
          </label>

          <label v-if="display !== 'table'">
            Labels&nbsp;
            <input
              type="checkbox"
              v-model="showLabelsLocal"
              :disabled="['pie','donut','radialBar','heatmap','treemap','polarArea','gauge','number','progress','funnel'].includes(markLocal)"
            />
          </label>

          <label v-if="display !== 'table'">
            Legend&nbsp;
            <input
              type="checkbox"
              v-model="showLegendLocal"
              @change="() => { $nextTick(() => reflow()); setLegend(showLegendLocal); }"
              :disabled="displayLocal === 'table'"
            />
          </label>

          <div class="controls-actions">
            <Button
              type="button"
              severity="secondary"
              title="Refresh"
              icon="pi pi-refresh"
              :class="{ 'pi-spin': loading }"
              :loading="loading"
              :disabled="loading"
              @click="refreshChart"
            />
            <Button
              severity="secondary"
              :icon="!fullPageLocal ? 'pi pi-arrows-h' : 'pi pi-arrow-down-left-and-arrow-up-right-to-center'"
              v-tooltip="fullPageLocal ? 'Exit Full page' : 'Full page'"
              class="fullscreen-btn"
              @click="toggleFullPage"
            />
          </div>
        </div>
      </template>

      <!-- RIGHT HEADER ICONS -->
      <template #icons>
        <Button type="button" severity="secondary" icon="pi pi-download" @click="toggleDownLoadMenu" aria-haspopup="true" aria-controls="overlay_menu" />
        <Menu ref="downloadMenu" id="overlay_menu" :model="downloadOptions" :popup="true" />
      </template>

      <!-- LOADING OVERLAY -->
      <div v-if="loading" class="loading-overlay">
        <div class="spinner"></div>
        <div class="loading-text">Loading…</div>
      </div>

      <!-- CHART -->
      <div v-if="displayLocal !== 'table'" class="chart-area" ref="chartArea">
        <!-- was: v-if="hasChartData || markLocal === 'number' || markLocal === 'progress'" -->
        <VChart
          v-if="hasChartData || markLocal === 'number' || markLocal === 'progress' || markLocal === 'gauge'"
          ref="echartRef"
          :key="chartKey"
          :option="chartOption"
          autoresize
          class="echart-host"
          :style="{ height: (apexHeight + 80)+ 'px', width: '100%' }"
        />

        <p v-else class="muted">No chartable data</p>
      </div>

      <!-- TABLE -->
      <div v-if="displayLocal !== 'chart'" class="table-area">
        <h3 v-if="chartTitle" class="table-title">{{ chartTitle }}</h3>

        <div class="table-toolbar">
          <input v-model="tableSearch" type="search" class="table-search" placeholder="Search…" />
          <span class="rows-count">{{ filteredRows.length }} rows</span>
        </div>

        <div class="table-scroll">
          <table class="datatable">
            <thead>
              <tr>
                <th
                  v-for="c in tableCols"
                  :key="c"
                  @click="sortBy(c)"
                  :class="{ sortable: true, active: sortKey === c }"
                >
                  {{ c }}
                  <span v-if="sortKey === c" class="sort-indicator">{{ sortDir === 'asc' ? '▲' : '▼' }}</span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(r, i) in pagedRows" :key="i">
                <td v-for="c in tableCols" :key="c">{{ formatCell(r[c]) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="pager">
          <button @click="prevPage" :disabled="page === 1">Prev</button>
          <span>Page {{ page }} / {{ totalPages }}</span>
          <button @click="nextPage" :disabled="page === totalPages">Next</button>
          <label class="page-size">
            per page
            <select v-model.number="pageSize">
              <option :value="10">10</option>
              <option :value="25">25</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
          </label>
        </div>
      </div>

      <p v-if="error" class="text-red-500 text-xs mt-2">{{ error }}</p>
    </Panel>
  </div>
</template>

<script lang="ts">
import { defineComponent, nextTick, PropType } from "vue";

/* PrimeVue */
import Panel from "primevue/panel";
import Button from "primevue/button";
import Dropdown from "primevue/dropdown";
import Menu from "primevue/menu";

/* vue-echarts + tree-shakable ECharts core */
import { use } from "echarts/core";
import VChart from "vue-echarts";

/* ECharts: charts */
import {
  BarChart, LineChart, ScatterChart, PieChart,
  HeatmapChart, TreemapChart, RadarChart, GaugeChart, FunnelChart
} from "echarts/charts";

/* ECharts: components (Grid provides cartesian2d) */
import {
  GridComponent, TooltipComponent, LegendComponent, TitleComponent,
  VisualMapComponent, DatasetComponent, RadarComponent
} from "echarts/components";

/* ECharts: renderer */
import { CanvasRenderer } from "echarts/renderers";

/* Register everything we use (fixes 'cartesian2d cannot be found …') */
use([
  BarChart, LineChart, ScatterChart, PieChart,
  HeatmapChart, TreemapChart, RadarChart, GaugeChart, FunnelChart,
  GridComponent, RadarComponent, TooltipComponent, LegendComponent, TitleComponent,
  VisualMapComponent, DatasetComponent, CanvasRenderer
]);

/* Services (same as your original) */
import axios from "axios";
import _AppCache from "../service/appCache";
import MetabaseService from "@/views/pages/career/metabase/metabase.service";
import OrgUnitService from "../views/pages/manage/organization_units/orgUnit.service";

type MarkType =
  | "bar" | "line" | "area" | "scatter"
  | "pie" | "donut"
  | "gauge" | "radialBar"
  | "heatmap" | "funnel"
  | "number" | "progress"
  | "treemap" | "radar" | "polarArea"; // kept for backward compat

type DisplayMode = "chart" | "table" | "both";

export default defineComponent({
  name: "ApexChart",
  components: { Panel, Button, Dropdown, Menu, VChart },

  props: {
    orgUnitId: { type: String, default: "" },
    dataset: { type: Array as PropType<Array<Record<string, any>>>, default: () => [] },
    mapId: { type: String, default: "" },
    apiHeaders: { type: Object as PropType<Record<string, string>>, default: () => ({}) },
    apiAutoLoad: { type: Boolean, default: true },
    reload: { type: Number },

    x: { type: String, default: "" },
    y: { type: String, default: "" },
    valueFields: { type: Array as PropType<string[]>, default: () => [] },
    seriesFieldName: { type: String, default: "series" },
    valueFieldName: { type: String, default: "value" },

    mark: { type: String as PropType<MarkType>, default: "bar" },
    stack: { type: String as PropType<"zero" | "normalize" | "center" | null>, default: null },
    horizontal: { type: Boolean, default: false },
    showLabels: { type: Boolean, default: true },
    labelFormat: { type: String as PropType<string | null>, default: null },

    width: { type: Number as PropType<number | null>, default: null },
    height: { type: Number as PropType<number | null>, default: 420 },
    padding: { type: Number, default: 8 },
    resizable: { type: Boolean, default: true },
    controls: { type: Boolean, default: true },

    colorField: { type: String as PropType<string | null>, default: null },
    color: { type: String as PropType<string | null>, default: null },
    colorRange: { type: Array as PropType<string[]>, default: () => [] },
    colorMap: { type: Object as PropType<Record<string, string>>, default: () => ({}) },
    showLegend: { type: Boolean, default: true },
    legendPos: { type: String, default: "right" },

    xLabelAngle: { type: Number, default: 45 },
    yLabelAngle: { type: Number, default: 0 },
    yLabelMaxWidth: { type: Number, default: 420 },
    dataLabelsOffsetY: { type: Number, default: -8 },

    theme: { type: String as PropType<"light" | "dark">, default: "light" },
    display: { type: String as PropType<DisplayMode>, default: "chart" },
    autoInfer: { type: Boolean, default: true },

    tablePageSize: { type: Number, default: 10 },
    fullPage: { type: Boolean, default: false },
  },

  activated() {
    this.renderKey = `renderKey${Math.random()}`;
  },

  data() {
    return {
      queryParameter: {} as any,
      wrapperID: `chart${Math.random()}`,
      renderKey: `renderKey${Math.random()}`,
      downloadOptions: [] as any[],
      localTitle: "" as string,

      /* Metabase-like chart list */
      chartTypes: [
        { label: 'Bar',      value: 'bar',      icon: 'pi pi-chart-bar' },
        { label: 'Line',     value: 'line',     icon: 'pi pi-chart-line' },
        { label: 'Area',     value: 'area',     icon: 'pi pi-chart-area' },
        { label: 'Scatter',  value: 'scatter',  icon: 'pi pi-circle-fill' },
        { label: 'Pie',      value: 'pie',      icon: 'pi pi-chart-pie' },
        { label: 'Donut',    value: 'donut',    icon: 'pi pi-chart-pie' },
        { label: 'Funnel',   value: 'funnel',   icon: 'pi pi-filter' },
        { label: 'Gauge',    value: 'gauge',    icon: 'pi pi-compass' },
        { label: 'Heatmap',  value: 'heatmap',  icon: 'pi pi-th-large' },
        { label: 'Number',   value: 'number',   icon: 'pi pi-hashtag' },
        { label: 'Progress', value: 'progress', icon: 'pi pi-percentage' },
      ],

      defaultColors: [
        "#4E79A7","#F28E2B","#E15759","#76B7B2","#59A14F","#EDC948","#B07AA1","#FF9DA7","#9C755F","#BAB0AC",
        "#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf",
        "#2E86AB","#F6C85F","#6F4E7C","#9FD356","#CA472F","#FFA056","#36A2EB","#9966FF","#8DD3C7","#80B1D3",
        "#FB8072","#FDB462","#B3DE69","#FCCDE5","#BC80BD","#CCEBC5","#FFED6F","#A6CEE3","#1B9E77","#D95F02",
        "#7570B3","#E7298A","#66A61E","#E6AB02","#A6761D","#666666","#4DB6AC","#BA68C8","#F06292","#7986CB"
      ],

      downloading: false,
      markLocal: this.mark as MarkType,
      horizontalLocal: this.horizontal,
      showLabelsLocal: this.showLabels,
      displayLocal: this.display as DisplayMode,

      internalData: (this.dataset ?? []) as Array<Record<string, any>>,
      internalCols: [] as any[],
      error: "" as string,
      loading: false,
      showLegendLocal: this.showLegend,

      tableSearch: "",
      sortKey: "",
      sortDir: "asc" as "asc" | "desc",
      page: 1,
      pageSize: this.tablePageSize,

      resizeObs: null as ResizeObserver | null,
      visObs: null as IntersectionObserver | null,

      fullPageLocal: this.fullPage,
      apexHeightLocal: this.height ?? 420,
      chartTitle: "" as string,
    };
  },

  computed: {
    xAngle(): number {
      const v = this.xLabelAngle ?? 45;
      return Math.max(-80, Math.min(80, v));
    },
    xAlign(): "left" | "center" | "right" {
      return this.xAngle > 0 ? "right" : this.xAngle < 0 ? "left" : "center";
    },
    wrapperStyle(): Record<string, string> {
      return this.computeWrapper().style;
    },
    apexHeight(): number | string { return this.apexHeightLocal; },

    /* -------- inference -------- */
    inferredX(): string | "" {
      if (!this.autoInfer || !this.internalCols?.length) return "";
      const txt = this.internalCols.find(this.isTextCol);
      return (txt as any)?.name || (txt as any)?.display_name || (txt as any)?.["lib/deduplicated-name"] || "";
    },
    inferredValueFields(): string[] {
      if (!this.autoInfer || !this.internalCols?.length) return [];
      return this.internalCols
        .filter(this.isNumericCol)
        .map((c: any) => c?.name ?? c?.display_name ?? c?.["lib/deduplicated-name"]);
    },

    effX(): string {
      return (this.x && this.x.length) ? this.x : (this.inferredX || this.x || "");
    },
    effSeriesList(): string[] {
      if (this.valueFields?.length) return this.valueFields;
      if (this.y && (!this.autoInfer || this.inferredValueFields.length <= 1)) return [this.y];
      if (this.autoInfer && this.inferredValueFields.length) return this.inferredValueFields;
      const sample = this.internalData[0] || {};
      return Object.keys(sample).filter(k => typeof (sample as any)[k] === "number");
    },
    isMultiSeries(): boolean { return this.effSeriesList.length > 1; },

    plottedData(): Array<Record<string, any>> {
      if (!this.internalData?.length || !this.effX) return [];
      if (this.isMultiSeries) {
        return this.toLongForm(this.internalData, this.effSeriesList, this.effX, this.seriesFieldName, this.valueFieldName);
      }
      return this.internalData;
    },

    colorFieldUsed(): string | null {
      if (this.colorField) return this.colorField;
      if (this.isMultiSeries) return this.seriesFieldName;
      if (["pie","donut","polarArea","radialBar","treemap","heatmap"].includes(this.markLocal)) return this.effX;
      if (this.markLocal === "bar") return this.effX;
      return null;
    },
    seriesDomain(): string[] {
      const cf = this.colorFieldUsed;
      if (!cf) return [];
      const s = new Set<string>();
      for (const r of this.plottedData) {
        const v = (r as any)?.[cf];
        if (v !== null && v !== undefined) s.add(String(v));
      }
      return Array.from(s);
    },
    colors(): string[] {
      const domain = this.seriesDomain;
      if (Object.keys(this.colorMap).length > 0 && domain.length > 0) {
        return domain.map((k, i) => this.colorMap[k] ?? this.defaultColors[i % this.defaultColors.length]);
      }
      if (this.colorRange.length > 0) return this.colorRange;
      if (this.color && !this.colorFieldUsed) return [this.color];
      return this.defaultColors;
    },

    hasChartData(): boolean {
     if (['number','progress','gauge'].includes(this.markLocal)) return true;
      return Array.isArray(this.internalData) && this.internalData.length > 0 && !!this.effX && this.effSeriesList.length > 0;
    },

    /* -------- vue-echarts remount key -------- */
    chartFamily(): "cartesian" | "pie" | "gauge" | "heatmap" | "treemap" | "radar" | "funnel" | "other" {
      const m = this.markLocal;
      if (m === "heatmap") return "heatmap";
      if (m === "treemap") return "treemap";
      if (m === "radar") return "radar";
      if (m === "gauge" || m === "radialBar" || m === "number") return "gauge";
      if (m === "pie" || m === "donut" || m === "polarArea") return "pie";
      if (m === "funnel") return "funnel";
      if (m === "progress") return "cartesian";
      return "cartesian";
    },
    chartKey(): string {
      return `${this.theme}-${this.chartFamily}-${this.markLocal}-${this.effX}-${this.effSeriesList.join(",")}`;
    },

    /* -------- ECharts option -------- */
    chartOption(): any {
      
      const categories = Array.from(new Set((this.internalData || []).map(d => String((d as any)?.[this.effX]))));
      const seriesList = this.effSeriesList;
      
      const mark = this.markLocal;

      const isCartesian = ["bar","line","area","scatter","progress"].includes(mark);
      const horiz = (this.horizontalLocal && mark === "bar") || mark === "progress";
      const normalize = mark === "bar" && this.stack === "normalize";
      const colors = this.colors?.length ? this.colors : undefined;

      const valAt = (cat: string, field: string) => {
        const row = (this.internalData || []).find(d => String((d as any)[this.effX]) === cat) || {};
        const v = Number((row as any)[field] ?? 0);
        return Number.isFinite(v) ? v : 0;
      };

      const sums = normalize ? categories.map(c => seriesList.reduce((s, n) => s + valAt(c, n), 0)) : [];
      const pct = (v: number, i: number) => (sums[i] ? v / sums[i] : 0);
      const axisLabelPercent = (v: any) => `${Math.round(v * 100)}%`;

      const labelPos =
        mark === "bar"
          ? (horiz ? (normalize ? "insideRight" : "right") : (normalize ? "insideTop" : "top"))
          : (mark === "line" || mark === "area")
            ? "top"
            : "outside";

      /* ---- series ---- */
      const series: any[] = (() => {
        if (["bar","line","area","scatter"].includes(mark)) {
          return seriesList.map(name => {
            const raw = categories.map((c) => valAt(c, name));
            const data = normalize ? raw.map((v, i) => pct(v, i)) : raw;
            return {
              name,
              type: mark === "area" ? "line" : mark,
              stack: mark === "bar" && (this.stack === "zero" || this.stack === "normalize") ? "total" : undefined,
              areaStyle: mark === "area" ? {} : undefined,
              symbolSize: 6,
              data,
              emphasis: { 
                focus: "series", 
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              },
              label: this.showLabelsLocal ? {
                show: true,
                position: labelPos,
                distance: Math.abs(this.xAngle) > 0 ? 14 : 8,
                formatter: (p: any) => {
                  if (normalize || this.labelFormat === "%") return `${Math.round((p.value ?? 0) * 100)}%`;
                  try { return new Intl.NumberFormat().format(p.value ?? 0); } catch { return String(p.value ?? 0); }
                }
              } : undefined,
              labelLayout: horiz ? { moveOverlap: "shiftX", hideOverlap: true }
                                : { moveOverlap: "shiftY", hideOverlap: true },
            };
          });
        }

        if (["pie","donut","polarArea"].includes(mark)) {
          const metric = seriesList[0];
          return [{
            name: metric,
            type: "pie",
            radius: mark === "donut" ? ["40%","70%"] : "70%",
            roseType: mark === "polarArea" ? "area" : undefined,
            data: categories.map(c => ({ name: c, value: valAt(c, metric) })),
            label: this.showLabelsLocal ? { show: true } : { show: false },
            emphasis: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)' },
          }];
        }

        if (mark === "gauge" || mark === "radialBar") {
  const metric = seriesList[0] || this.y || this.inferredValueFields[0];
  const values = (this.internalData || []).map(r => Number((r as any)[metric] ?? 0)).filter(n => Number.isFinite(n));
  const current = values[0] ?? 0;
  let max = Math.max(...values, 100);
  if (!Number.isFinite(max) || max <= 0) max = 100;

  return [{
    name: metric || 'Value',
    type: "gauge",
    min: 0,
    max,
    progress: { show: true, width: 12 },
    axisLine: { lineStyle: { width: 12 } },
    detail: {
      valueAnimation: true,
      formatter: (v: number) => {
        try { return new Intl.NumberFormat().format(v); } catch { return String(v); }
      }
    },
    data: [{ value: Math.min(current, max), name: metric || '' }],
    emphasis: { 
      shadowBlur: 10,
      shadowOffsetX: 0,
      shadowColor: 'rgba(0, 0, 0, 0.5)' },
  }];
}

        if (mark === "funnel") {
          const metric = seriesList[0];
          const data = categories.map(c => ({ name: c, value: valAt(c, metric) }))
                                 .sort((a, b) => b.value - a.value);
          return [{
            name: metric,
            type: "funnel",
            left: "10%",
            top: 30,
            bottom: 10,
            width: "80%",
            sort: "descending",
            gap: 2,
            label: { show: true, position: "inside" },
            data
          }];
        }

        if (mark === "heatmap") {
          const matrix: any[] = [];
          seriesList.forEach((name, yi) => categories.forEach((c, xi) => matrix.push([xi, yi, valAt(c, name)])));
          return [{ type: "heatmap", data: matrix }];
        }

        if (mark === "treemap") {
          const metric = seriesList[0];
          return [{ type: "treemap", data: categories.map(c => ({ name: c, value: valAt(c, metric) })), leafDepth: 1 }];
        }

        if (mark === "radar") {
          return seriesList.map(name => ({
            name, type: "radar",
            data: [{ value: categories.map(c => valAt(c, name)), name }]
          }));
        }

        if (mark === "progress") {
          const metric = seriesList[0] || this.y || this.inferredValueFields[0];
          const values = (this.internalData || []).map(r => Number((r as any)[metric] ?? 0)).filter(n => Number.isFinite(n));
          const current = values[0] ?? 0;
          const goalCandidate = Number((this.internalData?.[0] as any)?.goal ?? (this.internalData?.[0] as any)?.target ?? NaN);
          let max = Number.isFinite(goalCandidate) ? goalCandidate : Math.max(...values, 100);
          if (!Number.isFinite(max) || max <= 0) max = 100;
          return [{
            type: "bar",
            data: [Math.min(current, max)],
            barMaxWidth: 28,
            itemStyle: { borderRadius: 14 },
            label: {
              show: true,
              position: "insideRight",
              formatter: () => `${Math.round((Math.min(current, max) / max) * 100)}%`
            },
            emphasis: { focus: "series" }
          }];
        }

        if (mark === "number") {
          // Rendered via 'graphic' (below). Keep series empty.
          return [];
        }

        return [];
      })();

      /* ---- axes ---- */
      const xAxis = isCartesian
        ? (horiz
          ? { type: "value",
              show: mark !== "progress",
              axisLabel: (normalize || this.labelFormat === "%")
                ? { formatter: axisLabelPercent, rotate: this.xLabelAngle || 0 }
                : { rotate: this.xLabelAngle || 0 } }
          : { type: "category",
              data: categories,
              axisLabel: { interval: 0, rotate: this.xAngle, align: this.xAlign, hideOverlap: true, overflow: "truncate", width: 140, margin: 12 } })
        : undefined;

      const yAxis = isCartesian
        ? (horiz
          ? { type: "category",
              data: mark === "progress" ? [""] : categories,
              axisLabel: { interval: 0, rotate: 0, width: this.yLabelMaxWidth || 420, overflow: "truncate", hideOverlap: true, margin: 12 },
              show: mark !== "progress" }
          : { type: "value",
              axisLabel: (normalize || this.labelFormat === "%")
                ? { formatter: axisLabelPercent, rotate: this.yLabelAngle || 0 }
                : { rotate: this.yLabelAngle || 0 } })
        : undefined;

      const radar = mark === "radar" ? {
        indicator: categories.map(c => ({ name: c })),
        splitArea: { areaStyle: { opacity: 0.02 } },
      } : undefined;

      /* Legend only where it makes sense (Metabase-like) */
      const supportsLegend = ["bar","line","area","scatter","pie","donut","heatmap","funnel"].includes(mark) || this.isMultiSeries;
      const legendPos = this.legendPos;
      const legend: any = {
        show: this.showLegendLocal && supportsLegend,
        orient: ["left","right"].includes(legendPos) ? "vertical" : "horizontal",
        left: ["left","right"].includes(legendPos) ? legendPos : "center",
        top: ["top","bottom"].includes(legendPos) ? legendPos : "top",
      };

      const xAxisHM = mark === "heatmap" ? { type: "category", data: categories } : undefined;
      const yAxisHM = mark === "heatmap" ? { type: "category", data: seriesList } : undefined;

      const gridBottom = (isCartesian && !horiz && mark !== "progress")
        ? Math.min(130, 26 + Math.abs(this.xAngle) * 1.4 + (this.showLabelsLocal ? 8 : 0))
        : 20;

      /* Number (single value) as central text via graphic */
      const numberGraphic = (() => {
        if (mark !== "number") return undefined;
        const metric = seriesList[0] || this.y || this.inferredValueFields[0];
        const values = (this.internalData || []).map(r => Number((r as any)[metric] ?? 0)).filter(n => Number.isFinite(n));
        const value = values.length ? values[0] : 0;
        const formatted = (() => { try { return new Intl.NumberFormat().format(value); } catch { return String(value); }})();
        return [
          {
            type: 'text',
            left: 'center',
            top: 'middle',
            style: {
              text: formatted,
              fontSize: 48,
              fontWeight: 700
            }
          },
          this.localTitle ? {
            type: 'text',
            left: 'center',
            top: '60%',
            style: { text: this.localTitle, fontSize: 14, opacity: 0.7 }
          } : null
        ].filter(Boolean);
      })();

      return {
        color: colors,
        title: this.chartTitle ? { text: this.chartTitle, left: "left" } : undefined,
        grid: mark === "progress"
          ? { left: 16, right: 16, top: 40, bottom: 30, containLabel: true }
          : isCartesian ? { left: 10, right: 10, top: 30, bottom: gridBottom, containLabel: true }
          : undefined,
        tooltip: mark === "number" ? { show: false } : { trigger: isCartesian ? "axis" : "item", axisPointer: { type: "shadow" } },
        legend,
        xAxis: mark === "heatmap" ? xAxisHM : xAxis,
        yAxis: mark === "heatmap" ? yAxisHM : yAxis,
        radar,
        series,
        graphic: numberGraphic,
        animationDuration: 500,
      };
    },

    /* -------- table -------- */
    tableCols(): string[] {
      if (this.internalCols?.length) {
        return this.internalCols.map((c: any) => c?.name ?? c?.display_name ?? c?.["lib/deduplicated-name"]);
      }
      const first = this.internalData[0] || {};
      return Object.keys(first);
    },
    filteredRows(): Array<Record<string, any>> {
      if (!this.tableSearch) return this.internalData;
      const q = this.tableSearch.toLowerCase();
      return this.internalData.filter(r =>
        this.tableCols.some(c => String((r as any)[c] ?? "").toLowerCase().includes(q))
      );
    },
    sortedRows(): Array<Record<string, any>> {
      if (!this.sortKey) return this.filteredRows;
      const dir = this.sortDir === "asc" ? 1 : -1;
      const key = this.sortKey;
      return [...this.filteredRows].sort((a, b) => {
        const av = (a as any)[key]; const bv = (b as any)[key];
        if (av == null && bv == null) return 0;
        if (av == null) return 1;
        if (bv == null) return -1;
        if (typeof av === "number" && typeof bv === "number") return (av - bv) * dir;
        return String(av).localeCompare(String(bv)) * dir;
      });
    },
    totalPages(): number { return Math.max(1, Math.ceil(this.sortedRows.length / this.pageSize)); },
    pagedRows(): Array<Record<string, any>> {
      const start = (this.page - 1) * this.pageSize;
      return this.sortedRows.slice(start, start + this.pageSize);
    },
  },

  watch: {
    reload() { /* no-op */ },
    dataset: {
      handler(v: any) {
        if (Array.isArray(v)) this.internalData = v;
        this.$nextTick(() => { this.reflow(); });
      },
      deep: true
    },
    mark(v: MarkType) {
      this.markLocal = v;
      this.$nextTick(() => { this.reflow(); });
    },
    horizontal(v: boolean) {
      this.horizontalLocal = v;
      this.$nextTick(() => { this.reflow(); });
    },
    showLabels(v: boolean) {
      this.showLabelsLocal = v;
      this.$nextTick(() => { this.reflow(); });
    },
    tablePageSize(v: number) { this.pageSize = v; this.page = 1; },
    display(v: DisplayMode) {
      this.displayLocal = v;
      this.$nextTick(() => { this.reflow(); });
    },
    showLegend(v: boolean) {
      this.showLegendLocal = v;
      this.$nextTick(() => { this.reflow(); });
    },
    height() { this.$nextTick(() => this.reflow()); },
    fullPage(v: boolean) { this.fullPageLocal = v; this.$nextTick(() => this.reflow()); },
    theme() { this.$nextTick(() => this.reflow()); },
    x() { this.$nextTick(() => this.reflow()); },
    valueFields() { this.$nextTick(() => this.reflow()); },
    y() { this.$nextTick(() => this.reflow()); },
    colorRange() { this.$nextTick(() => this.reflow()); },
    color() { this.$nextTick(() => this.reflow()); },
    colorMap: { handler() { this.$nextTick(() => this.reflow()); }, deep: true },
  },

  async mounted() {
    if (this.mapId && this.apiAutoLoad) await this.loadFromApi();
    this.$nextTick(() => this.reflow());

    this.resizeObs = new ResizeObserver(() => this.reflow());
    const wrap = this.$refs.wrap as HTMLElement | undefined;
    if (wrap && this.resizeObs) this.resizeObs.observe(wrap);

    const area = this.$refs.chartArea as HTMLElement | undefined;
    if ("IntersectionObserver" in window && area) {
      this.visObs = new IntersectionObserver(entries => {
        if (entries.some(e => e.isIntersecting)) this.reflow();
      }, { threshold: [0, 0.01, 0.1] });
      this.visObs.observe(area);
    }

    window.addEventListener("resize", this.reflow as any, { passive: true });
  },

  beforeUnmount() {
    if (this.resizeObs) {
      const wrap = this.$refs.wrap as HTMLElement | undefined;
      if (wrap) this.resizeObs.unobserve(wrap);
      this.resizeObs = null;
    }
    if (this.visObs) {
      const area = this.$refs.chartArea as HTMLElement | undefined;
      if (area) this.visObs.unobserve(area);
      this.visObs = null;
    }
    try { document.body.style.overflow = ""; } catch {}
    window.removeEventListener("keydown", this.onEsc as any);
    window.removeEventListener("resize", this.reflow as any);
  },

  created() {
      console.log("ApexChart created : ", this.mark);
  },
  methods: {
    getEcharts() {
      const cmp = this.$refs.echartRef as any;              // ref on <VChart/>
      return cmp?.getEchartsInstance?.();                   // vue-echarts API
    },
    setLegend(show: boolean) {
      this.getEcharts()?.setOption({ legend: { show } });
    },

    /* ========= Data helpers ========= */
    mapRowsCols(payload: any): { rows: Array<Record<string, any>>, cols: any[], title?: string } {
      let cols = payload?.cols, rows = payload?.rows;
      if (!cols || !rows) { cols = payload?.data?.cols; rows = payload?.data?.rows; }

      const names = (cols ?? []).map((c: any) => c?.name ?? c?.display_name ?? c?.["lib/deduplicated-name"]);
      const mapped = (rows ?? []).map((r: any[]) => Object.fromEntries(names.map((n: string, i: number) => [n, r[i]])));

      const title =
        payload?.question?.name ||
        payload?.name ||
        payload?.card?.name ||
        payload?.metadata?.name ||
        payload?.data?.name ||
        undefined;

      return { rows: mapped, cols: cols ?? [], title };
    },
    isTextCol(c: any): boolean {
      const t = (c?.effective_type || c?.base_type || "").toString().toLowerCase();
      return t.includes("type/text");
    },
    isNumericCol(c: any): boolean {
      const t = (c?.effective_type || c?.base_type || "").toString().toLowerCase();
      return t.includes("type/number") || t.includes("biginteger") || t.includes("integer") || t.includes("float") || t.includes("decimal");
    },
    toLongForm(
      data: Array<Record<string, any>>,
      keys: string[],
      baseField: string,
      seriesField = "series",
      valueField = "value"
    ) {
      const out: Array<Record<string, any>> = [];
      for (const row of data) for (const k of keys) {
        out.push({ [baseField]: (row as any)[baseField], [seriesField]: k, [valueField]: (row as any)[k] });
      }
      return out;
    },

    /* ========= Download actions ========= */
    setDownloadItems() {
      this.downloadOptions = [
        { key: "csv", label: "CSV", icon: "pi pi-file", command: () => this.handleDownload("csv") },
        { key: "xlsx", label: "Excel", icon: "pi pi-file-excel", command: () => this.handleDownload("xlsx") },
      ];
    },
    toggleDownLoadMenu(event: any) {
      (this.$refs.downloadMenu as any)?.toggle(event);
      this.setDownloadItems();
    },
    filenameFromDisposition(disposition?: string, fallback = "download") {
      if (!disposition) return fallback;
      const match = /filename\*?=(?:UTF-8'')?["']?([^"';]+)["']?/i.exec(disposition);
      return decodeURIComponent((match?.[1] ?? fallback)).trim();
    },
    async downloadWithAxios(url: string, fallbackName: string) {
      this.downloading = true;
      const cache = _AppCache.getSession() || {};
      try {
        const res = await axios.post(url, this.createRequestFilter(), {
          responseType: "blob",
          timeout: 300000,
          headers: {
            'x-access-token': cache.token,
            Authorization: `Bearer ${cache.token}`,
            ...this.apiHeaders
          }
        });
        const blob = res.data as Blob;
        const cd = (res.headers as any)?.["content-disposition"];
        const name = this.filenameFromDisposition(cd, fallbackName);
        const a = document.createElement("a");
        const href = URL.createObjectURL(blob);
        a.href = href; a.download = name; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(href);
      } catch (e: any) {
        console.error("Download failed:", e);
        this.error = `Download failed: ${e?.message || e}`;
      } finally {
        this.downloading = false;
        
      }
    },
    async handleDownload(kind: "csv" | "xlsx") {
      let url = `${(MetabaseService as any).server}/reports/mb_report_question_data/${this.mapId}/${kind}`;
      url = url.replace(/\/\//g, "/").replace(":/", "://");
      if (!url) { this.error = "Download URL could not be inferred."; return; }
      const baseName =
        (this.localTitle && this.localTitle.trim()) ||
        (`${this.mapId}`?.match(/\d+/)?.[0] ? `report_${this.mapId.match(/\d+/)![0]}` : "report");
      const fallback = `${baseName}.${kind}`;
      await this.downloadWithAxios(url, fallback);
    },

    /* ========= Layout / size ========= */
    computeWrapper() {
      const wrap = this.$refs.wrap as HTMLElement | undefined;
      const area = this.$refs.chartArea as HTMLElement | undefined;
      const padding = this.padding ?? 0;
      const toolbar = this.$refs.toolbar as HTMLElement | undefined;

      const totalH = this.fullPageLocal ? window.innerHeight : (this.height || wrap?.clientHeight || 0);
      const containerW = (area?.clientWidth ?? wrap?.clientWidth ?? 0);
      const innerW = Math.max(0, containerW - (padding * 2));
      const controlsH = (this.controls && toolbar) ? toolbar.offsetHeight : 0;
      let innerH = Math.max(240, totalH - 30 - (padding * 2) - controlsH - 4);

      const style: Record<string, string> = {
        width: this.fullPageLocal ? "100vw" : "100%",
        height: (this.fullPageLocal ? `${this.displayLocal === 'both' ? window.innerHeight / 2 : window.innerHeight}px` : (this.height ? `${this.height}px` : "100%")),
        padding: `${padding}px`,
      };

      return { totalH, controlsH, innerH, innerW, style };
    },
    computeChartHeight() {
      const { innerH } = this.computeWrapper();
      this.apexHeightLocal = innerH;
    },
    reflow() {
      this.computeChartHeight();
      setTimeout(() => { this.nudgeWrapperWidth(); }, 200);
    },
    async nudgeWrapperWidth() {
      const wrap = this.$refs.wrap as HTMLElement | undefined;
      if (!wrap) return;
      const prevWidth = wrap.style.width;
      const prevTransition = wrap.style.transition;
      wrap.style.transition = 'none';
      const originalPx = `${wrap.getBoundingClientRect().width}px`;
      wrap.style.width = '10px';
      void wrap.offsetWidth;
      wrap.style.width = originalPx;
      await this.$nextTick();
      wrap.style.transition = prevTransition;
      if (prevWidth) wrap.style.width = prevWidth; else wrap.style.removeProperty('width');
    },

    /* ========= API ========= */
    createRequestFilter() { return [ this.queryParameter ]; },
    async loadFromApi() {
      this.error = ""; this.loading = true;
      try {
        const result = await OrgUnitService.read(this.orgUnitId);
        this.queryParameter = { name: `${result.level}_id`, value: result.id };
        const json = await (MetabaseService as any).getData(this.mapId, this.createRequestFilter());
        const { rows, cols, title } = this.mapRowsCols(json);
        this.internalData = rows;
        this.internalCols = cols || [];
        this.localTitle = title || "";
        this.chartTitle = '';
        this.page = 1; this.tableSearch = "";
      } catch (e: any) {
        this.error = `API: ${e?.message || e}`;
      } finally {
        this.loading = false;
        this.$nextTick(() => { this.reflow(); });
      }
    },

    /* ========= Controls ========= */
    async setDisplay(mode: DisplayMode) {
      this.displayLocal = mode;
      await this.$nextTick();
      this.nudgeWrapperWidth();
    },
    async refreshChart() {
      this.loading = true;
      try {
        if (this.mapId) { await this.loadFromApi(); }
        else { await nextTick(); this.reflow(); }
      } finally { this.loading = false; }
    },

    toggleFullPage() {
      this.fullPageLocal = !this.fullPageLocal;

      // lock/unlock page scroll
      try { document.body.style.overflow = this.fullPageLocal ? "hidden" : ""; } catch {}

      // attach / detach ESC listener
      if (this.fullPageLocal) {
        window.addEventListener("keydown", this.onEsc as any, { passive: true });
      } else {
        window.removeEventListener("keydown", this.onEsc as any);
      }

      this.$nextTick(() => { this.reflow(); });
    },

    onEsc(e: KeyboardEvent) {
      if (e.key === "Escape" && this.fullPageLocal) {
        this.fullPageLocal = false;
        try { document.body.style.overflow = ""; } catch {}
        this.$nextTick(() => this.reflow());
      }
    },

    /* ========= Table helpers ========= */
    sortBy(col: string) {
      if (this.sortKey === col) this.sortDir = this.sortDir === "asc" ? "desc" : "asc";
      else { this.sortKey = col; this.sortDir = "asc"; }
    },
    formatCell(v: any) {
      if (v === null || v === undefined) return "";
      if (typeof v === "number") { try { return new Intl.NumberFormat().format(v); } catch { return v; } }
      return String(v);
    },
    nextPage() { if (this.page < this.totalPages) this.page += 1; },
    prevPage() { if (this.page > 1) this.page -= 1; },
  },
});
</script>

<style scoped>
/* ECharts host element */
.echart-host { width: 100%; min-height: 160px; }

/* ---- Original styles (kept) ---- */
.chart-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 260px;
  display: flex;
  flex-direction: column;
  border-radius: 10px;
  transition: box-shadow .2s ease-in-out;
}

/* Fullscreen mode */
.chart-wrapper.fullscreen { position: fixed; inset: 0; z-index: 9999; border-radius: 0; }

/* Loading overlay */
.loading-overlay {
  position: absolute; inset: 0; background: rgba(255, 255, 255, 0.6);
  display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 5;
}
.chart-wrapper.dark .loading-overlay { background: rgba(0, 0, 0, 0.35); }
.spinner { width: 28px; height: 28px; border: 3px solid rgba(0, 0, 0, 0.15); border-top-color: #3b82f6; border-radius: 50%; animation: spin 0.8s linear infinite; }
.loading-text { margin-top: 8px; font-size: 12px; font-weight: 600; }
@keyframes spin { to { transform: rotate(360deg); } }

/* themes */
.chart-wrapper.light { background: #fff; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08); }
.chart-wrapper.light:hover { box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12); }
.chart-wrapper.dark { background: #0f1115; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.5); }
.chart-wrapper.dark:hover { box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6); }

.chart-wrapper.resizable { resize: both; overflow: auto; min-width: 280px; min-height: 220px; border: 1px dashed rgba(0, 0, 0, 0.15); padding: 8px; }
.chart-wrapper.panel.p-panel-header { display: none !important; }

/* toolbar */
.p-panel-header {
  display: grid; background-color: #0b0e13;
  grid-template-columns: auto auto auto auto auto 1fr auto;
  gap: 12px; align-items: center; font-size: 13px; margin-bottom: 8px;
  padding: 5px; border-radius: 8px; border: 1px solid #e5e7eb;
}
.styled-panel.light :deep(.p-panel-header) {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-bottom: 1px solid #cbd5e0; padding: 1.25rem 1.5rem;
}
.chart-wrapper.light .p-panel-header { background: #f9fafb; color: #374151; }
.chart-wrapper.dark .p-panel-header { background: #111827; border-color: #1f2937; color: #e5e7eb; }

.p-panel-header label { display: inline-flex; gap: 6px; align-items: center; font-weight: 500; margin-left: 10px; cursor: pointer; }
.p-panel-header button { margin-left: 20px; }
.p-panel-header label:first-child { margin-left: 0; }
.p-select { border: none; }
.p-panel-header select, .p-panel-header input[type="checkbox"] { cursor: pointer; }

.controls-actions { display: inline-flex; gap: 8px; }

/* CHART AREA */
.chart-area { flex: 1 1 auto; display: flex; width: 100%; margin-top: -20px; }

/* TABLE */
.table-area { margin-top: 10px; display: flex; flex-direction: column; gap: 8px; }
.table-title { margin: 0 0 4px; font-size: 20px; font-weight: 700; color: #696e7b; }
.table-toolbar { display: flex; align-items: center; gap: 10px; }
.table-search { width: 240px; padding: 6px 8px; border: 1px solid #e5e7eb; border-radius: 6px; }
.rows-count { margin-left: auto; font-size: 12px; opacity: .75; }

.table-scroll { overflow: auto; border: 1px solid #e5e7eb; border-radius: 8px; }
.datatable { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 11px; }
.datatable thead th { position: sticky; top: 0; background: #f3f4f6; text-align: left; padding: 3px 6px; border-bottom: 1px solid #e5e7eb; cursor: pointer; }
.datatable thead th.active { color: #111827; }
.datatable thead th.sortable:hover { background: #eef2ff; }
.sort-indicator { margin-left: 6px; font-size: 11px; opacity: .7; }
.datatable tbody td { padding: 8px 10px; border-bottom: 1px solid #f1f5f9; }
.datatable tbody tr:nth-child(odd) td { background: #fafafa; }

.pager { display: flex; align-items: center; gap: 10px; justify-content: flex-end; }
.pager button { border: 1px solid #e5e7eb; background: #fff; padding: 4px 10px; border-radius: 6px; cursor: pointer; }
.pager button:disabled { opacity: .5; cursor: not-allowed; }
.page-size { display: inline-flex; align-items: center; gap: 6px; }

/* PrimeVue overlay over fullscreen */
:deep(.p-dropdown-panel) { z-index: 10050 !important; }

/* compact dropdown */
.p-dropdown { min-width: 280px; }
</style>
