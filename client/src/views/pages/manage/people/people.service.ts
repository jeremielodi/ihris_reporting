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

    service.documents = new PrototypeApiService('/manage/documents');
    service.documents.upload = (file, typeId, personId, description) => {
        const form = new FormData();
        form.append('file', file);
        form.append('description', description);
        form.append('type_id', typeId);
        return service.documents.post(`/upload/${personId}`, form);
    };
    service.documents.dowloadPdf = async (target, fileName, returnFile) => {
        return service.documents.getPdfStream(target, {});
    };

    service.importList = (orgUnitId, data) => {
        return service.post(`/import/${orgUnitId}`, data);
    };

    service.documents.list = (personId) => {
        return service.documents.get(`/upload/${personId}`);
    };

    return service;
}

const PeopleService =  _PeopleService()
export default PeopleService;
