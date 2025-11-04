import PrototypeApiService from '@/service/httpService';
function _IdentificationService() {
    const baseUrl = '/manage/identifications';
    const service = new PrototypeApiService(baseUrl);
    service.person = (personId) => {
        return service.get(`/person/${personId}`);
    };
    return service;
}

const IdentificationService = _IdentificationService();
export default IdentificationService;
