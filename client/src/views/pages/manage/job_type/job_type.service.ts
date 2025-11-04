
import PrototypeApiService from '@/service/httpService';
function Job_typeService() {
    const baseUrl = '/manage/job_types';
    const service = new PrototypeApiService(baseUrl);
    service.import = (data) => {
        return service.post('/import', data);
    };
    return service;
}

const a = Job_typeService();
export default a;
