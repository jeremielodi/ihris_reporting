
import PrototypeApiService from '@/service/httpService';
function Salary_sourceService() {
    const baseUrl = '/manage/salary_sources';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const a = Salary_sourceService();
export default a;
