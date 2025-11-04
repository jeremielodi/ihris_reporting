<!-- src/components/ApexChart.vue -->
<template>
  <div toggleable :id="wrapperID" :class="[
    'chart-wrapper',
    theme,
    { resizable, fullscreen: fullPageLocal }
  ]" :style="wrapperStyle" ref="wrap">
    <Panel style="width: 100%;" class='styled-panel'>

      <template #header>

        <div ref="toolbar" class="controls">
          <label v-if="display != 'table'">
            <i class="pi pi-chart-bar" style="font-size: 1.5rem"  @click="async ()=>{
              displayLocal = 'chart';
              await $nextTick();
              nudgeWrapperWidth();
            }"></i> &nbsp;
            <i class="pi pi-table" style="font-size: 1.5rem"  @click="async ()=>{
              displayLocal = 'table';
              await $nextTick();
              nudgeWrapperWidth();
            }"></i>
            
          </label>

          <label  v-if="display != 'table'">
        
            <Dropdown title="Type" v-model="markLocal" @change="nudgeWrapperWidth()" :options="chartTypes" optionLabel="label"
              optionValue="value" class="w-48">
              <!-- Custom template to show icons + labels -->
              <template #option="slotProps">
                <div class="flex items-center gap-2">
                  <i :class="slotProps.option.icon"></i>
                  <span>{{ slotProps.option.label }}</span>
                </div>
              </template>

              <!-- Selected item template -->
              <template #value="slotProps">
                <div v-if="slotProps.value" class="flex items-center gap-2">
                  <i :class="chartTypes.find(ct => ct.value === slotProps.value)?.icon"></i>
                  <span>{{chartTypes.find(ct => ct.value === slotProps.value)?.label}}</span>
                </div>
                <span v-else>Select type</span>
              </template>
            </Dropdown>
          </label>

          <label  v-if="display != 'table'">
            Horizontal&nbsp;
            <input type="checkbox" v-model="horizontalLocal" :disabled="markLocal !== 'bar'" />
          </label>

          <label  v-if="display != 'table'">
            Labels&nbsp;
            <input type="checkbox" v-model="showLabelsLocal"
              :disabled="['pie', 'donut', 'radialBar', 'heatmap', 'treemap', 'polarArea'].includes(markLocal)" />
          </label>

          <div class="controls-actions">
            
            <Button type="button" severity="secondary"  title="Refresh" icon="pi pi-refresh" :class="{'pi-spinner': loading}" :loading="loading" :disabled="loading" @click="refreshChart" />

            <Button severity="secondary" :icon="!fullPageLocal ? 'pi pi-arrows-h': 'pi pi-arrow-down-left-and-arrow-up-right-to-center'" v-tooltip="fullPageLocal ? 'Exit Full page' : 'Full page'" class="fullscreen-btn" @click="toggleFullPage"/>
          </div>
        </div>

      </template>

      <template #icons>
        <Button type="button" severity="secondary"  icon="pi pi-download" @click="toggleDownLoadMenu"
            aria-haspopup="true" aria-controls="overlay_menu" />
          <Menu ref="downloadMenu" id="overlay_menu" :model="downloadOptions" :popup="true" />
      
      </template>
      <!-- LOADING OVERLAY -->
      <div v-if="loading" class="loading-overlay">
        <div class="spinner"></div>
        <div class="loading-text">Loading…</div>
      </div>



      <!-- CHART -->
      <div v-if="displayLocal !== 'table'" class="chart-area" ref="chartArea">
        <apexcharts :key="renderKey" :ref="chartRef" v-if="hasChartSeries" :type="apexType" :options="options"
          :series="series" :height="apexHeight" />
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
                <th v-for="c in tableCols" :key="c" @click="sortBy(c)"
                  :class="{ sortable: true, active: sortKey === c }">
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
  import { defineComponent, PropType } from "vue";
  import VueApexCharts from "vue3-apexcharts";
  import axios from "axios";
  import _AppCache from "../service/appCache";
  import MetabaseService from "@/views/pages/career/metabase/metabase.service";
  import OrgUnitService from "../views/pages/manage/organization_units/orgUnit.service";

  type MarkType =
    | "bar" | "line" | "area" | "scatter" | "bubble"
    | "pie" | "donut" | "radialBar"
    | "heatmap" | "treemap" | "radar" | "polarArea";
  type DisplayMode = "chart" | "table" | "both";

  export default defineComponent({
    name: "ApexChart",
    components: { apexcharts: VueApexCharts },

    props: {
      QueryResult: [],
      orgUnitId: { type: String, default: "" },
      card: { type: Object as PropType<Record<string, any>>, required: true },
      dataset: { type: Array as PropType<Array<Record<string, any>>>, default: () => [] },
      mapId: { type: String, default: "" },
      apiHeaders: { type: Object as PropType<Record<string, string>>, default: () => ({}) },
      apiAutoLoad: { type: Boolean, default: true },
      reload: { type: Number, },
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

      xLabelAngle: { type: Number, default: -45 },
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
        this.$nextTick(() => {
           this.renderKey =  `renderKey${Math.random()}`;
        })
      },

    data() {
      return {
        queryParameter: {},
        wrapperID: `chart${Math.random()}`,
        renderKey: `renderKey${Math.random()}`,
        downloadOptions: [] as any[],
        chartRef:  `chart${Math.random()}`,
        chartTypes: [
          { label: 'Bar', value: 'bar', icon: 'pi pi-chart-bar' },
          { label: 'Line', value: 'line', icon: 'pi pi-chart-line' },
          { label: 'Area', value: 'area', icon: 'pi pi-chart-area' },
          { label: 'Scatter', value: 'scatter', icon: 'pi pi-circle-fill' },
          { label: 'Bubble', value: 'bubble', icon: 'pi pi-circle-off' },
          { label: 'Pie', value: 'pie', icon: 'pi pi-chart-pie' },
          { label: 'Donut', value: 'donut', icon: 'pi pi-chart-pie' },
          { label: 'RadialBar', value: 'radialBar', icon: 'pi pi-circle' },
          { label: 'Heatmap', value: 'heatmap', icon: 'pi pi-th-large' },
          { label: 'Treemap', value: 'treemap', icon: 'pi pi-sitemap' },
          { label: 'Radar', value: 'radar', icon: 'pi pi-sliders-h' },
          { label: 'PolarArea', value: 'polarArea', icon: 'pi pi-circle-on' },
        ],
        defaultColors: [
          "#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F", "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AC",
          "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
          "#2E86AB", "#F6C85F", "#6F4E7C", "#9FD356", "#CA472F", "#FFA056", "#36A2EB", "#9966FF", "#8DD3C7", "#80B1D3",
          "#FB8072", "#FDB462", "#B3DE69", "#FCCDE5", "#BC80BD", "#CCEBC5", "#FFED6F", "#A6CEE3", "#1B9E77", "#D95F02",
          "#7570B3", "#E7298A", "#66A61E", "#E6AB02", "#A6761D", "#666666", "#4DB6AC", "#BA68C8", "#F06292", "#7986CB"
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
      wrapperStyle(): Record<string, string> {
        return this.computeWrapper().style;
      },
      apexHeight(): number | string { return this.apexHeightLocal; },

      /* inference */
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
        if (["pie", "donut", "polarArea", "radialBar", "treemap", "heatmap"].includes(this.markLocal)) return this.effX;
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

      /* series/options */
      series(): any {
        const x = this.effX, y = this.isMultiSeries ? this.valueFieldName : (this.effSeriesList[0] || this.valueFieldName);
        const cats = Array.from(new Set(this.internalData.map(d => String((d as any)[x]))));

        if (["pie", "donut", "polarArea", "radialBar"].includes(this.markLocal)) {
          const metric = this.isMultiSeries ? this.effSeriesList[0] : y;
          return this.internalData.map(d => Number((d as any)[metric] ?? 0));
        }

        if (this.markLocal === "heatmap") {
          if (this.isMultiSeries) {
            return this.effSeriesList.map(name => ({
              name,
              data: cats.map(cx => ({ x: cx, y: Number(((this.internalData.find(d => String((d as any)[x]) === cx) || {}) as any)[name] ?? 0) }))
            }));
          }
          const metric = this.effSeriesList[0];
          return [{
            name: String(metric),
            data: cats.map(cx => ({ x: cx, y: Number(((this.internalData.find(d => String((d as any)[x]) === cx) || {}) as any)[metric] ?? 0) }))
          }];
        }

        if (this.markLocal === "treemap") {
          const metric = this.effSeriesList[0];
          return [{ data: this.internalData.map(d => ({ x: String((d as any)[x]), y: Number((d as any)[metric] ?? 0) })) }];
        }

        if (this.isMultiSeries) {
          if (this.markLocal === "bubble") {
            return this.effSeriesList.map(name => ({
              name,
              data: cats.map(cx => {
                const v = Number(((this.internalData.find(d => String((d as any)[x]) === cx) || {}) as any)[name] ?? 0);
                return { x: cx, y: v, z: Math.max(5, Math.min(60, v)) };
              })
            }));
          }
          return this.effSeriesList.map(name => ({
            name,
            data: cats.map(cx => Number(((this.internalData.find(d => String((d as any)[x]) === cx) || {}) as any)[name] ?? 0))
          }));
        }

        const metric = this.effSeriesList[0];
        if (this.markLocal === "bubble") {
          return [{
            name: String(metric),
            data: cats.map(cx => {
              const v = Number(((this.internalData.find(d => String((d as any)[x]) === cx) || {}) as any)[metric] ?? 0);
              return { x: cx, y: v, z: Math.max(5, Math.min(60, v)) };
            })
          }];
        }
        return [{
          name: String(metric),
          data: cats.map(cx => Number(((this.internalData.find(d => String((d as any)[x]) === cx) || {}) as any)[metric] ?? 0))
        }];
      },

      hasChartSeries(): boolean {
        if (!this.internalData.length || !this.effX) return false;
        if (["pie", "donut", "polarArea", "radialBar"].includes(this.markLocal)) return (this.series as any)?.length > 0;
        return Array.isArray(this.series) ? (this.series as any).length > 0 : !!this.series;
      },

      options(): any {
        const categories = Array.from(new Set(this.internalData.map(d => String((d as any)[this.effX]))));
        const isBar = this.markLocal === "bar";
        const horiz = isBar && this.horizontalLocal;
        const isSingleSeriesBar = isBar && !this.isMultiSeries;

        const distributed = isSingleSeriesBar;
        const stacked = isBar && (this.stack === "zero" || this.stack === "normalize");
        const stackType = this.stack === "normalize" ? "100%" : undefined;

        const qualitativeTitle = this.effX || "Category";
        const quantitativeTitle = this.isMultiSeries ? "Value" : (this.effSeriesList[0] || "Value");

        const dataLabels = {
          enabled: this.showLabelsLocal && !["pie", "donut", "radialBar", "heatmap", "treemap", "polarArea"].includes(this.markLocal),
          formatter: (val: number) => {
            if (this.labelFormat === "%") return `${(val * 100).toFixed(0)}%`;
            try { return new Intl.NumberFormat().format(val); } catch { return String(val); }
          },
          offsetY: horiz ? 0 : this.dataLabelsOffsetY,
          offsetX: horiz ? 6 : 0,
          style: { fontSize: "12px" },
          background: {
            enabled: true,
            foreColor: "blue",
            borderRadius: 2,
            padding: 4,
            opacity: 0.9,
            borderWidth: 1,
            borderColor: "#fff",
          },
        };

        const legendShow =
          this.showLegend &&
          (["pie", "donut", "radialBar", "radar", "polarArea", "heatmap", "treemap"].includes(this.markLocal) || this.isMultiSeries);

        const labels = ["pie", "donut", "polarArea", "radialBar"].includes(this.markLocal) ? categories : undefined;

        const xaxis = ["pie", "donut", "radialBar", "polarArea", "treemap", "heatmap"].includes(this.markLocal)
          ? undefined
          : {
            categories,
            labels: horiz ? { show: false } : { rotate: this.xLabelAngle, trim: false },
            axisTicks: { show: !horiz },
            axisBorder: { show: !horiz },
            tickPlacement: "on",
            title: { text: horiz ? quantitativeTitle : qualitativeTitle },
          };

        const yaxis = ["pie", "donut", "radialBar", "polarArea", "treemap", "heatmap"].includes(this.markLocal)
          ? undefined
          : {
            labels: horiz
              ? {
                maxWidth: this.yLabelMaxWidth ?? 420,
                formatter: (v: any) => String(v ?? "").replace(/_/g, " "),
                trim: false,
                style: { fontSize: "14px", fontWeight: 700, colors: "#4b5563" },
              }
              : { rotate: this.yLabelAngle },
            title: { text: horiz ? qualitativeTitle : quantitativeTitle },
          };

        return {
          chart: { type: this.apexType, toolbar: { show: false }, stacked, stackType, parentHeightOffset: 0 },
          title: this.chartTitle ? { text: this.chartTitle, align: "left", style: { fontWeight: 700, fontSize: 20, color:'#696e7b' } } : undefined,
          colors: this.colors,
          labels,
          xaxis,
          yaxis,
          dataLabels,
          legend: { show: legendShow, position: this.legendPos as any },
          tooltip: { enabled: true },
          stroke: {
            curve: (this.markLocal === "line" || this.markLocal === "area" || this.markLocal === "radar") ? "smooth" : "straight",
            width: this.markLocal === "scatter" ? 0 : 2,
          },
          markers: { size: (this.markLocal === "scatter" || this.markLocal === "line") ? 4 : 0 },
          plotOptions: {
            bar: {
              horizontal: horiz,
              distributed,
              barHeight: horiz ? "55%" : undefined,
              borderRadius: 4,
              dataLabels: { position: horiz ? "center" : "top" },
            },
            radialBar: { dataLabels: { total: { show: false } } },
            heatmap: { colorScale: { inverse: false } },
            treemap: { enableShades: false },
            radar: { polygons: { fill: { opacity: 0.02 } } },
          },
          grid: {
            padding: { left: 12, right: 8 },
            xaxis: { lines: { show: !horiz } },
            yaxis: { lines: { show: true } },
          },
          responsive: [
            { breakpoint: 1024, options: { chart: { width: "100%" } } },
            { breakpoint: 768, options: { chart: { width: "100%" } } },
            { breakpoint: 480, options: { chart: { width: "100%" } } },
          ],
        };
      },

      apexType(): any { return this.markLocal; },

      /* table */
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
      reload: (v) => {
        console.log('reload :' + v)
      },
      dataset: {
        handler(v: any) {
          if (Array.isArray(v)) this.internalData = v;
          this.$nextTick(() => { this.rebuildChart(); this.reflow(); });
        },
        deep: true
      },
      mark(v: MarkType) {
        this.markLocal = v;
        console.log(this.markLocal);
        this.$nextTick(() => {
          this.rebuildChart(); this.reflow();
        });
      },
      horizontal(v: boolean) {
        this.horizontalLocal = v;
        this.$nextTick(() => {
          this.rebuildChart()
        });
      },
      showLabels(v: boolean) {
        this.showLabelsLocal = v;
        this.$nextTick(() => { this.rebuildChart(); this.reflow(); });
      },
      tablePageSize(v: number) { this.pageSize = v; this.page = 1; },

      display(v: DisplayMode) {
        this.displayLocal = v;
        this.$nextTick(() => { this.rebuildChart(); this.reflow(); });
      },

      height() { this.$nextTick(() => this.reflow()); },
      fullPage(v: boolean) { this.fullPageLocal = v; this.$nextTick(() => this.reflow()); }
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

      window.addEventListener("resize", this.reflow, { passive: true });
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
      window.removeEventListener("resize", this.reflow as any);
    },
    created() {
    },
    methods: {
      /* ========= MOVED HELPERS (now methods) ========= */
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
            headers:{
              'x-access-token': cache.token,
              Authorization: `Bearer ${cache.token}`,
            }
          });
          const blob = res.data as Blob;
          const cd = (res.headers as any)?.["content-disposition"];
          const name = this.filenameFromDisposition(cd, fallbackName);

          const a = document.createElement("a");
          const href = URL.createObjectURL(blob);
          a.href = href;
          a.download = name;
          document.body.appendChild(a);
          a.click();
          a.remove();
          URL.revokeObjectURL(href);
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
        if (!url) {
          this.error = "Download URL could not be inferred.";
          return;
        }
        const baseName =
          (this.chartTitle && this.chartTitle.trim()) ||
          (this.mapId?.match(/\d+/)?.[0] ? `report_${this.mapId.match(/\d+/)![0]}` : "report");
        const fallback = `${baseName}.${kind}`;
        await this.downloadWithAxios(url, fallback);
      },

      /* ========= Chart refs & layout ========= */
      getChartInstance(): any | null {
        const cmp: any = this.$refs[this.chartRef];

        return cmp?.chart || null;
      },
      computeWrapper() {
        const wrap = this.$refs.wrap as HTMLElement | undefined;
        const area = this.$refs.chartArea as HTMLElement | undefined;
        const padding = this.padding ?? 0;
        const toolbar = this.$refs.toolbar as HTMLElement | undefined;

        const totalH = this.fullPageLocal
          ? window.innerHeight
          : (this.height || wrap?.clientHeight || 0);

        const containerW = (area?.clientWidth ?? wrap?.clientWidth ?? 0);
        const innerW = Math.max(0, containerW - (padding * 2));

        const controlsH = (this.controls && toolbar) ? toolbar.offsetHeight : 0;
        let innerH = Math.max(240,  totalH -30-(padding * 2) - controlsH - 4);
        
        const style: Record<string, string> = {
          width: "100%",
          height: (this.fullPageLocal ? `${this.display == 'both'? window.innerHeight/2:  window.innerHeight}px` : (this.height ? `${this.height}px` : "100%")),
          padding: `${padding}px`,
        };

        return { totalH, controlsH, innerH, innerW, style };
      },
      computeChartHeight() {
        const { innerH } = this.computeWrapper();
        this.apexHeightLocal = innerH;
      },
      computeChartWidth(): number {
        const { innerW } = this.computeWrapper();
        return innerW > 0 ? innerW : 0;
      },
      ensureWidthAfterShow() {
        requestAnimationFrame(() => {
          this.resizeChart();
        });
      },
      resizeChart() {
        const chart = this.getChartInstance();
        if (!chart) return;
        const w = this.computeChartWidth();
        if (w <= 0) return;
        try {
          chart.updateOptions(
            { chart: { width: w, height: this.apexHeightLocal } },
            false,
            false,
            true
          );
        } catch { }
      },

      /* ========= Data ========= */
        createRequestFilter() {
        return [
          this.queryParameter
        ];
    },
      async loadFromApi() {
        this.error = ""; this.loading = true;
        try {
          const result = await OrgUnitService.read(this.orgUnitId);
          this.queryParameter = {
            name: `${result.level}_id`,
            value: result.id
          };
   
          // QueryResult is a json array like [{},{},{}]
          this.internalData = this.QueryResult;
          if(this.internalData.length === 0){
            this.error = "No data available for the selected organizational unit.";
            this.internalCols = [];
            this.chartTitle = "";
            this.page = 1; this.tableSearch = "";
            return;
          }else{
            this.internalCols = Object.keys(this.internalData[0]).map(k => ({ name: k }));
          }
          this.internalCols = [];
          this.chartTitle =  this.chartTitle || "";
          this.page = 1; this.tableSearch = "";
        } catch (e: any) {
          this.error = `API: ${e?.message || e}`;
        } finally {
          this.loading = false;
          this.$nextTick(() => { this.rebuildChart(); this.reflow(); });
        }
      },

      /* ========= Controls ========= */
      async refreshChart() {
        this.loading = true;
        try {
          if (this.mapId) {
            await this.loadFromApi();
          } else {
            this.rebuildChart();
            await this.$nextTick();
            this.reflow();
          }
        } finally {
          this.loading = false;
        }
      },
      rebuildChart() { this.renderKey =  `renderKey${Math.random()}`;},
      toggleFullPage() {
        this.fullPageLocal = !this.fullPageLocal;
        this.$nextTick(() => {

        this.rebuildChart();
        this.reflow()
      });
      },
      reflow() {
        this.computeChartHeight();

        setTimeout(() => {
          this.nudgeWrapperWidth();
        }, 200)
      },
      async nudgeWrapperWidth() {
        const wrap = this.$refs.wrap as HTMLElement | undefined;
        if (!wrap) return;

        // Remember inline styles so we can restore exactly
        const prevWidth = wrap.style.width;
        const prevTransition = wrap.style.transition;

        // Freeze transitions and capture the current pixel width
        wrap.style.transition = 'none';
        const originalPx = `${wrap.getBoundingClientRect().width}px`;

        // Shrink, flush, restore
        wrap.style.width = '10px';
        // Force a reflow so ResizeObserver definitely fires
        void wrap.offsetWidth;

        wrap.style.width = originalPx;

        // Let the DOM paint, then restore styles and trigger an Apex resize
        await this.$nextTick();
        wrap.style.transition = prevTransition;
        // If wrapper didn't previously have an inline width, clear it
        if (prevWidth) wrap.style.width = prevWidth; else wrap.style.removeProperty('width');

        // Finally, update the chart using the real computed width
        this.ensureWidthAfterShow();
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
.chart-wrapper.fullscreen {
  position: fixed;
  inset: 0;
  z-index: 9999;
  border-radius: 0;
}

/* Loading overlay */
.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.6);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 5;
}

.chart-wrapper.dark .loading-overlay {
  background: rgba(0, 0, 0, 0.35);
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid rgba(0, 0, 0, 0.15);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-text {
  margin-top: 8px;
  font-size: 12px;
  font-weight: 600;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* themes */
.chart-wrapper.light {
  background: #fff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.chart-wrapper.light:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.chart-wrapper.dark {
  background: #0f1115;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.5);
}

.chart-wrapper.dark:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6);
}

.chart-wrapper.resizable {
  resize: both;
  overflow: auto;
  min-width: 280px;
  min-height: 220px;
  border: 1px dashed rgba(0, 0, 0, 0.15);
  padding: 8px;
}
.chart-wrapper.panel.p-panel-header {
  display: none !important;
}

/* toolbar */
.p-panel-header {
  display: grid;
  background-color: #0b0e13;
  grid-template-columns: auto auto auto auto auto 1fr auto;
  gap: 12px;
  align-items: center;
  font-size: 13px;
  margin-bottom: 8px;
  padding: 5px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}
.styled-panel.light :deep(.p-panel-header) {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-bottom: 1px solid #cbd5e0;
  padding: 1.25rem 1.5rem;
}

.chart-wrapper.light  .p-panel-header {
  background: #f9fafb;
  color: #374151;
}

.chart-wrapper.dark .p-panel-header {
  background: #111827;
  border-color: #1f2937;
  color: #e5e7eb;
}

.p-panel-header label {
  display: inline-flex;
  gap: 6px;
  align-items: center;
  font-weight: 500;
  margin-left: 10px;
  cursor: pointer;
}
.p-panel-header button {
 margin-left: 20px;
}
.p-panel-header label:first {
 margin-left: 0px;
}
.p-select {
  border:none
}
.p-panel-header select,
.p-panel-header input[type="checkbox"] {
  cursor: pointer;
}

/* inferred dropdown */
.inferred {
  margin-left: auto;
}

.inferred>summary {
  list-style: none;
  cursor: pointer;
  user-select: none;
  padding: 4px 8px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fff;
}

.chart-wrapper.dark .inferred>summary {
  background: #0b0e13;
  border-color: #1f2937;
}

.inferred-body {
  margin-top: 6px;
  font-size: 12px;
  opacity: .85;
}

/* action buttons */
.controls-actions {
  display: inline-flex;
  gap: 8px;
}

.refresh-btn,
.fullscreen-btn {
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  background: #fff;
  cursor: pointer;
  font-weight: 600;
  width: 30px;
  text-align: center;
}

.refresh-btn:disabled {
  opacity: .6;
  cursor: not-allowed;
}

.chart-wrapper.dark .refresh-btn,
.chart-wrapper.dark .fullscreen-btn {
  background: #0b0e13;
  border-color: #1f2937;
  color: #e5e7eb;
}

/* CHART AREA */
.chart-area {
  flex: 1 1 auto;
  display: flex;
  width: 100%;
}

.apexcharts-canvas {
  flex: 1 1 auto;
  width: 100% !important;
}

:deep(.apexcharts-container) {
  width: 100% !important;
}

:deep(.apexcharts-canvas) {
  width: 100% !important;
}

/* TABLE */
.table-area {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.table-title {
  margin: 0 0 4px;
  font-size: 20px;
  font-weight: 700;
  color: #696e7b;
}

.table-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.table-search {
  width: 240px;
  padding: 6px 8px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
}

.rows-count {
  margin-left: auto;
  font-size: 12px;
  opacity: .75;
}

.table-scroll {
  overflow: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.datatable {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 11px;
}

.datatable thead th {
  position: sticky;
  top: 0;
  background: #f3f4f6;
  text-align: left;
  padding: 3px 6px;
  border-bottom: 1px solid #e5e7eb;
  cursor: pointer;
}

.datatable thead th.active {
  color: #111827;
}

.datatable thead th.sortable:hover {
  background: #eef2ff;
}

.sort-indicator {
  margin-left: 6px;
  font-size: 11px;
  opacity: .7;
}

.datatable tbody td {
  padding: 8px 10px;
  border-bottom: 1px solid #f1f5f9;
}

.datatable tbody tr:nth-child(odd) td {
  background: #fafafa;
}

.pager {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: flex-end;
}

.pager button {
  border: 1px solid #e5e7eb;
  background: #fff;
  padding: 4px 10px;
  border-radius: 6px;
  cursor: pointer;
}

.pager button:disabled {
  opacity: .5;
  cursor: not-allowed;
}

.page-size {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

/* generic button look reused for new download buttons */
.btn,
.refresh-btn,
.fullscreen-btn {
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  background: #fff;
  cursor: pointer;
  font-weight: 600;
}

.btn:disabled,
.refresh-btn:disabled {
  opacity: .6;
  cursor: not-allowed;
}

.download-group {
  display: inline-flex;
  gap: 6px;
  float: right;
  margin-right: 6px;
}

.chart-wrapper.dark .btn,
.chart-wrapper.dark .refresh-btn,
.chart-wrapper.dark .fullscreen-btn {
  background: #0b0e13;
  border-color: #1f2937;
  color: #e5e7eb;
}

/* Styling the <select> element */
select {
  width: 100px;
  padding: 2px;
  height: 30px;
  margin-top: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #f8f8f8;
  color: #333;
  font-size: 16px;
}

/* Styling the <option> elements */
option {
  background-color: #fff;
  color: #333;
  padding: 5px;
}

option:hover {
  background-color: #e0e0e0;
}

/* make dropdown a bit compact */
.p-dropdown {
  min-width: 280px;
}


</style>
