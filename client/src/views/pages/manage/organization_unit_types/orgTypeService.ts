import PrototypeApiService from '@/service/httpService';
function _OrgUnitTypeService() {
    const baseUrl = '/manage/organization_unit_types';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const OrgUnitTypeService = _OrgUnitTypeService();
export default OrgUnitTypeService;
