import PrototypeApiService from '@/service/httpService';

function SpecialityService() {
    const baseUrl = '/manage/specialities';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const a = SpecialityService();
export default a;
