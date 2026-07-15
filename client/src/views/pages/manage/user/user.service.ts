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

    // Revokes the refresh token server-side (best-effort; UI logout does
    // not need to wait on this before clearing local session state).
    service.users.reportingLogout = (refreshToken) => {
        return service.users.post(`/reporting/logout`, { refresh_token: refreshToken });
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
