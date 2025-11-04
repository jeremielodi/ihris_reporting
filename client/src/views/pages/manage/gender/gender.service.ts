
import PrototypeApiService from '@/service/httpService';
function GenderService() {
    const baseUrl = '/manage/genders';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const a = GenderService();
export default a;
