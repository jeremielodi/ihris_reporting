import PrototypeApiService from '@/service/httpService';

function _JobTitleService() {
    const baseUrl = '/manage/job_titles';
    const service = new PrototypeApiService(baseUrl);
    return service;
}

const JobTitleService = _JobTitleService();
export default JobTitleService;
