import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { getPayments, createPayment, deletePayment, getARAPSummary } from '../api/payments';
import { toDisplayMessage } from '../utils/toDisplayMessage';
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
    const [activeTab, setActiveTab] = useState('receivables'); // 'receivables' | 'payables'
    const [page, setPage] = useState(1);
    const queryClient = useQueryClient();
    const { register, handleSubmit, reset, watch, formState: { errors } } = useForm();

    const paymentType = watch('type');

    const { data: paymentsData, isLoading: paymentsLoading } = useQuery({
        queryKey: ['payments', { page }],
        queryFn: () => getPayments({ page, size: 20 }),
        enabled: false, // Disabled as per user request to remove "All" tab
    });

    const { data: arapData } = useQuery({
        queryKey: ['ar-ap-summary'],
        queryFn: getARAPSummary,
        enabled: activeTab === 'receivables' || activeTab === 'payables',
    });

    // Get customers with debt for receivables tab
    const { data: customersWithDebt } = useQuery({
        queryKey: ['customers-with-debt'],
        queryFn: () => getCustomers({ size: 100 }),
        enabled: activeTab === 'receivables',
    });

    // Get suppliers with payable for payables tab
    const { data: suppliersWithPayable } = useQuery({
        queryKey: ['suppliers-with-payable'],
        queryFn: () => getSuppliers({ size: 100 }),
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
            queryClient.invalidateQueries({ queryKey: ['ar-ap-summary'] });
            queryClient.invalidateQueries({ queryKey: ['customers-with-debt'] });
            queryClient.invalidateQueries({ queryKey: ['suppliers-with-payable'] });
            toast.success('Tạo phiếu thanh toán thành công!');
            closeModal();
        },
        onError: (error) => toast.error(toDisplayMessage(error)),
    });

    const deleteMutation = useMutation({
        mutationFn: deletePayment,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['payments'] });
            queryClient.invalidateQueries({ queryKey: ['ar-ap-summary'] });
            queryClient.invalidateQueries({ queryKey: ['customers-with-debt'] });
            queryClient.invalidateQueries({ queryKey: ['suppliers-with-payable'] });
            toast.success('Xóa phiếu thanh toán thành công!');
        },
        onError: (error) => toast.error(toDisplayMessage(error)),
    });

    const openModal = () => {
        reset({ type: 'incoming', method: 'cash', amount: '', customer_id: '', supplier_id: '', is_settlement: false, notes: '' });
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
            is_settlement: data.is_settlement === 'true' || data.is_settlement === true,
            notes: data.notes || undefined,
        };
        if (data.type === 'incoming') {
            payload.customer_id = String(data.customer_id);
        } else {
            payload.supplier_id = String(data.supplier_id);
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


            {activeTab === 'receivables' && (
                <div className="card">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="font-semibold">Công nợ phải thu</h3>
                        <p className="text-lg font-bold text-red-600">{formatVND(arapData?.total_receivables || 0)}</p>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="table-header">Mã ĐT</th>
                                    <th className="table-header">Tên đối tượng</th>
                                    <th className="table-header text-right">Công nợ</th>
                                    <th className="table-header text-right">Thao tác</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {/* Customers with negative debt */}
                                {customersWithDebt?.items?.filter(c => Number(c.total_debt) < 0).map(item => (
                                    <tr key={item.id} className="hover:bg-gray-50">
                                        <td className="table-cell font-medium">{item.code}</td>
                                        <td className="table-cell">{item.name} <span className="text-xs text-gray-400">(KH)</span></td>
                                        <td className="table-cell text-right font-medium text-red-600">{formatVND(item.total_debt)}</td>
                                        <td className="table-cell text-right">
                                            <button
                                                onClick={() => {
                                                    reset({ type: 'incoming', method: 'cash', amount: Math.abs(item.total_debt), customer_id: item.id, supplier_id: '', is_settlement: true, notes: '' });
                                                    setIsModalOpen(true);
                                                }}
                                                className="text-green-600 hover:text-green-800 font-medium"
                                            >Thu tiền</button>
                                        </td>
                                    </tr>
                                ))}
                                {/* Suppliers with negative payable (they owe us) */}
                                {suppliersWithPayable?.items?.filter(s => Number(s.total_payable) < 0).map(item => (
                                    <tr key={item.id} className="hover:bg-gray-50">
                                        <td className="table-cell font-medium">{item.code}</td>
                                        <td className="table-cell">{item.name} <span className="text-xs text-gray-400">(NCC)</span></td>
                                        <td className="table-cell text-right font-medium text-red-600">{formatVND(item.total_payable)}</td>
                                        <td className="table-cell text-right">
                                            <button
                                                onClick={() => {
                                                    reset({ type: 'incoming', method: 'cash', amount: Math.abs(item.total_payable), customer_id: '', supplier_id: item.id, is_settlement: true, notes: '' });
                                                    setIsModalOpen(true);
                                                }}
                                                className="text-green-600 hover:text-green-800 font-medium"
                                            >Thu tiền</button>
                                        </td>
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
                        <p className="text-lg font-bold text-orange-600">{formatVND(arapData?.total_payables || 0)}</p>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="table-header">Mã ĐT</th>
                                    <th className="table-header">Tên đối tượng</th>
                                    <th className="table-header text-right">Công nợ</th>
                                    <th className="table-header text-right">Thao tác</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {/* Suppliers with positive payable */}
                                {suppliersWithPayable?.items?.filter(s => Number(s.total_payable) > 0).map(item => (
                                    <tr key={item.id} className="hover:bg-gray-50">
                                        <td className="table-cell font-medium">{item.code}</td>
                                        <td className="table-cell">{item.name} <span className="text-xs text-gray-400">(NCC)</span></td>
                                        <td className="table-cell text-right font-medium text-orange-600">{formatVND(item.total_payable)}</td>
                                        <td className="table-cell text-right">
                                            <button
                                                onClick={() => {
                                                    reset({ type: 'outgoing', method: 'cash', amount: Math.abs(item.total_payable), customer_id: '', supplier_id: item.id, is_settlement: true, notes: '' });
                                                    setIsModalOpen(true);
                                                }}
                                                className="text-blue-600 hover:text-blue-800 font-medium"
                                            >Thanh toán</button>
                                        </td>
                                    </tr>
                                ))}
                                {/* Customers with positive debt (we owe them / prepayment) */}
                                {customersWithDebt?.items?.filter(c => Number(c.total_debt) > 0).map(item => (
                                    <tr key={item.id} className="hover:bg-gray-50">
                                        <td className="table-cell font-medium">{item.code}</td>
                                        <td className="table-cell">{item.name} <span className="text-xs text-gray-400">(KH)</span></td>
                                        <td className="table-cell text-right font-medium text-orange-600">{formatVND(item.total_debt)}</td>
                                        <td className="table-cell text-right">
                                            <button
                                                onClick={() => {
                                                    reset({ type: 'outgoing', method: 'cash', amount: Math.abs(item.total_debt), customer_id: item.id, supplier_id: '', is_settlement: true, notes: '' });
                                                    setIsModalOpen(true);
                                                }}
                                                className="text-blue-600 hover:text-blue-800 font-medium"
                                            >Thanh toán</button>
                                        </td>
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
                            <h3 className="text-lg font-semibold mb-4">
                                {paymentType === 'incoming' ? 'Ghi nhận thu tiền' : 'Ghi nhận chi tiền'}
                            </h3>
                            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                                <div>
                                    <label className="form-label">Loại *</label>
                                    <select {...register('type', { required: true })} className="form-input">
                                        <option value="incoming">Phiếu Thu (Khách hàng)</option>
                                        <option value="outgoing">Phiếu Chi (Nhà cung cấp)</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="form-label">Nghiệp vụ *</label>
                                    <select {...register('is_settlement', { required: true })} className="form-input">
                                        <option value="false">Ghi nợ (Tạo khoản nợ mới)</option>
                                        <option value="true">Tất toán (Thu/Trả tiền nợ)</option>
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
                                    <button type="submit" className="btn-primary" disabled={createMutation.isPending}>
                                        {paymentType === 'incoming' ? 'Lưu phiếu thu' : 'Lưu phiếu chi'}
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
