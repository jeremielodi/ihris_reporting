import PrototypeApiService from '@/service/httpService';
function _TimesheetService() {
    const baseUrl = '/manage/timesheets';
    const service = new PrototypeApiService(baseUrl);
    service.person = (personId) => {
        return service.get(`/person/${personId}`);
    };
    return service;
}

const TimesheetService = _TimesheetService();
export default TimesheetService;
