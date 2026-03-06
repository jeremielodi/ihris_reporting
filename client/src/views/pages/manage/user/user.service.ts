import PrototypeApiService from '@/service/httpService';
function UserService() {
    const baseUrl = '/manage/users';
    const service = new PrototypeApiService(baseUrl);
    service.users = new PrototypeApiService('/users');
    service.auth = (user) => {
        return service.post(`/log/in`, user);
    };

    service.users.login = (user) => {
        return service.users.post(`/reporting/login`, user);
    };

    service.logout = () => {
        return service.get(`/log/out`);
    };

    service.changeSelfPassword = (params) => {
        const url = '/changeSelfPassword';
        return service.post(url, params);
    };
    return service;
}

const a = UserService();
export default a;
