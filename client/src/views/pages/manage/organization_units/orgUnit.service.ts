import PrototypeApiService from '@/service/httpService';

function _OrgUnitService() {
    const baseUrl = '/manage/organization_units';
    const service = new PrototypeApiService(baseUrl);

    service.children = (parentId) => {
        return service.get(`/children/${parentId}`);
    };

    service.tree = (parentId) => {
        return service.get(`/tree/${parentId}`);
    };

    service.path = (orgId) => {
        return service.get(`/path/${orgId}`);
    };

    service.import = (data) => {
        return service.post(`/import/json`, data);
    };

    service.downloadAsXLSX = () => {
        return service.download(`/export/xlsx`);
    };

    return service;
}

const OrgUnitService = _OrgUnitService();
export default OrgUnitService;
