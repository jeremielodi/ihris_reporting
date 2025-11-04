
import PrototypeApiService from '@/service/httpService';
function Institution_typeService() {
    const baseUrl = '/manage/institution_types';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const a = Institution_typeService();
export default a;
