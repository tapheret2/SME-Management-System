import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { getProducts, createProduct, updateProduct, deleteProduct } from '../api/products';
import { toDisplayMessage, warnIfNotRenderable } from '../utils/toDisplayMessage';
import { cleanFormData } from '../utils/form';

function formatVND(value) {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value);
}

export default function Products() {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingProduct, setEditingProduct] = useState(null);
    const [search, setSearch] = useState('');
    const [page, setPage] = useState(1);
    const queryClient = useQueryClient();

    const { register, handleSubmit, reset, formState: { errors } } = useForm();

    const { data, isLoading } = useQuery({
        queryKey: ['products', { page, search }],
        queryFn: () => getProducts({ page, search, size: 20 }),
    });

    const createMutation = useMutation({
        mutationFn: createProduct,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['products'] });
            toast.success('Tạo sản phẩm thành công!');
            closeModal();
        },
        onError: (error) => {
            const msg = toDisplayMessage(error);
            warnIfNotRenderable(msg, 'products.create');
            toast.error(msg);
        },
    });

    const updateMutation = useMutation({
        mutationFn: ({ id, data }) => updateProduct(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['products'] });
            toast.success('Cập nhật sản phẩm thành công!');
            closeModal();
        },
        onError: (error) => {
            const msg = toDisplayMessage(error);
            warnIfNotRenderable(msg, 'products.update');
            toast.error(msg);
        },
    });

    const deleteMutation = useMutation({
        mutationFn: deleteProduct,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['products'] });
            toast.success('Xóa sản phẩm thành công!');
        },
        onError: (error) => {
            const msg = toDisplayMessage(error);
            warnIfNotRenderable(msg, 'products.delete');
            toast.error(msg);
        },
    });

    const openModal = (product = null) => {
        setEditingProduct(product);
        if (product) {
            reset(product);
        } else {
            reset({ sku: '', name: '', category: '', unit: 'cái', cost_price: 0, sell_price: 0, min_stock: 0, current_stock: 0 });
        }
        setIsModalOpen(true);
    };

    const closeModal = () => {
        setIsModalOpen(false);
        setEditingProduct(null);
        reset();
    };

    const onSubmit = (formData) => {
        const data = cleanFormData({
            ...formData,
            cost_price: Number(formData.cost_price),
            sell_price: Number(formData.sell_price),
            min_stock: Number(formData.min_stock),
            current_stock: Number(formData.current_stock || 0),
        });

        if (editingProduct) {
            updateMutation.mutate({ id: editingProduct.id, data });
        } else {
            createMutation.mutate(data);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Sản phẩm</h1>
                    <p className="text-gray-500">Quản lý danh mục sản phẩm</p>
                </div>
                <button onClick={() => openModal()} className="btn-primary">
                    + Thêm sản phẩm
                </button>
            </div>

            {/* Search */}
            <div className="card">
                <input
                    type="text"
                    placeholder="Tìm kiếm theo SKU hoặc tên..."
                    value={search}
                    onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                    className="form-input max-w-md"
                />
            </div>

            {/* Table */}
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
                                    <th className="table-header">SKU</th>
                                    <th className="table-header">Tên sản phẩm</th>
                                    <th className="table-header">Danh mục</th>
                                    <th className="table-header text-right">Giá vốn</th>
                                    <th className="table-header text-right">Giá bán</th>
                                    <th className="table-header text-right">Tồn kho</th>
                                    <th className="table-header text-right">Thao tác</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {data?.items?.map((product) => (
                                    <tr key={product.id} className="hover:bg-gray-50">
                                        <td className="table-cell font-medium">{product.sku}</td>
                                        <td className="table-cell">{product.name}</td>
                                        <td className="table-cell text-gray-500">{product.category || '-'}</td>
                                        <td className="table-cell text-right">{formatVND(product.cost_price)}</td>
                                        <td className="table-cell text-right">{formatVND(product.sell_price)}</td>
                                        <td className="table-cell text-right">
                                            <span className={product.is_low_stock ? 'text-red-600 font-medium' : ''}>
                                                {product.current_stock}
                                            </span>
                                        </td>
                                        <td className="table-cell text-right space-x-2">
                                            <button onClick={() => openModal(product)} className="text-primary-600 hover:text-primary-800">
                                                Sửa
                                            </button>
                                            <button
                                                onClick={() => { if (confirm('Xác nhận xóa sản phẩm?')) deleteMutation.mutate(product.id); }}
                                                className="text-red-600 hover:text-red-800"
                                            >
                                                Xóa
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                {/* Pagination */}
                {data && data.total > 20 && (
                    <div className="flex items-center justify-between px-6 py-3 border-t bg-gray-50">
                        <p className="text-sm text-gray-500">
                            Hiển thị {(page - 1) * 20 + 1} - {Math.min(page * 20, data.total)} của {data.total}
                        </p>
                        <div className="flex gap-2">
                            <button
                                onClick={() => setPage(p => Math.max(1, p - 1))}
                                disabled={page === 1}
                                className="btn-secondary text-sm py-1"
                            >
                                Trước
                            </button>
                            <button
                                onClick={() => setPage(p => p + 1)}
                                disabled={page * 20 >= data.total}
                                className="btn-secondary text-sm py-1"
                            >
                                Sau
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {/* Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 z-50 overflow-y-auto">
                    <div className="flex min-h-screen items-center justify-center p-4">
                        <div className="fixed inset-0 bg-black/50" onClick={closeModal} />
                        <div className="relative bg-white rounded-xl shadow-xl max-w-lg w-full p-6">
                            <h3 className="text-lg font-semibold mb-4">
                                {editingProduct ? 'Sửa sản phẩm' : 'Thêm sản phẩm mới'}
                            </h3>
                            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="form-label">SKU *</label>
                                        <input {...register('sku', { required: 'Bắt buộc' })} className="form-input" />
                                        {errors.sku && <p className="form-error">{errors.sku.message}</p>}
                                    </div>
                                    <div>
                                        <label className="form-label">Đơn vị</label>
                                        <input {...register('unit')} className="form-input" placeholder="cái" />
                                    </div>
                                </div>
                                <div>
                                    <label className="form-label">Tên sản phẩm *</label>
                                    <input {...register('name', { required: 'Bắt buộc' })} className="form-input" />
                                    {errors.name && <p className="form-error">{errors.name.message}</p>}
                                </div>
                                <div>
                                    <label className="form-label">Danh mục</label>
                                    <input {...register('category')} className="form-input" />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="form-label">Giá vốn (VND)</label>
                                        <input type="number" {...register('cost_price')} className="form-input" />
                                    </div>
                                    <div>
                                        <label className="form-label">Giá bán (VND)</label>
                                        <input type="number" {...register('sell_price')} className="form-input" />
                                    </div>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="form-label">Tồn kho tối thiểu</label>
                                        <input type="number" {...register('min_stock')} className="form-input" />
                                    </div>
                                    {!editingProduct && (
                                        <div>
                                            <label className="form-label">Tồn kho ban đầu</label>
                                            <input type="number" {...register('current_stock')} className="form-input" />
                                        </div>
                                    )}
                                </div>
                                <div className="flex justify-end gap-3 pt-4">
                                    <button type="button" onClick={closeModal} className="btn-secondary">Hủy</button>
                                    <button type="submit" className="btn-primary" disabled={createMutation.isPending || updateMutation.isPending}>
                                        {editingProduct ? 'Cập nhật' : 'Tạo mới'}
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
