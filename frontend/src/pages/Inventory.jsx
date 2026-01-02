import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import api from '../api/client';
import { getProducts, getLowStockProducts } from '../api/products';
import { toDisplayMessage } from '../utils/toDisplayMessage';

function formatVND(value) {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value);
}

export default function Inventory() {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [modalType, setModalType] = useState('in'); // 'in' | 'out' | 'adjust'
    const [formData, setFormData] = useState({ product_id: '', quantity: 0, supplier_id: '', reason: '' });
    const queryClient = useQueryClient();

    const { data: productsData } = useQuery({
        queryKey: ['products-inventory'],
        queryFn: () => getProducts({ size: 100, active_only: true }),
    });

    const { data: lowStockProducts } = useQuery({
        queryKey: ['low-stock-products'],
        queryFn: getLowStockProducts,
    });

    const { data: movementsData } = useQuery({
        queryKey: ['stock-movements'],
        queryFn: async () => {
            const response = await api.get('/stock', { params: { size: 20 } });
            return response.data;
        },
    });

    const stockMutation = useMutation({
        mutationFn: async (data) => {
            const endpoint = `/stock/${modalType}`;
            const response = await api.post(endpoint, data);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['products-inventory'] });
            queryClient.invalidateQueries({ queryKey: ['low-stock-products'] });
            queryClient.invalidateQueries({ queryKey: ['stock-movements'] });
            toast.success('Cập nhật tồn kho thành công!');
            closeModal();
        },
        onError: (error) => toast.error(toDisplayMessage(error)),
    });

    const openModal = (type) => {
        setModalType(type);
        setFormData({ product_id: '', quantity: 0, supplier_id: '', reason: '' });
        setIsModalOpen(true);
    };

    const closeModal = () => {
        setIsModalOpen(false);
        setFormData({ product_id: '', quantity: 0, supplier_id: '', reason: '' });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        const payload = {
            product_id: Number(formData.product_id),
            quantity: Number(formData.quantity),
            reason: formData.reason || undefined,
        };
        if (modalType === 'in' && formData.supplier_id) {
            payload.supplier_id = Number(formData.supplier_id);
        }
        stockMutation.mutate(payload);
    };

    const typeLabels = { in: 'Nhập', out: 'Xuất', adjust: 'Điều chỉnh' };
    const typeColors = {
        in: 'bg-green-100 text-green-800',
        out: 'bg-red-100 text-red-800',
        adjust: 'bg-yellow-100 text-yellow-800',
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Tồn kho</h1>
                    <p className="text-gray-500">Quản lý xuất nhập kho</p>
                </div>
                <div className="flex gap-2">
                    <button onClick={() => openModal('in')} className="btn-success">+ Nhập kho</button>
                    <button onClick={() => openModal('out')} className="btn-danger">- Xuất kho</button>
                    <button onClick={() => openModal('adjust')} className="btn-secondary">Điều chỉnh</button>
                </div>
            </div>

            {/* Low Stock Alert */}
            {lowStockProducts && lowStockProducts.length > 0 && (
                <div className="card bg-red-50 border-red-200">
                    <h3 className="font-semibold text-red-800 mb-2">⚠️ Cảnh báo tồn kho thấp</h3>
                    <p className="text-sm text-red-700 mb-3">{lowStockProducts.length} sản phẩm có tồn kho dưới mức tối thiểu</p>
                    <div className="flex flex-wrap gap-2">
                        {lowStockProducts.slice(0, 5).map(p => (
                            <span key={p.id} className="badge bg-red-100 text-red-800">
                                {p.sku}: {p.current_stock}/{p.min_stock}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Products Stock */}
                <div className="card overflow-hidden p-0">
                    <div className="px-6 py-4 border-b bg-gray-50">
                        <h3 className="font-semibold">Tồn kho hiện tại</h3>
                    </div>
                    <div className="overflow-x-auto max-h-96">
                        <table className="min-w-full">
                            <thead className="bg-gray-50 sticky top-0">
                                <tr>
                                    <th className="table-header">SKU</th>
                                    <th className="table-header">Sản phẩm</th>
                                    <th className="table-header text-right">Tồn kho</th>
                                    <th className="table-header text-right">Giá trị</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {productsData?.items?.map(product => (
                                    <tr key={product.id} className={product.is_low_stock ? 'bg-red-50' : ''}>
                                        <td className="table-cell font-medium">{product.sku}</td>
                                        <td className="table-cell">{product.name}</td>
                                        <td className="table-cell text-right">
                                            <span className={product.is_low_stock ? 'text-red-600 font-medium' : ''}>
                                                {product.current_stock}
                                            </span>
                                        </td>
                                        <td className="table-cell text-right text-gray-500">
                                            {formatVND(product.current_stock * product.cost_price)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Recent Movements */}
                <div className="card overflow-hidden p-0">
                    <div className="px-6 py-4 border-b bg-gray-50">
                        <h3 className="font-semibold">Phiếu xuất nhập gần đây</h3>
                    </div>
                    <div className="overflow-x-auto max-h-96">
                        <table className="min-w-full">
                            <thead className="bg-gray-50 sticky top-0">
                                <tr>
                                    <th className="table-header">Loại</th>
                                    <th className="table-header">Sản phẩm</th>
                                    <th className="table-header text-right">SL</th>
                                    <th className="table-header text-right">Sau</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {movementsData?.items?.map(m => (
                                    <tr key={m.id}>
                                        <td className="table-cell">
                                            <span className={`badge ${typeColors[m.type]}`}>{typeLabels[m.type]}</span>
                                        </td>
                                        <td className="table-cell">{m.product_name}</td>
                                        <td className="table-cell text-right font-medium">
                                            {m.type === 'out' ? '-' : m.quantity > 0 ? '+' : ''}{m.quantity}
                                        </td>
                                        <td className="table-cell text-right">{m.stock_after}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Stock Movement Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 z-50 overflow-y-auto">
                    <div className="flex min-h-screen items-center justify-center p-4">
                        <div className="fixed inset-0 bg-black/50" onClick={closeModal} />
                        <div className="relative bg-white rounded-xl shadow-xl max-w-md w-full p-6">
                            <h3 className="text-lg font-semibold mb-4">
                                {modalType === 'in' && 'Nhập kho'}
                                {modalType === 'out' && 'Xuất kho'}
                                {modalType === 'adjust' && 'Điều chỉnh tồn kho'}
                            </h3>
                            <form onSubmit={handleSubmit} className="space-y-4">
                                <div>
                                    <label className="form-label">Sản phẩm *</label>
                                    <select
                                        value={formData.product_id}
                                        onChange={(e) => setFormData(prev => ({ ...prev, product_id: e.target.value }))}
                                        className="form-input"
                                        required
                                    >
                                        <option value="">Chọn sản phẩm</option>
                                        {productsData?.items?.map(p => (
                                            <option key={p.id} value={p.id}>{p.sku} - {p.name} (Tồn: {p.current_stock})</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="form-label">
                                        Số lượng {modalType === 'adjust' ? '(âm để giảm)' : ''} *
                                    </label>
                                    <input
                                        type="number"
                                        value={formData.quantity}
                                        onChange={(e) => setFormData(prev => ({ ...prev, quantity: e.target.value }))}
                                        className="form-input"
                                        min={modalType === 'adjust' ? undefined : 1}
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="form-label">Lý do {modalType === 'adjust' ? '*' : ''}</label>
                                    <input
                                        value={formData.reason}
                                        onChange={(e) => setFormData(prev => ({ ...prev, reason: e.target.value }))}
                                        className="form-input"
                                        required={modalType === 'adjust'}
                                    />
                                </div>
                                <div className="flex justify-end gap-3 pt-4">
                                    <button type="button" onClick={closeModal} className="btn-secondary">Hủy</button>
                                    <button type="submit" className="btn-primary" disabled={stockMutation.isPending}>Lưu</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
