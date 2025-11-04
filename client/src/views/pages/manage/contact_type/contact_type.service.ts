
import PrototypeApiService from '@/service/httpService';
function _Contact_typeService() {
    const baseUrl = '/manage/contact_types';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const ContactTypeService = _Contact_typeService();
export default ContactTypeService;
