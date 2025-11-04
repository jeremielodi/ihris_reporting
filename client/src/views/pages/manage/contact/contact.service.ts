
import PrototypeApiService from '@/service/httpService';
function _ContactService() {
    const baseUrl = '/manage/contacts';
    const service = new PrototypeApiService(baseUrl);
    service.person = (personId) => {
        return service.get(`/person/${personId}`);
    };
    return service;
}

const ContactService = _ContactService();
export default ContactService;
