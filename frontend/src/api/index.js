import axios from 'axios';

// 创建axios实例
// IMPORTANT: Please replace 'YOUR_LOCAL_IP_ADDRESS' with the actual local IP address of the machine running the backend server.
const api = axios.create({
  baseURL: `http://${window.location.hostname}:7888`,
  timeout: 10000,
  headers: {}
});

console.log('ip地址',window.location.hostname);
console.log('api内容',api)

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data;
  },
  error => {
    console.error('请求错误:', error);
    return Promise.reject(error);
  }
);

export default api;
