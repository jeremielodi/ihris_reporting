import PrototypeApiService from '@/service/httpService';
function _EmployeeStatusService() {
    const baseUrl = '/manage/employee_status';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const EmployeeStatusService = _EmployeeStatusService();
export default EmployeeStatusService;
