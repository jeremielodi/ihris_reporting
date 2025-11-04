import PrototypeApiService from '@/service/httpService';
function ClassificationService() {
    const baseUrl = '/manage/classifications';
    const service = new PrototypeApiService(baseUrl);
    service.import = (data) => {
        return service.post('/import', data);
    };
    return service;
}

const a = ClassificationService();
export default a;
