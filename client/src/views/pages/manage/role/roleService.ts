import PrototypeApiService from '@/service/httpService';
function _RoleService() {
    const baseUrl = '/manage/roles';
    const service = new PrototypeApiService(baseUrl);

    service.loadModules = (roleId) => {
        return service.get(`/modulesForRole/${roleId}`);
    };

    service.userRoles = (userId) => {
        return service.get(`/userRoles/${userId}`);
    };

    service.userAddRoles = (data) => {
        return service.post(`/assignRoles`, data);
    };

    service.affectPages = (data) => {
        return service.post(`/affectPages`, data);
    };

    service.loadUserModules = (userId) =>{
        return service.get(`/userModules/${userId}`);
    };
    service.pageInfos = (pageCode) => {
        return service.get(`/pageInfos/${pageCode}`);
    };

    service.actions = (roleUuid) => {
        const url = `/actions/${roleUuid}`;
        return service.get(url);
    };

    service.assignActions = (data) => {
        const url = `/actions`;
        return service.post(url, data);
    };

    service.userHasAction = (actionId) => {
        const url = `/actions/user/${actionId}`;
        return service.get(url);
    };

    return service;
}

const RoleService = _RoleService();
export default RoleService;
