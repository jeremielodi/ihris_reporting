import PrototypeApiService from '@/service/httpService';
function DegreeService() {
    const baseUrl = '/manage/degrees';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const a = DegreeService();
export default a;
