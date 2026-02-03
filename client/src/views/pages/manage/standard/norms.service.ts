import PrototypeApiService from '@/service/httpService';

function _NormService() {
    const baseUrl = '/manage/norms';
    const service = new PrototypeApiService(baseUrl);
    service.getTree = (orgUnitId: string) => {
        return service.get(`/${orgUnitId}/tree`);
    };

    return service;
}

const NormService = _NormService();
export default NormService;
