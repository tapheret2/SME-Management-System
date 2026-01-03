import api from './client';

export const getPayments = async (params = {}) => {
    const response = await api.get('/payments', { params });
    return response.data;
};

export const getPayment = async (id) => {
    const response = await api.get(`/payments/${id}`);
    return response.data;
};

export const createPayment = async (data) => {
    const response = await api.post('/payments', data);
    return response.data;
};

export const updatePayment = async (id, data) => {
    const response = await api.put(`/payments/${id}`, data);
    return response.data;
};

export const deletePayment = async (id) => {
    const response = await api.delete(`/payments/${id}`);
    return response.data;
};

export const getARAPSummary = async () => {
    const response = await api.get('/payments/ar-ap');
    return response.data;
};
