<script>
import { defineComponent } from 'vue';
import { CodeEditor } from 'monaco-editor-vue3';
import DashboardQueryService from './query.service';
import QueryView from '@/components/QueryView.vue';

export default defineComponent({
    name: 'QueryEditor',
    components: { CodeEditor, QueryView},
    data() {
        return {
            params: {},
            result: [],
            error: null,
            code: '',
            loading: false,
            editorOptions: {
                fontSize: 13,
                minimap: { enabled: false },
                automaticLayout: true
            }
        };
    },
    methods: {
        runQuery() {
            if (this.loading) return;
            this.loading = true;
            DashboardQueryService.run(this.code).then((results) => {
                this.result = results;
                this.error = null;
            }).catch((error) => {
                this.error = error.response?.data?.detail || error.message || 'An error occurred';
                this.result = [];
            }).finally(() => {
                this.loading = false;
            });
        }
    }
});
</script>

<template>
    <div class="card manage-container" style="height: 90vh">
        <div>
            <input type="text" pInputText placeholder="Query Name" style="width: 300px; margin-right: 10px; margin-top: 10px; height: 40px;" />
            <Button :label="$t('FORM.BUTTONS.SAVE')" icon="pi pi-save" style="margin-right: 10px; margin-top: 10px"/>
            <Button @click="runQuery()" :label="$t('FORM.BUTTONS.RUN')" icon="pi pi-play" style="margin-right: 10px; margin-top: 10px"/>
        </div>
       <div class="grid">
            <div class="col-9">
                <CodeEditor v-model:value="code" :options="editorOptions" language="sql" style="height: 400px; width: 100%; padding-top: 20px; border: 1px solid #ccc; border-radius: 4px" />
                <div class="queryResults">
                    {{ error }}
                    <template v-if="result || result.length > 0">
                        <QueryView id="0" :QueryResult="result" display="table"/>
                    </template>
                </div>
            </div>
            <div class="col-3" :class="params ? 'visible' : 'invisible'">
                
            </div>
        </div>
    </div>
</template>
<style scoped>
.queryResults {
    margin-top: 20px; border: 1px solid #ccc; border-radius: 4px; padding: 10px; height: 400px; overflow: auto
}
</style>
