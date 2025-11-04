import PrototypeApiService from '@/service/httpService';
function CountryService() {
    const baseUrl = '/manage/countries';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const a = CountryService();
export default a;
