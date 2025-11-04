
import PrototypeApiService from '@/service/httpService';
function Payment_frequencyService() {
    const baseUrl = '/manage/payment_frequencies';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const a = Payment_frequencyService();
export default a;
