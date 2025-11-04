export default class NotifyService {
    static success(obj, title, description) {
        const msg = description || 'FORM.INFO.OPERATION_SUCCESS';
        obj.$toast.add({
            severity: "success",
            summary: obj.$t(title || ''),
            detail: obj.$t(msg),
            life: 4000,
        });
    }

    static danger(obj, title, description) {
        const msg = description || 'FORM.INFO.OPERATION_FAILED';
        obj.$toast.add({
            severity: "error",
            summary: obj.$t(title || ''),
            detail: obj.$t(msg),
            life:4000,
        });
    }

    static parseErrorMessage(obj, error) {
        if (!error || !error.response) {
            if (error?.code) {
                return obj.$t(`ERROR.${error.code}`);
            }
            return error;
        }
        const code = error.response.data?.code
        const msgCode = obj.$te(`ERROR.${error.response.data?.code}`);
        if (code && msgCode) {
            return obj.$t(`ERROR.${error.response.data?.code}`);
        }
        const msg = obj.$te(`ERROR.${error.response.status}`);
        if (!code && msg) {
            return obj.$t(`ERROR.${error.response.status}`);
        }
        return error.message;
    }
    
    static handleSuccess(obj, msg) {
        if (msg.status === 204) {
            return obj.$toast.add({
                severity: "success",
                summary: obj.$t('SUCCESS.NO_CONTENT'),
                detail: obj.$t('SUCCESS.OPERATION_SUCCESS'),
                life: 6000,
            });
        }
        return obj.$toast.add({
            severity: 'success',
            summary: obj.$t('SUCCESS.OPERATION_SUCCESS'),
            detail: msg?.data?.message || 'Success',
            life: 7000,
        });
    }

    static handleError(obj, error) {
        return obj.$toast.add({
            severity: 'error',
            summary: this.parseErrorMessage(obj, error),
            life: 4000
        });
    }
}