import PrototypeApiService from '@/service/httpService';

function _NormService() {
    const baseUrl = '/manage/norms';
    const service = new PrototypeApiService(baseUrl);
    service.getTree = (orgUnitId: string) => {
        return service.get(`/${orgUnitId}/tree`);
    };
    // Uses the authenticated blob download (sends the Bearer token),
    // unlike a plain <a href> which cannot attach an Authorization header.
    service.downloadTreeExport = (orgUnitId: string) => {
        return service.download(`/${orgUnitId}/tree/export`);
    };

    return service;
}

const NormService = _NormService();
export default NormService;
