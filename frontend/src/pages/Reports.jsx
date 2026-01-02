import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getRevenueReport, getTopProducts, getInventoryValuation, getARAPSummary } from '../api/reports';
import { toDisplayMessage } from '../utils/toDisplayMessage';
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function formatVND(value) {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value);
}

function formatShortVND(value) {
    if (value >= 1000000000) return `${(value / 1000000000).toFixed(1)}B`;
    if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `${(value / 1000).toFixed(0)}K`;
    return value;
}

export default function Reports() {
    const [revenuePeriod, setRevenuePeriod] = useState('day');
    const [revenueDays, setRevenueDays] = useState(30);

    const { data: revenueData } = useQuery({
        queryKey: ['revenue-report', { period: revenuePeriod, days: revenueDays }],
        queryFn: () => getRevenueReport({ period: revenuePeriod, days: revenueDays }),
    });

    const { data: topProducts } = useQuery({
        queryKey: ['top-products'],
        queryFn: () => getTopProducts({ days: 30, limit: 10 }),
    });

    const { data: inventoryData } = useQuery({
        queryKey: ['inventory-valuation'],
        queryFn: getInventoryValuation,
    });

    const { data: arapData } = useQuery({
        queryKey: ['arap-summary'],
        queryFn: getARAPSummary,
    });

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-gray-900">Báo cáo</h1>
                <p className="text-gray-500">Thống kê và phân tích kinh doanh</p>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="card">
                    <p className="text-sm text-gray-500">Tổng doanh thu</p>
                    <p className="text-2xl font-bold text-primary-600">{formatVND(revenueData?.total_revenue || 0)}</p>
                    <p className="text-sm text-gray-500">{revenueData?.total_orders || 0} đơn hàng</p>
                </div>
                <div className="card">
                    <p className="text-sm text-gray-500">Giá trị tồn kho</p>
                    <p className="text-2xl font-bold text-green-600">{formatVND(inventoryData?.total_value || 0)}</p>
                    <p className="text-sm text-gray-500">{inventoryData?.data?.length || 0} sản phẩm</p>
                </div>
                <div className="card">
                    <p className="text-sm text-gray-500">Công nợ phải thu</p>
                    <p className="text-2xl font-bold text-red-600">{formatVND(arapData?.total_receivables || 0)}</p>
                    <p className="text-sm text-gray-500">{arapData?.customer_count || 0} khách hàng</p>
                </div>
                <div className="card">
                    <p className="text-sm text-gray-500">Công nợ phải trả</p>
                    <p className="text-2xl font-bold text-orange-600">{formatVND(arapData?.total_payables || 0)}</p>
                    <p className="text-sm text-gray-500">{arapData?.supplier_count || 0} nhà cung cấp</p>
                </div>
            </div>

            {/* Revenue Chart */}
            <div className="card">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
                    <h3 className="font-semibold">Biểu đồ doanh thu</h3>
                    <div className="flex gap-2">
                        <select
                            value={revenuePeriod}
                            onChange={(e) => setRevenuePeriod(e.target.value)}
                            className="form-input py-1 text-sm"
                        >
                            <option value="day">Theo ngày</option>
                            <option value="week">Theo tuần</option>
                            <option value="month">Theo tháng</option>
                        </select>
                        <select
                            value={revenueDays}
                            onChange={(e) => setRevenueDays(Number(e.target.value))}
                            className="form-input py-1 text-sm"
                        >
                            <option value={7}>7 ngày</option>
                            <option value={30}>30 ngày</option>
                            <option value={90}>90 ngày</option>
                            <option value={365}>1 năm</option>
                        </select>
                    </div>
                </div>
                <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={revenueData?.data || []}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="period" tickFormatter={(v) => v.slice(-5)} />
                            <YAxis tickFormatter={formatShortVND} />
                            <Tooltip formatter={(value) => [formatVND(value), 'Doanh thu']} />
                            <Area type="monotone" dataKey="revenue" stroke="#3b82f6" fill="#93c5fd" fillOpacity={0.5} />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Top Products */}
                <div className="card">
                    <h3 className="font-semibold mb-4">Top 10 sản phẩm bán chạy</h3>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={topProducts?.data || []} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis type="number" tickFormatter={formatShortVND} />
                                <YAxis type="category" dataKey="product_sku" width={80} />
                                <Tooltip formatter={(value) => [formatVND(value), 'Doanh thu']} />
                                <Bar dataKey="total_revenue" fill="#10b981" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Inventory Valuation */}
                <div className="card overflow-hidden p-0">
                    <div className="px-6 py-4 border-b bg-gray-50 flex justify-between items-center">
                        <h3 className="font-semibold">Giá trị tồn kho</h3>
                        <span className="font-bold text-green-600">{formatVND(inventoryData?.total_value || 0)}</span>
                    </div>
                    <div className="overflow-x-auto max-h-72">
                        <table className="min-w-full">
                            <thead className="bg-gray-50 sticky top-0">
                                <tr>
                                    <th className="table-header">SKU</th>
                                    <th className="table-header text-right">SL</th>
                                    <th className="table-header text-right">Giá vốn</th>
                                    <th className="table-header text-right">Giá trị</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {inventoryData?.data?.slice(0, 10).map(item => (
                                    <tr key={item.product_id} className="hover:bg-gray-50">
                                        <td className="table-cell font-medium">{item.product_sku}</td>
                                        <td className="table-cell text-right">{item.current_stock}</td>
                                        <td className="table-cell text-right text-gray-500">{formatVND(item.cost_price)}</td>
                                        <td className="table-cell text-right font-medium">{formatVND(item.total_value)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Export Section */}
            <div className="card">
                <h3 className="font-semibold mb-4">Xuất báo cáo</h3>
                <div className="flex flex-wrap gap-3">
                    <a href="/api/export/products" target="_blank" className="btn-secondary text-sm">
                        📥 Xuất sản phẩm (CSV)
                    </a>
                    <a href="/api/export/orders" target="_blank" className="btn-secondary text-sm">
                        📥 Xuất đơn hàng (CSV)
                    </a>
                    <a href="/api/export/payments" target="_blank" className="btn-secondary text-sm">
                        📥 Xuất thanh toán (CSV)
                    </a>
                </div>
            </div>
        </div>
    );
}
