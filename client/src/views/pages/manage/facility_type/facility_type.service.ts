
import PrototypeApiService from '@/service/httpService';
function Facility_typeService() {
    const baseUrl = '/manage/facility_types';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const a = Facility_typeService();
export default a;
