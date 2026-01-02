import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { getOrders, createOrder, updateOrderStatus } from '../api/orders';
import { toDisplayMessage, warnIfNotRenderable } from '../utils/toDisplayMessage';
import { cleanFormData } from '../utils/form';
import { getCustomers } from '../api/customers';
import { getProducts } from '../api/products';
import { format } from 'date-fns';

function formatVND(value) {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value);
}

// ... statusLabels and statusColors remain ...

export default function Orders() {
    // ... state ...

    // ... queries ...

    const createMutation = useMutation({
        mutationFn: createOrder,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['orders'] });
            toast.success('Tạo đơn hàng thành công!');
            setIsModalOpen(false);
            setNewOrder({ customer_id: '', line_items: [], discount: 0 });
        },
        onError: (error) => {
            const msg = toDisplayMessage(error);
            warnIfNotRenderable(msg, 'orders.create');
            if (import.meta?.env?.DEV) {
                console.log('[Create order] error payload:', error?.response?.data ?? error);
                console.log('[Create order] display message:', msg);
            }
            toast.error(msg);
        },
    });

    const statusMutation = useMutation({
        mutationFn: ({ id, status }) => updateOrderStatus(id, status),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['orders'] });
            toast.success('Cập nhật trạng thái thành công!');
        },
        onError: (error) => {
            const msg = toDisplayMessage(error);
            warnIfNotRenderable(msg, 'orders.updateStatus');
            toast.error(msg);
        },
    });

    // ... line item helpers ...

    const handleSubmit = (e) => {
        e.preventDefault();

        // Clean the input data first (convert empty strings to null)
        const cleanedOrder = cleanFormData(newOrder);

        if (!cleanedOrder.customer_id) {
            toast.error('Vui lòng chọn khách hàng');
            return;
        }

        if (newOrder.line_items.length === 0) {
            toast.error('Vui lòng thêm ít nhất một sản phẩm');
            return;
        }

        // Validate line items
        for (const item of newOrder.line_items) {
            const quantity = Number(item.quantity);
            const unitPrice = Number(item.unit_price);

            if (!item.product_id) {
                toast.error('Vui lòng chọn sản phẩm cho tất cả các dòng');
                return;
            }
            if (!quantity || quantity <= 0) {
                toast.error(`Số lượng sản phẩm phải lớn hơn 0 (Dòng có giá: ${formatVND(unitPrice)})`);
                return;
            }
        }

        const payload = {
            customer_id: Number(cleanedOrder.customer_id),
            discount: newOrder.discount === '' ? 0 : Number(newOrder.discount),
            line_items: newOrder.line_items.map(item => ({
                product_id: Number(item.product_id),
                quantity: item.quantity === '' ? 0 : Number(item.quantity),
                unit_price: item.unit_price === '' ? 0 : Number(item.unit_price),
                discount: item.discount === '' || item.discount === undefined ? 0 : Number(item.discount)
            }))
        };

        createMutation.mutate(payload);
    };

    const getNextStatus = (currentStatus) => {
        const transitions = {
            draft: ['confirmed', 'cancelled'],
            confirmed: ['shipped', 'cancelled'],
            shipped: ['completed'],
        };
        return transitions[currentStatus] || [];
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Đơn hàng</h1>
                    <p className="text-gray-500">Quản lý đơn hàng bán</p>
                </div>
                <button onClick={() => setIsModalOpen(true)} className="btn-primary">+ Tạo đơn hàng</button>
            </div>

            <div className="card">
                <select
                    value={statusFilter}
                    onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
                    className="form-input max-w-xs"
                >
                    <option value="">Tất cả trạng thái</option>
                    {Object.entries(statusLabels).map(([value, label]) => (
                        <option key={value} value={value}>{label}</option>
                    ))}
                </select>
            </div>

            <div className="card overflow-hidden p-0">
                {isLoading ? (
                    <div className="flex items-center justify-center h-64">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="table-header">Mã đơn</th>
                                    <th className="table-header">Khách hàng</th>
                                    <th className="table-header">Ngày đặt</th>
                                    <th className="table-header text-right">Tổng tiền</th>
                                    <th className="table-header text-right">Còn nợ</th>
                                    <th className="table-header">Trạng thái</th>
                                    <th className="table-header text-right">Thao tác</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {data?.items?.map((order) => (
                                    <tr key={order.id} className="hover:bg-gray-50">
                                        <td className="table-cell font-medium">
                                            <Link to={`/orders/${order.id}`} className="text-primary-600 hover:underline">{order.order_number}</Link>
                                        </td>
                                        <td className="table-cell">{order.customer_name}</td>
                                        <td className="table-cell text-gray-500">{format(new Date(order.order_date), 'dd/MM/yyyy')}</td>
                                        <td className="table-cell text-right font-medium">{formatVND(order.total)}</td>
                                        <td className="table-cell text-right">
                                            <span className={Number(order.remaining_amount) > 0 ? 'text-red-600' : 'text-green-600'}>
                                                {formatVND(order.remaining_amount)}
                                            </span>
                                        </td>
                                        <td className="table-cell">
                                            <span className={statusColors[order.status]}>{statusLabels[order.status]}</span>
                                        </td>
                                        <td className="table-cell text-right">
                                            <div className="flex justify-end gap-1">
                                                {getNextStatus(order.status).map(status => (
                                                    <button
                                                        key={status}
                                                        onClick={() => statusMutation.mutate({ id: order.id, status })}
                                                        className={`text-xs px-2 py-1 rounded ${status === 'cancelled' ? 'bg-red-100 text-red-700' : 'bg-primary-100 text-primary-700'}`}
                                                    >
                                                        {status === 'confirmed' && 'Xác nhận'}
                                                        {status === 'shipped' && 'Giao hàng'}
                                                        {status === 'completed' && 'Hoàn thành'}
                                                        {status === 'cancelled' && 'Hủy'}
                                                    </button>
                                                ))}
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Create Order Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 z-50 overflow-y-auto">
                    <div className="flex min-h-screen items-center justify-center p-4">
                        <div className="fixed inset-0 bg-black/50" onClick={() => setIsModalOpen(false)} />
                        <div className="relative bg-white rounded-xl shadow-xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
                            <h3 className="text-lg font-semibold mb-4">Tạo đơn hàng mới</h3>
                            <form onSubmit={handleSubmit} className="space-y-4">
                                <div>
                                    <label className="form-label">Khách hàng *</label>
                                    <select
                                        value={newOrder.customer_id}
                                        onChange={(e) => setNewOrder(prev => ({ ...prev, customer_id: e.target.value }))}
                                        className="form-input"
                                    >
                                        <option value="">Chọn khách hàng</option>
                                        {customersData?.items?.map(c => (
                                            <option key={c.id} value={c.id}>{c.code} - {c.name}</option>
                                        ))}
                                    </select>
                                </div>

                                <div>
                                    <div className="flex justify-between items-center mb-2">
                                        <label className="form-label mb-0">Sản phẩm</label>
                                        <button type="button" onClick={addLineItem} className="text-sm text-primary-600 hover:text-primary-700">+ Thêm sản phẩm</button>
                                    </div>
                                    <div className="space-y-2">
                                        {newOrder.line_items.map((item, index) => (
                                            <div key={index} className="flex gap-2 items-center">
                                                <select
                                                    value={item.product_id}
                                                    onChange={(e) => updateLineItem(index, 'product_id', e.target.value)}
                                                    className="form-input flex-1"
                                                >
                                                    <option value="">Chọn SP</option>
                                                    {productsData?.items?.map(p => (
                                                        <option key={p.id} value={p.id}>{p.sku} - {p.name}</option>
                                                    ))}
                                                </select>
                                                <input
                                                    type="number"
                                                    value={item.quantity}
                                                    onChange={(e) => updateLineItem(index, 'quantity', e.target.value)}
                                                    className="form-input w-20"
                                                    placeholder="SL"
                                                    min="1"
                                                />
                                                <input
                                                    type="number"
                                                    value={item.unit_price}
                                                    onChange={(e) => updateLineItem(index, 'unit_price', e.target.value)}
                                                    className="form-input w-32"
                                                    placeholder="Đơn giá"
                                                />
                                                <button type="button" onClick={() => removeLineItem(index)} className="text-red-500 hover:text-red-700">✕</button>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div>
                                    <label className="form-label">Giảm giá (VND)</label>
                                    <input
                                        type="number"
                                        value={newOrder.discount}
                                        onChange={(e) => setNewOrder(prev => ({ ...prev, discount: e.target.value }))}
                                        className="form-input max-w-xs"
                                    />
                                </div>

                                <div className="flex justify-end gap-3 pt-4">
                                    <button type="button" onClick={() => setIsModalOpen(false)} className="btn-secondary">Hủy</button>
                                    <button type="submit" className="btn-primary" disabled={createMutation.isPending}>Tạo đơn</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
