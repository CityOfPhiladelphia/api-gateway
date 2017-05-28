import axios from 'axios';

export const api = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true,
  validateStatus: function (status) {
    return (status >= 200 && status < 300) ||
           (status >= 400 && status < 500);
  }
});

api.interceptors.request.use((config) => {
  // TODO: add csrf header if method is unsafe
  return config;                 
});

api.interceptors.response.use((response) => {
  // TODO: log errors
  return response;
});

export const checkSession = () => {
  if (!window.localStorage.getItem('csrf_token'))
    return new Promise((resolve, reject) => { resolve(false) });

  return api.get('/session')
  .then((res) => {
    if (res.status == 200 || res.status == 204)
      return true;
    else
      return false;
  });
}
