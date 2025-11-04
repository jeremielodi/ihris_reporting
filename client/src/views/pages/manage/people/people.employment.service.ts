import PrototypeApiService from '@/service/httpService';
function _EmploymentInfoService() {
    const baseUrl = '/manage/employment_status_infos';
    const service = new PrototypeApiService(baseUrl);
    service.person = (personId) => {
        return service.get(`/person/${personId}`);
    };
    return service;
}
const EmploymentInfoService = _EmploymentInfoService();
export default EmploymentInfoService;
