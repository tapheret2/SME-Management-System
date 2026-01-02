import api from './client';

export const getProducts = async (params = {}) => {
    const response = await api.get('/products', { params });
    return response.data;
};

export const getProduct = async (id) => {
    const response = await api.get(`/products/${id}`);
    return response.data;
};

export const createProduct = async (data) => {
    const response = await api.post('/products', data);
    return response.data;
};

export const updateProduct = async (id, data) => {
    const response = await api.put(`/products/${id}`, data);
    return response.data;
};

export const deleteProduct = async (id) => {
    const response = await api.delete(`/products/${id}`);
    return response.data;
};

export const getLowStockProducts = async () => {
    const response = await api.get('/products/low-stock');
    return response.data;
};
