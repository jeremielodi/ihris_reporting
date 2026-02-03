import PrototypeApiService from '@/service/httpService';
function _ClassificationService() {
    const baseUrl = '/manage/classifications';
    const service = new PrototypeApiService(baseUrl);
    service.import = (data) => {
        return service.post('/import', data);
    };
    return service;
}

const ClassificationService = _ClassificationService();
export default ClassificationService;
