import PrototypeApiService from '@/service/httpService';
function _MaritalStatusService() {
    const baseUrl = '/manage/marital_status';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const MaritalStatusService = _MaritalStatusService();
export default MaritalStatusService;
