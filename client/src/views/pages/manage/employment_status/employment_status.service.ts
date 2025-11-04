
import PrototypeApiService from '@/service/httpService';
function employment_statuservice() {
    const baseUrl = '/manage/employment_status';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const a = employment_statuservice();
export default a;
