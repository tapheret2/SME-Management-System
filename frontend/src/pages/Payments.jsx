import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { getPayments, createPayment } from '../api/payments';
import { toDisplayMessage, warnIfNotRenderable } from '../utils/toDisplayMessage';
import { getCustomers } from '../api/customers';
import { getSuppliers } from '../api/suppliers';
import { format } from 'date-fns';

function formatVND(value) {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value);
}

const typeLabels = { incoming: 'Thu', outgoing: 'Chi' };
const methodLabels = { cash: 'Tiền mặt', bank: 'Chuyển khoản', other: 'Khác' };

export default function Payments() {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [activeTab, setActiveTab] = useState('all'); // 'all' | 'receivables' | 'payables'
    const [page, setPage] = useState(1);
    const queryClient = useQueryClient();
    const { register, handleSubmit, reset, watch, formState: { errors } } = useForm();

    const paymentType = watch('type');

    const { data: paymentsData, isLoading } = useQuery({
        queryKey: ['payments', { page }],
        queryFn: () => getPayments({ page, size: 20 }),
        enabled: activeTab === 'all',
    });

    const { data: receivablesData } = useQuery({
        queryKey: ['receivables'],
        queryFn: getReceivables,
        enabled: activeTab === 'receivables',
    });

    const { data: payablesData } = useQuery({
        queryKey: ['payables'],
        queryFn: getPayables,
        enabled: activeTab === 'payables',
    });

    const { data: customersData } = useQuery({
        queryKey: ['customers-select'],
        queryFn: () => getCustomers({ size: 100 }),
    });

    const { data: suppliersData } = useQuery({
        queryKey: ['suppliers-select'],
        queryFn: () => getSuppliers({ size: 100 }),
    });

    const createMutation = useMutation({
        mutationFn: createPayment,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['payments'] });
            queryClient.invalidateQueries({ queryKey: ['receivables'] });
            queryClient.invalidateQueries({ queryKey: ['payables'] });
            toast.success('Tạo phiếu thanh toán thành công!');
            closeModal();
        },
        onError: (error) => {
            const message = toDisplayMessage(error);
            warnIfNotRenderable(message, 'payments.create');
            toast.error(message);
        },
    });

    const openModal = () => {
        reset({ type: 'incoming', method: 'cash', amount: '', customer_id: '', supplier_id: '', notes: '' });
        setIsModalOpen(true);
    };

    const closeModal = () => {
        setIsModalOpen(false);
        reset();
    };

    const onSubmit = (data) => {
        const payload = {
            type: data.type,
            method: data.method,
            amount: Number(data.amount),
            notes: data.notes || undefined,
        };
        if (data.type === 'incoming') {
            payload.customer_id = Number(data.customer_id);
        } else {
            payload.supplier_id = Number(data.supplier_id);
        }
        createMutation.mutate(payload);
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Thanh toán</h1>
                    <p className="text-gray-500">Quản lý thu chi và công nợ</p>
                </div>
                <button onClick={openModal} className="btn-primary">+ Tạo phiếu</button>
            </div>

            {/* Tabs */}
            <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8">
                    {[
                        { id: 'all', label: 'Tất cả' },
                        { id: 'receivables', label: 'Phải thu (AR)' },
                        { id: 'payables', label: 'Phải trả (AP)' },
                    ].map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`py-3 px-1 border-b-2 font-medium text-sm ${activeTab === tab.id
                                ? 'border-primary-500 text-primary-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            {tab.label}
                        </button>
                    ))}
                </nav>
            </div>

            {/* Content based on tab */}
            {activeTab === 'all' && (
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
                                        <th className="table-header">Mã phiếu</th>
                                        <th className="table-header">Loại</th>
                                        <th className="table-header">Đối tượng</th>
                                        <th className="table-header text-right">Số tiền</th>
                                        <th className="table-header">PT thanh toán</th>
                                        <th className="table-header">Ngày</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200">
                                    {paymentsData?.items?.map(payment => (
                                        <tr key={payment.id} className="hover:bg-gray-50">
                                            <td className="table-cell font-medium">{payment.payment_number}</td>
                                            <td className="table-cell">
                                                <span className={`badge ${payment.type === 'incoming' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                                    {typeLabels[payment.type]}
                                                </span>
                                            </td>
                                            <td className="table-cell">{payment.customer_name || payment.supplier_name}</td>
                                            <td className="table-cell text-right font-medium">{formatVND(payment.amount)}</td>
                                            <td className="table-cell text-gray-500">{methodLabels[payment.method]}</td>
                                            <td className="table-cell text-gray-500">{format(new Date(payment.payment_date), 'dd/MM/yyyy')}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'receivables' && (
                <div className="card">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="font-semibold">Công nợ phải thu</h3>
                        <p className="text-lg font-bold text-red-600">{formatVND(receivablesData?.total_receivables || 0)}</p>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="table-header">Mã KH</th>
                                    <th className="table-header">Tên khách hàng</th>
                                    <th className="table-header text-right">Công nợ</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {receivablesData?.items?.map(item => (
                                    <tr key={item.entity_id} className="hover:bg-gray-50">
                                        <td className="table-cell font-medium">{item.entity_code}</td>
                                        <td className="table-cell">{item.entity_name}</td>
                                        <td className="table-cell text-right font-medium text-red-600">{formatVND(item.remaining_amount)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {activeTab === 'payables' && (
                <div className="card">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="font-semibold">Công nợ phải trả</h3>
                        <p className="text-lg font-bold text-orange-600">{formatVND(payablesData?.total_payables || 0)}</p>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="table-header">Mã NCC</th>
                                    <th className="table-header">Tên nhà cung cấp</th>
                                    <th className="table-header text-right">Công nợ</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {payablesData?.items?.map(item => (
                                    <tr key={item.entity_id} className="hover:bg-gray-50">
                                        <td className="table-cell font-medium">{item.entity_code}</td>
                                        <td className="table-cell">{item.entity_name}</td>
                                        <td className="table-cell text-right font-medium text-orange-600">{formatVND(item.remaining_amount)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Create Payment Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 z-50 overflow-y-auto">
                    <div className="flex min-h-screen items-center justify-center p-4">
                        <div className="fixed inset-0 bg-black/50" onClick={closeModal} />
                        <div className="relative bg-white rounded-xl shadow-xl max-w-md w-full p-6">
                            <h3 className="text-lg font-semibold mb-4">Tạo phiếu thanh toán</h3>
                            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                                <div>
                                    <label className="form-label">Loại *</label>
                                    <select {...register('type', { required: true })} className="form-input">
                                        <option value="incoming">Thu (từ khách hàng)</option>
                                        <option value="outgoing">Chi (cho nhà cung cấp)</option>
                                    </select>
                                </div>
                                {paymentType === 'incoming' ? (
                                    <div>
                                        <label className="form-label">Khách hàng *</label>
                                        <select {...register('customer_id', { required: paymentType === 'incoming' })} className="form-input">
                                            <option value="">Chọn khách hàng</option>
                                            {customersData?.items?.map(c => (
                                                <option key={c.id} value={c.id}>{c.code} - {c.name}</option>
                                            ))}
                                        </select>
                                    </div>
                                ) : (
                                    <div>
                                        <label className="form-label">Nhà cung cấp *</label>
                                        <select {...register('supplier_id', { required: paymentType === 'outgoing' })} className="form-input">
                                            <option value="">Chọn nhà cung cấp</option>
                                            {suppliersData?.items?.map(s => (
                                                <option key={s.id} value={s.id}>{s.code} - {s.name}</option>
                                            ))}
                                        </select>
                                    </div>
                                )}
                                <div>
                                    <label className="form-label">Số tiền (VND) *</label>
                                    <input type="number" {...register('amount', { required: true, min: 1 })} className="form-input" />
                                </div>
                                <div>
                                    <label className="form-label">Phương thức</label>
                                    <select {...register('method')} className="form-input">
                                        <option value="cash">Tiền mặt</option>
                                        <option value="bank">Chuyển khoản</option>
                                        <option value="other">Khác</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="form-label">Ghi chú</label>
                                    <textarea {...register('notes')} className="form-input" rows={2} />
                                </div>
                                <div className="flex justify-end gap-3 pt-4">
                                    <button type="button" onClick={closeModal} className="btn-secondary">Hủy</button>
                                    <button type="submit" className="btn-primary" disabled={createMutation.isPending}>Tạo phiếu</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
