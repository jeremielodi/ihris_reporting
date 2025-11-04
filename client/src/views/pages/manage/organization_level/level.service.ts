import PrototypeApiService from '@/service/httpService';
function _OrgLevelService() {
    const baseUrl = '/manage/organization_levels';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const OrgLevelService = _OrgLevelService();
export default OrgLevelService;
