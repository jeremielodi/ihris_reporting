import PrototypeApiService from '@/service/httpService';
function DocumentTypeService() {
    const baseUrl = '/manage/document_types';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const a = DocumentTypeService();
export default a;
