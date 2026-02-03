import PrototypeApiService from '@/service/httpService';

function _StandardService() {
    const baseUrl = '/manage/norm-requirements';
    const service = new PrototypeApiService(baseUrl);
    service.import = (data) => {
        return service.post('/import', data);
    };
    return service;
}

const StandardService = _StandardService();
export default StandardService;
