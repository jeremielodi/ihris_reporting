import PrototypeApiService from '@/service/httpService';
function GradeService() {
    const baseUrl = '/manage/grades';
    const service = new PrototypeApiService(baseUrl);
    service.import = (data) => {
        return service.post('/import', data);
    };
    return service;
}

const a = GradeService();
export default a;
