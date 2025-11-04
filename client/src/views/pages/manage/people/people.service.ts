import PrototypeApiService from '@/service/httpService';
function _PeopleService() {
    const baseUrl = '/manage/people';
    const service = new PrototypeApiService(baseUrl);
    service.passport = new PrototypeApiService('/manage/passport');
    service.passport.upload = (file, personId) => {
        const form = new FormData();
        form.append('file', file);
        return service.passport.post(`/upload/${personId}`, form);
    };

    service.passport.list = (personId) => {
        return service.passport.get(`/upload/${personId}`);
    };
    return service;
}

const PeopleService =  _PeopleService()
export default PeopleService;
