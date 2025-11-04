import axios from 'axios';
import NProgress from 'nprogress';

let apiService = axios.create({
    //baseURL: 'http://127.0.0.1:8000/',
    baseURL: import.meta.env.VITE_SERVER_URL,
    headers: {
        Authorization: `Bearer ${localStorage.getItem('_ihris_token')}`
    }
});

apiService.interceptors.request.use(
    function (config) {
        // Do something before request is sent
        NProgress.start();
        return config;
    },
    function (error) {
        // Do something with request error
        console.error(error);
        NProgress.done();
        return Promise.reject(error);
    }
);

// Add a response interceptor
apiService.interceptors.response.use(
    function (response) {
        // Do something with response data
        NProgress.done();
        return response;
    },
    function (error) {
        NProgress.done();
        // Do something with response error
        console.error(error);
        if (error.response.status === 401) {
            localStorage.removeItem('_ihris_token');
            //window.location.href = '/#/auth/login';
            setTimeout(() => {
               window.location.reload();
            }, 600);
        }
        return Promise.reject(error);
    }
);

export default apiService;

// const logout = () => {
//     topbarMenuActive.value = !topbarMenuActive.value;
   
//     setTimeout(() => {
//         window.location.reload();
//     }, 600);
// };