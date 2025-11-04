import PrototypeApiService from '@/service/httpService';
function _SettingService() {
    const baseUrl = '/manage/settings';
    const service = new PrototypeApiService(baseUrl);

    service.logoUpload = (file, appId) => {
        const form = new FormData();
        form.append('file', file);
        return service.post(`/logo/upload/${appId}`, form);
    };
    return service;
}

const SettingService = _SettingService();
export default SettingService;
