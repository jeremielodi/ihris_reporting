import { createStore } from 'vuex';

export default createStore({
    state: {
        currentNode: null,
        blockReportPreview: false,
        socket: null
    },
    mutations: {
        updateCurrentNode(state, nodeId) {
            state.currentNode = nodeId;
        },
        updateblockReportPreview(state, value) {
            console.log(value);
            state.blockReportPreview = !state.blockReportPreview;
        }
    },
    actions: {}
});
