import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getAnalytics = async () => {
    const response = await api.get('/api/analytics');
    return response.data;
};

export const getCalls = async (skip = 0, limit = 100) => {
    const response = await api.get(`/api/calls?skip=${skip}&limit=${limit}`);
    return response.data;
};

export const getCall = async (callId) => {
    const response = await api.get(`/api/calls/${callId}`);
    return response.data;
};

export const getCustomers = async (skip = 0, limit = 100) => {
    const response = await api.get(`/api/customers?skip=${skip}&limit=${limit}`);
    return response.data;
};

export const getTickets = async (skip = 0, limit = 100) => {
    const response = await api.get(`/api/tickets?skip=${skip}&limit=${limit}`);
    return response.data;
};

export const getDailyAnalytics = async (days = 7) => {
    const response = await api.get(`/api/analytics/daily?days=${days}`);
    return response.data;
};

export const getIntentAnalytics = async () => {
    const response = await api.get('/api/analytics/intents');
    return response.data;
};

export default api;
