
import PrototypeApiService from '@/service/httpService';
function Educational_levelService() {
    const baseUrl = '/manage/educational_levels';
    const service = new PrototypeApiService(baseUrl);
    service.import = (data) => {
        return service.post('/import', data);
    };
    return service;
}

const a = Educational_levelService();
export default a;
