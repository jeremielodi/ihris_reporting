
import PrototypeApiService from '@/service/httpService';
function DistrictService() {
    const baseUrl = '/manage/districts';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const a = DistrictService();
export default a;
