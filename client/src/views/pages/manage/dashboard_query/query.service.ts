import PrototypeApiService from '@/service/httpService';

function _service() {
    const baseUrl = '/manage/dashboard_queries';
    const service = new PrototypeApiService(baseUrl);
    service.forDashboard = (dashboardUuid: string) => {
        return service.get(`/for/${dashboardUuid}`);
    };
    service.run = (sql) => {
        return service.post(`/run`, {sql});
    };
    return service;
}

const DashboardQueryService = _service();
export default DashboardQueryService;
