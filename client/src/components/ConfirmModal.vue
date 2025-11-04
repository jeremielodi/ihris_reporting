<script>
import { defineComponent } from 'vue';

export default defineComponent({
    name: 'ConfirmModal',
    props: {
        message: String,
        close: Function,
        display: {
            type: Boolean,
            default: false
        }
    },
    data() {
        return {};
    },
    methods: {
        closeDialog() {
            this.close(false);
        },
        submit() {
            this.close(true);
        }
    }
});
</script>

<template>
    <Dialog v-if="display" :header="$t('FORM.LABELS.CONFIRMATION')" :closable="false" position="top" :style="{ width: '30vw' }" :modal="true" :visible="display" footer="Footer">
        <hr />

        <div class="col-p12">
            {{ $t(message || 'FORM.DIALOGS.CANNOT_UNDONE_ACTION') }}
        </div>

        <template #footer>
            <Button id="cancelButton" :label="$t('FORM.BUTTONS.CANCEL')" @click="closeDialog" class="p-button-text" />
            <Button id="submitButton" type="submit" @click="submit" :label="$t('FORM.BUTTONS.CONFIRM')" />
        </template>
    </Dialog>
</template>
