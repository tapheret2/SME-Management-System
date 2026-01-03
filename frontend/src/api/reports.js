import api from './client';

export const getDashboardMetrics = async () => {
    const response = await api.get('/reports/dashboard');
    return response.data;
};

export const getRevenueReport = async (params = {}) => {
    const response = await api.get('/reports/revenue', { params });
    return response.data;
};

export const getTopProducts = async (params = {}) => {
    const response = await api.get('/reports/top-products', { params });
    return response.data;
};

export const getInventoryValuation = async () => {
    const response = await api.get('/reports/inventory-valuation');
    return response.data;
};

export const getARAPSummary = async () => {
    const response = await api.get('/payments/ar-ap');
    return response.data;
};

// Export functions
export const exportProducts = () => {
    window.open(`${api.defaults.baseURL}/export/products`, '_blank');
};

export const exportOrders = (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    window.open(`${api.defaults.baseURL}/export/orders?${queryString}`, '_blank');
};

export const exportPayments = (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    window.open(`${api.defaults.baseURL}/export/payments?${queryString}`, '_blank');
};
