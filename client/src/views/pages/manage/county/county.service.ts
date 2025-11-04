
import PrototypeApiService from '@/service/httpService';
function CountyService() {
    const baseUrl = '/manage/counties';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const a = CountyService();
export default a;
