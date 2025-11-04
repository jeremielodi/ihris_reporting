import axios, { AxiosResponse, AxiosRequestConfig, ResponseType } from 'axios';
import NProgress from 'nprogress';
import AppCache from './appCache';

// Helper function to unwrap the HTTP response
function unwrapHttpResponse(response: AxiosResponse): any {
  const hasData = response.data !== undefined && response.data !== null;
  return hasData ? response.data : response;
}

// Centralized 401 error handler
function handleAuthError(error: any): Promise<never> {
  if (error.response?.status === 401) {
    localStorage.removeItem('_ihris_token');
    AppCache.clearSession?.();
    setTimeout(() => {
      window.location.reload();
    }, 600);
  }
  return Promise.reject(error);
}

// Generic HTTP request function
function httpRequest(
  url: string,
  method: string,
  param: Record<string, any> = {},
  responseType?: ResponseType
): Promise<any> {
  const _data = param;

  const cache = AppCache.getSession() || {};
  let token = cache.token;
  if (token === undefined || token === 'undefined' || token === 'null') {
    token = null;
  }

  const finalUrl = `${import.meta.env.VITE_SERVER_URL + url}`.replace(/\/\//g, '/').replace(':/', '://');
  const config: AxiosRequestConfig = {
    url: finalUrl,
    method,
    data: _data,
    headers: token
      ? {
          'x-access-token': cache.token,
          Authorization: `Bearer ${token}`,
        }
      : {},
    responseType,
  };

  NProgress.start();
  return axios(config)
    .then((resp) => {
      NProgress.done();
      return unwrapHttpResponse(resp);
    })
    .catch((error) => {
      NProgress.done();
      return handleAuthError(error);
    });
}

// PDF stream request function
function pdfStreamRequest(url: string, method: string, param: Record<string, any> = {}): Promise<any> {
  const _data = { ...param };
  delete _data.$$hashKey;

  const cache = AppCache.getSession() || {};
  NProgress.start();
  return axios({
    url,
    method,
    data: _data,
    headers: {
      'Content-Type': 'application/json',
      'x-access-token': cache.token,
      Authorization: `Bearer ${cache.token}`,
    },
    responseType: 'arraybuffer',
  })
    .then((resp) => {
      NProgress.done();
      return unwrapHttpResponse(resp);
    })
    .catch((error) => {
      NProgress.done();
      return handleAuthError(error);
    });
}

// HTML stream request function
function HTMLStreamRequest(url: string, method: string, param: Record<string, any> = {}): Promise<any> {
  const _data = { ...param };
  delete _data.$$hashKey;

  const cache = AppCache.getSession() || {};
  NProgress.start();
  return axios({
    url,
    method,
    data: _data,
    headers: {
      'Content-Type': 'application/json',
      'x-access-token': cache.token,
      Authorization: `Bearer ${cache.token}`,
    },
    responseType: 'arraybuffer',
  })
    .then((resp) => {
      NProgress.done();
      return unwrapHttpResponse(resp);
    })
    .catch((error) => {
      NProgress.done();
      return handleAuthError(error);
    });
}

// API service class
export default class Api {
  private server: string;
  private url: string;
  private $http: typeof axios;
  private unwrapHttpResponse: (response: AxiosResponse) => any;

  constructor(url: string) {
    const session = AppCache.getSession() || {};
    if (session.token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${session.token}`;
      axios.defaults.headers.common['x-access-token'] = session.token;
    }
    axios.defaults.baseURL = import.meta.env.VITE_SERVER_URL;
    this.server = import.meta.env.VITE_SERVER_URL;
    this.url = url;
    this.$http = axios;
    this.unwrapHttpResponse = unwrapHttpResponse;
  }

  // Generic request method
  request(url: string, method: string, param: Record<string, any> = {}): Promise<any> {
    return httpRequest(url, method, param);
  }

  // Get token from cache
  getToken(): string | null {
    const cache = AppCache.getSession() || {};
    return cache.token || null;
  }

  // Create resource
  create(param: Record<string, any>): Promise<any> {
    const target = `${this.url}`;
    return this.request(target, 'POST', param);
  }

  // Serialize query parameters
  serelize(params: Record<string, any>): string {
    return Object.entries({ ...params })
      .filter(([key, value]) => key && `${value}` !== 'null')
      .map(([key, value]) => `${key}=${value}`)
      .join('&');
  }

  // Read resource
  read(uuid: string | null, params: Record<string, any> = {}): Promise<any> {
    const req = uuid ? `/${uuid}` : '';
    let target = `${this.url}${req}`;
    if (Object.keys(params || {}).length > 0) {
      target += `?${this.serelize(params || {})}`;
    }
    console.log(target);
    return this.request(target, 'GET', params);
  }

  // Update resource
  update(id: string, param: Record<string, any>): Promise<any> {
    const target = `${this.url}/${id}`;
    return httpRequest(target, 'PUT', param);
  }

  // Delete resource
  delete(id: string): Promise<any> {
    const target = `${this.url}/${id}`;
    return httpRequest(target, 'DELETE', {});
  }

  // GET request
  get(target: string, params: Record<string, any> = {}): Promise<any> {
    return httpRequest(`${this.url}${target}`, 'GET', params);
  }

    // GET request
  download(target: string, params: Record<string, any> = {}): Promise<any> {
    return httpRequest(`${this.url}${target}`, 'GET', params, 'blob');
  }


  // GET PDF stream
  getPdfStream(target: string, params: Record<string, any> = {}): Promise<any> {
    return pdfStreamRequest(`${this.url}${target}`, 'GET', params);
  }

  // GET HTML stream
  getHTMLStream(target: string, params: Record<string, any> = {}): Promise<any> {
    return HTMLStreamRequest(`${this.url}${target}`, 'GET', params);
  }

  // POST request
  post(target: string, param: Record<string, any>): Promise<any> {
    const url = `${this.url}${target}`;
    return this.request(url, 'POST', param);
  }

  // PUT request
  put(target: string, param: Record<string, any>): Promise<any> {
    const url = `${this.url}${target}`;
    return this.request(url, 'PUT', param);
  }
}
