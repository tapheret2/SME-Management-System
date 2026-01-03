import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { getDashboardMetrics, getRevenueReport } from '../api/reports';
import { getLowStockProducts } from '../api/products';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function formatVND(value) {
    const num = Number(value) || 0;
    // Format with compact notation for large numbers
    if (num >= 1000000000) {
        return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND', notation: 'compact', maximumFractionDigits: 1 }).format(num);
    }
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(num);
}

function MetricCard({ title, value, subValue, icon, color = 'primary' }) {
    const colors = {
        primary: 'bg-primary-50 text-primary-600',
        green: 'bg-green-50 text-green-600',
        yellow: 'bg-yellow-50 text-yellow-600',
        red: 'bg-red-50 text-red-600',
    };

    return (
        <div className="card">
            <div className="flex items-start">
                <div className={`p-3 rounded-lg flex-shrink-0 ${colors[color]}`}>
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={icon} />
                    </svg>
                </div>
                <div className="ml-3 min-w-0">
                    <p className="text-sm font-medium text-gray-500">{title}</p>
                    <p className="text-lg font-bold text-gray-900 break-words">{value}</p>
                    {subValue && <p className="text-xs text-gray-500">{subValue}</p>}
                </div>
            </div>
        </div>
    );
}

export default function Dashboard() {
    const { data: metrics, isLoading: metricsLoading } = useQuery({
        queryKey: ['dashboard-metrics'],
        queryFn: getDashboardMetrics,
    });

    const { data: revenueData } = useQuery({
        queryKey: ['revenue-report', { period: 'day', days: 30 }],
        queryFn: () => getRevenueReport({ period: 'day', days: 30 }),
    });

    const { data: lowStockProducts } = useQuery({
        queryKey: ['low-stock-products'],
        queryFn: getLowStockProducts,
    });

    if (metricsLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
                <p className="text-gray-500">Tổng quan hoạt động kinh doanh</p>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                <MetricCard
                    title="Doanh thu tháng này"
                    value={formatVND(metrics?.month_revenue || 0)}
                    subValue={`${metrics?.month_count || 0} đơn hàng`}
                    icon="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    color="primary"
                />
                <MetricCard
                    title="Lợi nhuận tháng này"
                    value={formatVND(metrics?.month_profit || 0)}
                    subValue="Sau giá vốn"
                    icon="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                    color="green"
                />
                <MetricCard
                    title="Tiền nhập hàng tháng"
                    value={formatVND(metrics?.month_import_cost || 0)}
                    subValue="Tổng giá trị nhập kho"
                    icon="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
                    color="yellow"
                />
                <MetricCard
                    title="Công nợ phải thu"
                    value={formatVND(metrics?.total_receivables || 0)}
                    subValue={`${metrics?.debtor_count || 0} khách hàng`}
                    icon="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"
                    color="red"
                />
                <MetricCard
                    title="Cảnh báo tồn kho"
                    value={metrics?.low_stock_count || 0}
                    subValue={`${metrics?.total_products || 0} sản phẩm`}
                    icon="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    color={metrics?.low_stock_count > 0 ? 'red' : 'green'}
                />
            </div>

            {/* Revenue Chart */}
            <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Doanh thu 30 ngày qua</h3>
                <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={revenueData?.data || []}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="period" tickFormatter={(v) => v.slice(5)} />
                            <YAxis tickFormatter={(v) => `${(v / 1000000).toFixed(0)}M`} />
                            <Tooltip
                                formatter={(value) => [formatVND(value), 'Doanh thu']}
                                labelFormatter={(label) => `Ngày ${label}`}
                            />
                            <Area
                                type="monotone"
                                dataKey="revenue"
                                stroke="#3b82f6"
                                fill="#93c5fd"
                                fillOpacity={0.5}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Low Stock Products */}
            {lowStockProducts && lowStockProducts.length > 0 && (
                <div className="card">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-gray-900">Sản phẩm sắp hết hàng</h3>
                        <Link to="/inventory" className="text-sm text-primary-600 hover:text-primary-700">
                            Xem tất cả →
                        </Link>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="min-w-full">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="table-header">SKU</th>
                                    <th className="table-header">Tên sản phẩm</th>
                                    <th className="table-header text-right">Tồn kho</th>
                                    <th className="table-header text-right">Tồn tối thiểu</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {lowStockProducts.slice(0, 5).map((product) => (
                                    <tr key={product.id}>
                                        <td className="table-cell font-medium">{product.sku}</td>
                                        <td className="table-cell">{product.name}</td>
                                        <td className="table-cell text-right">
                                            <span className="text-red-600 font-medium">{product.current_stock}</span>
                                        </td>
                                        <td className="table-cell text-right">{product.min_stock}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}
