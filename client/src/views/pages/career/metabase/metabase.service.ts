import PrototypeApiService from '@/service/httpService';

function _metabase() {
    const baseUrl = '/reports';
    const service = new PrototypeApiService(baseUrl);

    service.getData = (id, data) => {
        return service.post(`/mb_report_question_data/${id}`, data);
    };

    service.getDashboadDetails = (id) => {
        return service.get(`/mb_dashbord_details/${id}`);
    };

    return service;
}

const MetabaseService = _metabase();
export default MetabaseService;
