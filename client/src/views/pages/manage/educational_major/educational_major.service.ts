import PrototypeApiService from '@/service/httpService';

function Education_majourService() {
    const baseUrl = '/manage/educational_majors';
    const service = new PrototypeApiService(baseUrl);
    service.import = (data) => {
        return service.post('/import', data);
    };
    return service;
}

const a = Education_majourService();
export default a;
