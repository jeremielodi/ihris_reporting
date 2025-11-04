
import PrototypeApiService from '@/service/httpService';
function Reason_departureService() {
    const baseUrl = '/manage/reason_departures';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const a = Reason_departureService();
export default a;
