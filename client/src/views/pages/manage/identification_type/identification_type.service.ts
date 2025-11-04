
import PrototypeApiService from '@/service/httpService';
function Identification_typeService() {
    const baseUrl = '/manage/identification_types';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const a = Identification_typeService();
export default a;
