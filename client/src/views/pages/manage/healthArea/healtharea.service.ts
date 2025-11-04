
import PrototypeApiService from '@/service/httpService';
function HealthAreaService() {
    const baseUrl = '/manage/health_areas';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const a = HealthAreaService();
export default a;
