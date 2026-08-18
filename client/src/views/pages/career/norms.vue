<script setup>
import NormService from '../manage/standard/norms.service';
import OrgUnitNormChart from '../../../components/OrgUnitNormChart.vue';
import ClassificationService from '../manage/classification/classification.service';
import PyarmidPath from './PyarmidPath.vue';
import { ref } from 'vue';
import { saveAs } from 'file-saver';

const resultTree = ref(null);
const classificationMap = ref({});

// ✅ NEW: filter/search on categories
const categorySearch = ref('');
const loading = ref(false);

const toNumber = (v) => (typeof v === 'number' ? v : Number(v || 0));

// ✅ NEW: full breakdown per structure (requis/présents/besoins/surplus) for a given classification
const getChildrenStats = (orgUnit, classificationId) => {
    const children = orgUnit?.items || [];
    return children
        .map((c) => {
            const required = c?.stat?.required?.[classificationId];
            const actual = c?.stat?.actual?.[classificationId];
            const missing = c?.stat?.missing_total?.[classificationId];
            const excess = c?.stat?.excess?.[classificationId];
            if (required === undefined && actual === undefined && missing === undefined && excess === undefined) return null;
            return {
                id: c.id,
                name: c.name,
                required: toNumber(required),
                actual: toNumber(actual),
                missing: toNumber(missing),
                excess: toNumber(excess)
            };
        })
        .filter(Boolean)
        .sort((a, b) => a.name.localeCompare(b.name));
};
const getChartData = (orgUnit) => {
    const stat = orgUnit?.stat || {};
    const ids = getFilteredClassifications(orgUnit); // respecte le filtre de recherche

    const categories = ids.map((cid) => classificationMap.value?.[cid]?.name || cid);

    const required = ids.map((cid) => Number(stat?.required?.[cid] ?? 0));
    const actual = ids.map((cid) => Number(stat?.actual?.[cid] ?? 0));
    const missing = ids.map((cid) => Number(stat?.missing_total?.[cid] ?? 0));
    const excess = ids.map((cid) => Number(stat?.excess?.[cid] ?? 0));

    return { categories, required, actual, missing, excess };
};

// ✅ NEW: union of classifications keys across required/actual/missing/excess
const getAllClassifications = (stat) => {
    const keys = new Set();
    if (!stat) return [];
    [stat.required, stat.actual, stat.missing_total, stat.excess].forEach((obj) => {
        if (!obj) return;
        Object.keys(obj).forEach((k) => keys.add(k));
    });
    return Array.from(keys);
};

// ✅ NEW: filtered list based on categorySearch
const getFilteredClassifications = (orgUnit) => {
    if (!orgUnit?.stat) return [];

    const allIds = getAllClassifications(orgUnit.stat);

    const q = (categorySearch.value || '').trim().toLowerCase();
    if (!q) return allIds;

    return allIds.filter((cid) => {
        const name = classificationMap.value?.[cid]?.name || cid;
        return name.toLowerCase().includes(q) || String(cid).toLowerCase().includes(q);
    });
};

const onclickGetReport = async (node) => {
    // Load classifications once per reload
    loading.value = true;
    resultTree.value = null;
    const classificationList = await ClassificationService.read();
    const map = {};
    for (const classif of classificationList) {
        map[classif.id] = classif;
    }
    classificationMap.value = map;

    if (node) {
        const nodeId = node.value || node;
        const result = await NormService.getTree(nodeId);
        resultTree.value = result.tree;
    }

    loading.value = false;
};

const treeUpdated = (node) => {
    onclickGetReport(node);
};

// The export endpoint requires authentication, so it must be fetched via
// the API service (which attaches the Bearer token) rather than a plain
// <a href> link, which cannot send custom headers.
const downloadTreeExport = async (orgUnitId) => {
    const blob = await NormService.downloadTreeExport(orgUnitId);
    saveAs(blob, `norms_${orgUnitId}.xlsx`);
};

defineExpose({
    treeUpdated
});
</script>

<template>
    <div>
        <div style="margin-bottom: 10px">
            <PyarmidPath :reload="onclickGetReport" />
        </div>

        <div className="card">
            <h4>{{ $t('FORM.LABELS.NORM_TITLE') }}</h4>



            <!-- ✅ NEW: Search input -->
            <div style="margin-bottom: 10px">
                <input v-model="categorySearch" type="text" :placeholder="$t('FORM.LABELS.NORM_SEARCH_PLACEHOLDER')" style="width: 85%; padding: 6px" />
            </div>

            <div v-if="loading" class="mt-4 pt-4">
                        <ScaleLoader :color="'#3B82F6'"></ScaleLoader>
                        <p class="text-center">{{ $t('FORM.INFO.LOADING') }}</p>
                    </div>

            <template v-if="resultTree">
                <template v-for="orgUnit in resultTree" :key="orgUnit.id">
                    <div style="float: right; margin-top: -35px">
                        <button type="button" class="p-button-success p-button-sm mx-2" @click="downloadTreeExport(orgUnit.id)"> <i class="pi pi-download"></i> {{ $t('FORM.BUTTONS.DOWNLOAD') }} </button>
                    </div>

                   

                    <table style="width: 100%" class="table">
                        <thead>
                            <tr>
                                <th colspan="5">{{ $t('FORM.LABELS.NORM_TITLE') }} - {{ orgUnit.name }}</th>
                            </tr>
                            <tr>
                                <th>{{ $t('FORM.LABELS.NORM_CATEGORY') }}</th>
                                <th align="right">{{ $t('FORM.LABELS.NORM_REQUIRED') }}</th>
                                <th align="right">{{ $t('FORM.LABELS.NORM_PRESENT') }}</th>
                                <th align="right">{{ $t('FORM.LABELS.NORM_NEEDS') }}</th>
                                <th align="right">{{ $t('FORM.LABELS.NORM_SURPLUS') }}</th>
                            </tr>
                        </thead>

                        <template v-if="orgUnit.stat">
                            <template v-for="classificationId in getFilteredClassifications(orgUnit)" :key="classificationId">
                                <tr v-if="orgUnit.stat?.required || orgUnit.stat?.actual">
                                    <td>
                                        {{ classificationMap[classificationId]?.name || classificationId }}
                                    </td>

                                    <td align="right" width="100">
                                        {{ orgUnit.stat?.required?.[classificationId] ?? 0 }}
                                    </td>

                                    <td align="right" width="100">
                                        {{ orgUnit.stat?.actual?.[classificationId] ?? 0 }}
                                    </td>

                                    <td align="right" width="100">
                                        {{ orgUnit.stat?.missing_total?.[classificationId] ?? 0 }}
                                    </td>

                                    <td align="right" width="100">
                                        {{ orgUnit.stat?.excess?.[classificationId] ?? 0 }}
                                    </td>
                                </tr>

                                <!-- Structures directement affichées, avec leurs données -->
                                <tr v-if="getChildrenStats(orgUnit, classificationId).length">
                                    <td colspan="5">
                                        <div class="details-box">
                                            <table class="table sub-table">
                                                <thead>
                                                    <tr>
                                                        <th>{{ $t('FORM.LABELS.NORM_STRUCTURE') }}</th>
                                                        <th align="right">{{ $t('FORM.LABELS.NORM_REQUIRED') }}</th>
                                                        <th align="right">{{ $t('FORM.LABELS.NORM_PRESENT') }}</th>
                                                        <th align="right">{{ $t('FORM.LABELS.NORM_NEEDS') }}</th>
                                                        <th align="right">{{ $t('FORM.LABELS.NORM_SURPLUS') }}</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr v-for="child in getChildrenStats(orgUnit, classificationId)" :key="child.id">
                                                        <td>{{ child.name }}</td>
                                                        <td align="right" width="100">{{ child.required }}</td>
                                                        <td align="right" width="100">{{ child.actual }}</td>
                                                        <td align="right" width="100">{{ child.missing }}</td>
                                                        <td align="right" width="100">{{ child.excess }}</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </td>
                                </tr>
                            </template>

                            <template v-if="getFilteredClassifications(orgUnit).length === 0">
                                <tr>
                                    <td colspan="5">{{ $t('FORM.LABELS.NORM_NO_FILTER_RESULT') }}</td>
                                </tr>
                            </template>
                        </template>

                        <template v-else>
                            <tr>
                                <td colspan="5">{{ $t('FORM.LABELS.NORM_NO_STAT') }}</td>
                            </tr>
                        </template>
                    </table>

                    <br />

                    <div class="card">
                        <OrgUnitNormChart
                        v-if="orgUnit.stat"
                        :title="`${$t('FORM.LABELS.NORM_TITLE')} - ${orgUnit.name}`"
                        :categories="getChartData(orgUnit).categories"
                        :required="getChartData(orgUnit).required"
                        :actual="getChartData(orgUnit).actual"
                        :missing="getChartData(orgUnit).missing"
                        :excess="getChartData(orgUnit).excess"
                    />
                    </div>
                </template>
            </template>
        </div>
    </div>
</template>

<style scoped>
.table {
    border: 1px solid rgb(233, 233, 234);
    background-color: rgb(206, 206, 210);
}

.table td {
    background-color: #fff;
    border: 1px solid rgb(188, 188, 191);
    padding: 3px;
}

.detailBottomLine {
    border-bottom: 1px solid rgb(201, 200, 200) !important;
}

/* Card container */
.card {
    background: #f9fafb;
    border-radius: 8px;
    padding: 12px;
}

/* Table */
.table {
    width: 100%;
    border-collapse: collapse;
    background-color: #ffffff;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

/* Header */
.table thead tr:first-child th {
    background: linear-gradient(90deg, #3b82f6, #2563eb);
    color: #fff;
    font-weight: 600;
    text-align: left;
    padding: 10px;
}

.table thead tr:nth-child(2) th {
    background-color: #e5e7eb;
    color: #374151;
    font-size: 0.85rem;
    text-transform: uppercase;
    padding: 8px;
    border-bottom: 1px solid #d1d5db;
}

/* Body cells */
.table td {
    padding: 8px;
    border-bottom: 1px solid #e5e7eb;
    font-size: 0.9rem;
}

/* Zebra rows */
.table tbody tr:nth-child(even) td {
    background-color: #f9fafb;
}

/* Hover effect */
.table tbody tr:hover td {
    background-color: #eef2ff;
}

/* Category cell (clickable) */
.table td:first-child {
    font-weight: 500;
    color: #1f2937;
}

/* Numeric alignment */
.table td[align='right'] {
    font-variant-numeric: tabular-nums;
    font-weight: 500;
}

/* Required / Actual */
.table td:nth-child(2),
.table td:nth-child(3) {
    color: #374151;
}

/* Missing */
.table td:nth-child(4) {
    color: #b91c1c;
    font-weight: 600;
}

/* Excess */
.table td:nth-child(5) {
    color: #92400e;
    font-weight: 600;
}

/* Clickable category underline */
.table td[style*='cursor'] {
    text-decoration: underline;
    text-decoration-style: dotted;
    text-underline-offset: 3px;
}

.table td[style*='cursor']:hover {
    color: #2563eb;
}

/* Details container */
.detailBottomLine {
    border-bottom: 1px dashed #d1d5db !important;
    padding: 4px 0;
}

/* Details box */
.details-box {
    background: #f8fafc;
    border-left: 4px solid #3b82f6;
    padding: 10px;
    border-radius: 4px;
}

/* Structures directly listed under each category */
.sub-table {
    box-shadow: none;
    margin: 0;
}

.sub-table thead tr th {
    background: #e5e7eb !important;
    color: #374151 !important;
    font-size: 0.78rem;
    text-transform: none !important;
    padding: 6px 8px !important;
}

.sub-table td {
    font-size: 0.85rem;
    padding: 6px 8px !important;
}

/* Section titles inside details */
.details-box h5 {
    margin: 0 0 6px 0;
    font-size: 0.9rem;
    color: #1e40af;
}

/* Search input */
input[type='text'] {
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 8px;
    font-size: 0.9rem;
    outline: none;
}

input[type='text']:focus {
    border-color: #2563eb;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
}
</style>
