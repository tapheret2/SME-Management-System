import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { getCustomers, createCustomer, updateCustomer, deleteCustomer } from '../api/customers';
import { getErrorMessage } from '../utils/errors';
import { cleanFormData } from '../utils/form';

function formatVND(value) {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value);
}

export default function Customers() {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingItem, setEditingItem] = useState(null);
    const [search, setSearch] = useState('');
    const [page, setPage] = useState(1);
    const queryClient = useQueryClient();

    const { register, handleSubmit, reset, formState: { errors } } = useForm();

    const { data, isLoading } = useQuery({
        queryKey: ['customers', { page, search }],
        queryFn: () => getCustomers({ page, search, size: 20 }),
    });

    const createMutation = useMutation({
        mutationFn: createCustomer,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['customers'] });
            toast.success('Tạo khách hàng thành công!');
            closeModal();
        },
        onError: (error) => toast.error(getErrorMessage(error, 'Không thể tạo khách hàng')),
    });

    const updateMutation = useMutation({
        mutationFn: ({ id, data }) => updateCustomer(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['customers'] });
            toast.success('Cập nhật thành công!');
            closeModal();
        },
        onError: (error) => toast.error(getErrorMessage(error, 'Không thể cập nhật')),
    });

    const deleteMutation = useMutation({
        mutationFn: deleteCustomer,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['customers'] });
            toast.success('Xóa thành công!');
        },
        onError: (error) => toast.error(getErrorMessage(error, 'Không thể xóa')),
    });

    const openModal = (item = null) => {
        setEditingItem(item);
        reset(item || { code: '', name: '', phone: '', email: '', address: '', notes: '' });
        setIsModalOpen(true);
    };

    const closeModal = () => {
        setIsModalOpen(false);
        setEditingItem(null);
        reset();
    };

    const onSubmit = (formData) => {
        const cleanedData = cleanFormData(formData);
        if (editingItem) {
            updateMutation.mutate({ id: editingItem.id, data: cleanedData });
        } else {
            createMutation.mutate(cleanedData);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Khách hàng</h1>
                    <p className="text-gray-500">Quản lý thông tin khách hàng</p>
                </div>
                <button onClick={() => openModal()} className="btn-primary">+ Thêm khách hàng</button>
            </div>

            <div className="card">
                <input
                    type="text"
                    placeholder="Tìm kiếm..."
                    value={search}
                    onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                    className="form-input max-w-md"
                />
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
                                    <th className="table-header">Mã KH</th>
                                    <th className="table-header">Tên khách hàng</th>
                                    <th className="table-header">Điện thoại</th>
                                    <th className="table-header">Email</th>
                                    <th className="table-header text-right">Công nợ</th>
                                    <th className="table-header text-right">Thao tác</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {data?.items?.map((item) => (
                                    <tr key={item.id} className="hover:bg-gray-50">
                                        <td className="table-cell font-medium">{item.code}</td>
                                        <td className="table-cell">{item.name}</td>
                                        <td className="table-cell text-gray-500">{item.phone || '-'}</td>
                                        <td className="table-cell text-gray-500">{item.email || '-'}</td>
                                        <td className="table-cell text-right">
                                            <span className={Number(item.total_debt) > 0 ? 'text-red-600 font-medium' : ''}>
                                                {formatVND(item.total_debt)}
                                            </span>
                                        </td>
                                        <td className="table-cell text-right space-x-2">
                                            <button onClick={() => openModal(item)} className="text-primary-600 hover:text-primary-800">Sửa</button>
                                            <button
                                                onClick={() => { if (confirm('Xác nhận xóa?')) deleteMutation.mutate(item.id); }}
                                                className="text-red-600 hover:text-red-800"
                                            >Xóa</button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {isModalOpen && (
                <div className="fixed inset-0 z-50 overflow-y-auto">
                    <div className="flex min-h-screen items-center justify-center p-4">
                        <div className="fixed inset-0 bg-black/50" onClick={closeModal} />
                        <div className="relative bg-white rounded-xl shadow-xl max-w-lg w-full p-6">
                            <h3 className="text-lg font-semibold mb-4">
                                {editingItem ? 'Sửa khách hàng' : 'Thêm khách hàng mới'}
                            </h3>
                            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="form-label">Mã KH *</label>
                                        <input {...register('code', { required: 'Bắt buộc' })} className="form-input" />
                                        {errors.code && <p className="form-error">{errors.code.message}</p>}
                                    </div>
                                    <div>
                                        <label className="form-label">Điện thoại</label>
                                        <input {...register('phone')} className="form-input" />
                                    </div>
                                </div>
                                <div>
                                    <label className="form-label">Tên khách hàng *</label>
                                    <input {...register('name', { required: 'Bắt buộc' })} className="form-input" />
                                    {errors.name && <p className="form-error">{errors.name.message}</p>}
                                </div>
                                <div>
                                    <label className="form-label">Email</label>
                                    <input type="email" {...register('email')} className="form-input" />
                                </div>
                                <div>
                                    <label className="form-label">Địa chỉ</label>
                                    <textarea {...register('address')} className="form-input" rows={2} />
                                </div>
                                <div>
                                    <label className="form-label">Ghi chú</label>
                                    <textarea {...register('notes')} className="form-input" rows={2} />
                                </div>
                                <div className="flex justify-end gap-3 pt-4">
                                    <button type="button" onClick={closeModal} className="btn-secondary">Hủy</button>
                                    <button type="submit" className="btn-primary" disabled={createMutation.isPending || updateMutation.isPending}>
                                        {editingItem ? 'Cập nhật' : 'Tạo mới'}
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
