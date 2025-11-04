import PrototypeApiService from '@/service/httpService';
function MaritalStatusService() {
    const baseUrl = '/manage/marital_status';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const a = MaritalStatusService();
export default a;
