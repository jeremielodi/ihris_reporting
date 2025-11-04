import PrototypeApiService from '@/service/httpService';
function _reportService() {
    const baseUrl = '/manage';
    const service = new PrototypeApiService(baseUrl);
    service.employmentStatus = () => {
        return service.get('/employment_status_report');
    };

    service.generateEmploymentStatus = () => {
        return service.post('/employment_status_report/generate');
    };
    return service;
}

const ReportService = _reportService();
export default ReportService;
