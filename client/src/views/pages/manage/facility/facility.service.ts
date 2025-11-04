
import PrototypeApiService from '@/service/httpService';
function FacilityService() {
    const baseUrl = '/manage/facilities';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const a = FacilityService();
export default a;
