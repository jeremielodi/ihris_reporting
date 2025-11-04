import PrototypeApiService from '@/service/httpService';
function DashboardService() {
    const baseUrl = '/manage/dashboards';
    const service = new PrototypeApiService(baseUrl);

    service.role = (roleId) => {
        return service.get(`/role/${roleId}`);
    };
    service.assigned = () => {
        return service.get(`/user/assinged`);
    };

    service.assignToRole =  (data) => {
        return service.post(`/role`, data);
    };
    return service;
}

const DashboardManageService = DashboardService();
export default DashboardManageService;
