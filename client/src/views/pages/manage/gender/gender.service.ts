import PrototypeApiService from '@/service/httpService';
function _GenderService() {
    const baseUrl = '/manage/genders';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const GenderService = _GenderService();
export default GenderService;
