import axios from 'axios';

const API_URL = process.env.API_URL || '';

const axiosClient = axios.create({
    baseURL: API_URL,
});

// Request Interceptor for logging
axiosClient.interceptors.request.use((config) => {
    console.log('Request:', config);
    return config;
}, (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
});

// Response Interceptor for logging
axiosClient.interceptors.response.use((response) => {
    console.log('Response:', response);
    return response;
}, (error) => {
    console.error('Response Error:', error);
    return Promise.reject(error);
});

// incidentApi object
export const incidentApi = {
    getIncidents: () => axiosClient.get('/incidents'),
    getIncidentDetail: (id: string) => axiosClient.get(`/incidents/${id}`),
    getStats: () => axiosClient.get('/incidents/stats'),
    ingestSignal: (signalData: any) => axiosClient.post('/incidents/signal', signalData),
};

// resourceApi object
export const resourceApi = {
    getResources: () => axiosClient.get('/resources'),
    getResourceDetail: (id: string) => axiosClient.get(`/resources/${id}`),
    getAvailableCount: () => axiosClient.get('/resources/available/count'),
};
