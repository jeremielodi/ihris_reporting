
import PrototypeApiService from '@/service/httpService';
function RegionService() {
    const baseUrl = '/manage/regions';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const a = RegionService();
export default a;
