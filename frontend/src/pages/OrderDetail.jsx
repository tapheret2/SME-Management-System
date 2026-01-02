import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { getOrder, updateOrderStatus } from '../api/orders';
import { toDisplayMessage } from '../utils/toDisplayMessage';
import { format } from 'date-fns';

function formatVND(value) {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value);
}

const statusLabels = {
    draft: 'Nháp',
    confirmed: 'Đã xác nhận',
    shipped: 'Đang giao',
    completed: 'Hoàn thành',
    cancelled: 'Đã hủy',
};

const statusColors = {
    draft: 'badge-draft',
    confirmed: 'badge-confirmed',
    shipped: 'badge-shipped',
    completed: 'badge-completed',
    cancelled: 'badge-cancelled',
};

export default function OrderDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const { data: order, isLoading } = useQuery({
        queryKey: ['order', id],
        queryFn: () => getOrder(id),
    });

    const statusMutation = useMutation({
        mutationFn: (status) => updateOrderStatus(id, status),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['order', id] });
            toast.success('Cập nhật trạng thái thành công!');
        },
        onError: (error) => toast.error(toDisplayMessage(error)),
    });

    const getNextStatus = (currentStatus) => {
        const transitions = {
            draft: ['confirmed', 'cancelled'],
            confirmed: ['shipped', 'cancelled'],
            shipped: ['completed'],
        };
        return transitions[currentStatus] || [];
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            </div>
        );
    }

    if (!order) {
        return <div className="text-center py-12">Không tìm thấy đơn hàng</div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <button onClick={() => navigate('/orders')} className="text-gray-500 hover:text-gray-700 mb-2">
                        ← Quay lại
                    </button>
                    <h1 className="text-2xl font-bold text-gray-900">Đơn hàng #{order.order_number}</h1>
                </div>
                <span className={statusColors[order.status]}>{statusLabels[order.status]}</span>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Order Info */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="card">
                        <h3 className="font-semibold mb-4">Thông tin đơn hàng</h3>
                        <dl className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                                <dt className="text-gray-500">Khách hàng</dt>
                                <dd className="font-medium">{order.customer_name}</dd>
                            </div>
                            <div>
                                <dt className="text-gray-500">Ngày đặt</dt>
                                <dd className="font-medium">{format(new Date(order.order_date), 'dd/MM/yyyy HH:mm')}</dd>
                            </div>
                            <div>
                                <dt className="text-gray-500">Người tạo</dt>
                                <dd className="font-medium">{order.creator_name}</dd>
                            </div>
                            <div>
                                <dt className="text-gray-500">Ngày tạo</dt>
                                <dd className="font-medium">{format(new Date(order.created_at), 'dd/MM/yyyy HH:mm')}</dd>
                            </div>
                        </dl>
                        {order.notes && (
                            <div className="mt-4 pt-4 border-t">
                                <p className="text-sm text-gray-500">Ghi chú: {order.notes}</p>
                            </div>
                        )}
                    </div>

                    {/* Line Items */}
                    <div className="card overflow-hidden p-0">
                        <div className="px-6 py-4 border-b bg-gray-50">
                            <h3 className="font-semibold">Chi tiết sản phẩm</h3>
                        </div>
                        <table className="min-w-full">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="table-header">SKU</th>
                                    <th className="table-header">Sản phẩm</th>
                                    <th className="table-header text-right">SL</th>
                                    <th className="table-header text-right">Đơn giá</th>
                                    <th className="table-header text-right">Giảm giá</th>
                                    <th className="table-header text-right">Thành tiền</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {order.line_items?.map((item) => (
                                    <tr key={item.id}>
                                        <td className="table-cell font-medium">{item.product_sku}</td>
                                        <td className="table-cell">{item.product_name}</td>
                                        <td className="table-cell text-right">{item.quantity}</td>
                                        <td className="table-cell text-right">{formatVND(item.unit_price)}</td>
                                        <td className="table-cell text-right">{formatVND(item.discount)}</td>
                                        <td className="table-cell text-right font-medium">{formatVND(item.line_total)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Summary & Actions */}
                <div className="space-y-6">
                    <div className="card">
                        <h3 className="font-semibold mb-4">Tổng cộng</h3>
                        <dl className="space-y-3 text-sm">
                            <div className="flex justify-between">
                                <dt className="text-gray-500">Tạm tính</dt>
                                <dd>{formatVND(order.subtotal)}</dd>
                            </div>
                            <div className="flex justify-between">
                                <dt className="text-gray-500">Giảm giá</dt>
                                <dd className="text-red-600">-{formatVND(order.discount)}</dd>
                            </div>
                            <div className="flex justify-between font-semibold text-lg pt-3 border-t">
                                <dt>Tổng tiền</dt>
                                <dd>{formatVND(order.total)}</dd>
                            </div>
                            <div className="flex justify-between pt-3 border-t">
                                <dt className="text-gray-500">Đã thanh toán</dt>
                                <dd className="text-green-600">{formatVND(order.paid_amount)}</dd>
                            </div>
                            <div className="flex justify-between">
                                <dt className="text-gray-500">Còn nợ</dt>
                                <dd className={Number(order.remaining_amount) > 0 ? 'text-red-600 font-medium' : 'text-green-600'}>
                                    {formatVND(order.remaining_amount)}
                                </dd>
                            </div>
                        </dl>
                    </div>

                    {/* Actions */}
                    {getNextStatus(order.status).length > 0 && (
                        <div className="card">
                            <h3 className="font-semibold mb-4">Thao tác</h3>
                            <div className="space-y-2">
                                {getNextStatus(order.status).map(status => (
                                    <button
                                        key={status}
                                        onClick={() => statusMutation.mutate(status)}
                                        disabled={statusMutation.isPending}
                                        className={`w-full ${status === 'cancelled' ? 'btn-danger' : 'btn-primary'}`}
                                    >
                                        {status === 'confirmed' && 'Xác nhận đơn hàng'}
                                        {status === 'shipped' && 'Giao hàng'}
                                        {status === 'completed' && 'Hoàn thành'}
                                        {status === 'cancelled' && 'Hủy đơn hàng'}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
