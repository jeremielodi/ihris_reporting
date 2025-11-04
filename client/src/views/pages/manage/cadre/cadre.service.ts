import PrototypeApiService from '@/service/httpService';

function CadreService() {
    const baseUrl = '/manage/cadres';
    const service = new PrototypeApiService(baseUrl);
    service.import = (data) => {
        return service.post('/import', data);
    };
    return service;
}

const a = CadreService();
export default a;
