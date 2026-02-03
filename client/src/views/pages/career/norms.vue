<script setup>
import NormService from '../manage/standard/norms.service';
import ClassificationService from '../manage/classification/classification.service';
import PyarmidPath from './PyarmidPath.vue';
import { ref } from 'vue';
const resultTree = ref(null);
const classificationMap = ref({});

const toNumber = (v) => (typeof v === 'number' ? v : Number(v || 0));

const getChildrenWithValue = (orgUnit, type, classificationId) => {
    // type = "missing_total" ou "excess"
    const children = orgUnit?.items || [];
    return children
        .map((c) => {
            const val = toNumber(c?.stat?.[type]?.[classificationId]);
            return val > 0 ? { ...c, _val: val } : null;
        })
        .filter(Boolean)
        .sort((a, b) => b._val - a._val);
};

const getAllClassifications = (stat) => {
    const keys = new Set();
    if (!stat) return [];
    [stat.required, stat.actual, stat.missing_total, stat.excess].forEach((obj) => {
        if (!obj) return;
        Object.keys(obj).forEach((k) => keys.add(k));
    });
    return Array.from(keys);
};

// Optionnel: petit toggle par classification pour afficher/cacher la liste
const opened = ref({}); // key: `${orgUnit.id}|${type}|${classificationId}` -> bool
const toggleDetails = (orgUnitId, type, classificationId) => {
    const key = `${orgUnitId}|${type}|${classificationId}`;
    opened.value[key] = !opened.value[key];
};
const isOpen = (orgUnitId, type, classificationId) => !!opened.value[`${orgUnitId}|${type}|${classificationId}`];

const onclickGetReport = async (node) => {
    const classificationList = await ClassificationService.read();
    for (const classif of classificationList) {
        classificationMap.value[classif.id] = classif;
    }
    if (node) {
        let nodeId = node.value || node;
        NormService.getTree(nodeId).then((result) => {
            resultTree.value = result.tree;
        });
    }
};

const treeUpdated = (node) => {
    onclickGetReport(node);
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
            <h4>Normes</h4>
           
            <template v-if="resultTree">
                <template v-for="orgUnit in resultTree" :key="orgUnit.id">
                     <div style="float: right;">
                                    <a target="_blank" :href="NormService.server + `manage/norms/${orgUnit.id}/tree/export`">Télécharger</a>
                     </div>

                    <table style="width: 100%" class="table">
                        <thead>
                            <tr>
                                <th colspan="4">NORMES - {{ orgUnit.name }}</th>
                                
                            </tr>
                            <tr>
                                <th>CATEGORIE</th>
                                <th align="right">REQUIS</th>
                                <th align="right">ACTIFS</th>
                                <th align="right">CARENCE</th>
                                <th align="right">PLETORE</th>
                            </tr>
                        </thead>

                        <template v-if="orgUnit.stat">
                            <template v-for="classificationId in getAllClassifications(orgUnit.stat)" :key="classificationId">
                                <tr>
                                    <!-- click on category name -->
                                    <td style="cursor: pointer; text-decoration: underline" @click="orgUnit.items.length > 0 ? toggleDetails(orgUnit.id, 'mix', classificationId) : () => {}">
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

                                <!-- Details row -->
                                <tr v-if="isOpen(orgUnit.id, 'mix', classificationId)">
                                    <td colspan="5">
                                        <div style="padding: 8px; background: #fff">
                                            <!-- Missing details -->
                                            <template v-if="(orgUnit.stat?.missing_total?.[classificationId] ?? 0) > 0">
                                                <div style="margin-bottom: 10px">
                                                    <b>Structures manquant les <span class="text-primary">{{ classificationMap[classificationId]?.name }}</span>:</b>
                                                    <template v-if="getChildrenWithValue(orgUnit, 'missing_total', classificationId).length">
                                                        <div
                                                            v-for="child in getChildrenWithValue(orgUnit, 'missing_total', classificationId)"
                                                            :key="child.id + '_m'"
                                                            class="detailBottomLine"
                                                            style="display: flex; justify-content: space-between; padding: 2px 0"
                                                        >
                                                            <span>{{ child.name }}</span>
                                                            <b>{{ child._val }}</b>
                                                        </div>
                                                    </template>
                                                    <template v-else>
                                                        <div>Aucun item avec manque pour cette catégorie.</div>
                                                    </template>
                                                </div>
                                            </template>

                                            <!-- Excess details -->
                                            <template v-if="(orgUnit.stat?.excess?.[classificationId] ?? 0) > 0">
                                                <div>
                                                    <b>Structures ayant plus des <span class="text-primary">{{ classificationMap[classificationId]?.name }}</span> :</b>
                                                    <template v-if="getChildrenWithValue(orgUnit, 'excess', classificationId).length">
                                                        <div
                                                            v-for="child in getChildrenWithValue(orgUnit, 'excess', classificationId)"
                                                            :key="child.id + '_e'"
                                                            class="detailBottomLine"
                                                            style="display: flex; justify-content: space-between; padding: 2px 0"
                                                        >
                                                            <span>{{ child.name }}</span>
                                                            <b>{{ child._val }}</b>
                                                        </div>
                                                    </template>
                                                    <template v-else>
                                                        <div>Aucune structure avec excès pour cette catégorie.</div>
                                                    </template>
                                                </div>
                                            </template>

                                            <!-- If neither missing nor excess -->
                                            <template v-if="(orgUnit.stat?.missing_total?.[classificationId] ?? 0) === 0 && (orgUnit.stat?.excess?.[classificationId] ?? 0) === 0">
                                                <div>Aucun manque ni excès pour cette catégorie.</div>
                                            </template>
                                        </div>
                                    </td>
                                </tr>
                            </template>

                            <template v-if="getAllClassifications(orgUnit.stat).length === 0">
                                <tr>
                                    <td colspan="5">Aucune donnée disponible.</td>
                                </tr>
                            </template>
                        </template>

                        <template v-else>
                            <tr>
                                <td colspan="5">Aucune statistique disponible.</td>
                            </tr>
                        </template>
                    </table>

                    <br />
                </template>
            </template>
        </div>
    </div>
</template>

<style scoped>
.table {
    border: 1px solid rgb(233, 233, 234);
    background-color: rgb(238, 238, 240);
}

.table td {
    background-color: #fff;
    padding: 3px;
}
.detailBottomLine {
    border-bottom: 1px solid rgb(201, 200, 200) !important;
}
</style>
