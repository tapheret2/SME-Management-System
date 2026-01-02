import api from './client';

export const getSuppliers = async (params = {}) => {
    const response = await api.get('/suppliers', { params });
    return response.data;
};

export const getSupplier = async (id) => {
    const response = await api.get(`/suppliers/${id}`);
    return response.data;
};

export const createSupplier = async (data) => {
    const response = await api.post('/suppliers', data);
    return response.data;
};

export const updateSupplier = async (id, data) => {
    const response = await api.put(`/suppliers/${id}`, data);
    return response.data;
};

export const deleteSupplier = async (id) => {
    const response = await api.delete(`/suppliers/${id}`);
    return response.data;
};
