import React, { useState } from 'react';
import { Database, Filter, Download, MoreHorizontal } from 'lucide-react';

const MOCK_DATA = [
  { id: '1', sku: 'LAP-001', name: 'MacBook Pro M3 Max 16-inch', brand: 'Apple', price: '89,990,000', source: 'TheGioiDiDong', date: '2023-11-15' },
  { id: '2', sku: 'LAP-002', name: 'ASUS ROG Strix G16', brand: 'ASUS', price: '35,490,000', source: 'PhongVu', date: '2023-11-15' },
  { id: '3', sku: 'KB-001', name: 'Keychron K8 Pro QMK', brand: 'Keychron', price: '2,490,000', source: 'TheGioiDiDong', date: '2023-11-15' },
  { id: '4', sku: 'MON-001', name: 'LG UltraGear 27GP850-B 27" Nano IPS', brand: 'LG', price: '8,590,000', source: 'PhongVu', date: '2023-11-15' },
  { id: '5', sku: 'LAP-003', name: 'Dell XPS 15 9530', brand: 'Dell', price: '54,990,000', source: 'TheGioiDiDong', date: '2023-11-14' },
  { id: '6', sku: 'LAP-004', name: 'Lenovo ThinkPad X1 Carbon Gen 11', brand: 'Lenovo', price: '45,990,000', source: 'PhongVu', date: '2023-11-14' },
  { id: '7', sku: 'KB-002', name: 'Logitech MX Mechanical Mini', brand: 'Logitech', price: '3,290,000', source: 'TheGioiDiDong', date: '2023-11-14' },
  { id: '8', sku: 'MON-002', name: 'Dell UltraSharp U2723QE 27" 4K', brand: 'Dell', price: '14,990,000', source: 'PhongVu', date: '2023-11-14' },
];

const DataTable = () => {
  const [activeTab, setActiveTab] = useState('All');
  
  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Dữ Liệu Thu Thập (Data Table)</h1>
          <p className="text-slate-400 mt-1">Danh sách sản phẩm được thu thập từ các nguồn (HDFS/Hive).</p>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-slate-800 text-slate-300 rounded-lg hover:bg-slate-700 hover:text-white transition-colors border border-slate-700">
            <Filter size={16} />
            Bộ Lọc
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 transition-colors shadow-[0_0_15px_rgba(79,70,229,0.3)]">
            <Download size={16} />
            Xuất Excel
          </button>
        </div>
      </div>

      <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 rounded-2xl shadow-lg overflow-hidden">
        {/* Tabs */}
        <div className="flex border-b border-slate-700/50">
          {['All', 'Laptop', 'Keyboard', 'Monitor'].map(tab => (
            <button 
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-4 text-sm font-medium transition-colors border-b-2 ${
                activeTab === tab 
                  ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5' 
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="text-xs text-slate-400 uppercase bg-slate-800/50 border-b border-slate-700/50">
              <tr>
                <th className="px-6 py-4">Mã SKU</th>
                <th className="px-6 py-4">Tên Sản Phẩm</th>
                <th className="px-6 py-4">Thương Hiệu</th>
                <th className="px-6 py-4">Giá (VNĐ)</th>
                <th className="px-6 py-4">Nguồn</th>
                <th className="px-6 py-4">Ngày Crawl</th>
                <th className="px-6 py-4 text-center">Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {MOCK_DATA.filter(item => activeTab === 'All' || item.sku.startsWith(activeTab === 'Laptop' ? 'LAP' : activeTab === 'Keyboard' ? 'KB' : 'MON')).map((row, i) => (
                <tr key={row.id} className={`border-b border-slate-700/50 hover:bg-slate-800/50 transition-colors ${i % 2 === 0 ? 'bg-transparent' : 'bg-slate-800/20'}`}>
                  <td className="px-6 py-4 font-medium text-slate-200">{row.sku}</td>
                  <td className="px-6 py-4">{row.name}</td>
                  <td className="px-6 py-4">
                    <span className="px-2.5 py-1 bg-slate-700/50 rounded-full text-xs font-medium border border-slate-600/50">
                      {row.brand}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono text-emerald-400">{row.price}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <Database size={14} className="text-slate-500" />
                      {row.source}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-slate-400">{row.date}</td>
                  <td className="px-6 py-4 text-center">
                    <button className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-700 rounded-md transition-colors">
                      <MoreHorizontal size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {/* Pagination */}
        <div className="p-4 border-t border-slate-700/50 flex items-center justify-between text-sm text-slate-400">
          <div>Hiển thị 1 đến 8 trong số 12,432 kết quả</div>
          <div className="flex gap-1">
            <button className="px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 transition-colors disabled:opacity-50" disabled>Trang trước</button>
            <button className="px-3 py-1 rounded bg-indigo-600 text-white shadow-[0_0_10px_rgba(79,70,229,0.3)]">1</button>
            <button className="px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 transition-colors">2</button>
            <button className="px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 transition-colors">3</button>
            <button className="px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 transition-colors">Trang sau</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataTable;
