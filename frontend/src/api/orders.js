import api from './client';

export const getOrders = async (params = {}) => {
    const response = await api.get('/orders', { params });
    return response.data;
};

export const getOrder = async (id) => {
    const response = await api.get(`/orders/${id}`);
    return response.data;
};

export const createOrder = async (data) => {
    const response = await api.post('/orders', data);
    return response.data;
};

export const updateOrder = async (id, data) => {
    const response = await api.put(`/orders/${id}`, data);
    return response.data;
};

export const updateOrderStatus = async (id, status) => {
    const response = await api.put(`/orders/${id}/status`, { status });
    return response.data;
};

export const deleteOrder = async (id) => {
    const response = await api.delete(`/orders/${id}`);
    return response.data;
};
