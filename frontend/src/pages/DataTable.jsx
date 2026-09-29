import React, { useState, useEffect } from 'react';
import { Database, Filter, Download, MoreHorizontal, RefreshCw, Plus, Edit2, Trash2 } from 'lucide-react';


const DataTable = () => {
  const [activeTab, setActiveTab] = useState('All');
  const [actionLoading, setActionLoading] = useState(false);
  const [tableData, setTableData] = useState([]);
  const [loadingData, setLoadingData] = useState(false);
  
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);
  const [totalRecords, setTotalRecords] = useState(0);

  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState('add');
  const [formData, setFormData] = useState({ sku: '', name: '', brand: '', price: '' });

  useEffect(() => {
    setPage(1); // Reset page when tab changes
  }, [activeTab]);

  useEffect(() => {
    setLoadingData(true);
    fetch(`http://localhost:8000/api/data-table/?category=${activeTab}&page=${page}&limit=${limit}`)
      .then(res => res.json())
      .then(data => {
        setTableData(data.data || []);
        setTotalRecords(data.total || 0);
        setLoadingData(false);
      })
      .catch(err => {
        console.error("Lỗi lấy data-table:", err);
        setLoadingData(false);
      });
  }, [activeTab, page, limit]);

  const handleRunSqoop = async () => {
    const tableName = activeTab === 'Laptop' ? 'laptop_products_common' : activeTab === 'Keyboard' ? 'keyboard_products_common' : 'monitor_products_common';
    alert(`Đang bắt đầu kéo dữ liệu (Sqoop) cho bảng: ${tableName}...\nVui lòng chờ, quá trình này có thể mất vài phút.`);
    setActionLoading(true);
    try {
      const settings = JSON.parse(localStorage.getItem('bigdata_settings')) || {};
      const response = await fetch('http://localhost:8000/api/run-sqoop/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
              hadoop_host: settings.hadoopIp || '192.168.10.10',
              hadoop_user: settings.hadoopUser || 'hadoopthuc',
              mysql_host: settings.mysqlHost || '192.168.10.5',
              mysql_user: settings.mysqlUser || 'root',
              mysql_password: settings.mysqlPassword || '123456789',
              mysql_db: settings.mysqlDatabase || 'bigdata_db',
              table_name: tableName,
              target_dir: `/user/hadoopthuc/project/input_${tableName}`
          })
      });
      const data = await response.json();
      setActionLoading(false);
      if (data.status === "success") {
          alert("Chạy Sqoop thành công!\nLog: " + data.logs.substring(0, 500));
      } else {
          alert("Lỗi khi chạy Sqoop:\n\n" + data.error_logs);
      }
    } catch (error) {
      setActionLoading(false);
      alert("Lỗi kết nối tới Server: " + error);
    }
  };

  const handleRunMapReduce = async () => {
    const tableName = activeTab === 'Laptop' ? 'laptop_products_common' : activeTab === 'Keyboard' ? 'keyboard_products_common' : 'monitor_products_common';
    const outputName = activeTab === 'Laptop' ? 'laptop_stats' : activeTab === 'Keyboard' ? 'keyboard_stats' : 'monitor_stats';
    alert(`Đang bắt đầu chạy MapReduce cho dữ liệu: ${activeTab}...\nVui lòng chờ, quá trình này có thể mất vài phút.`);
    setActionLoading(true);
    try {
      const settings = JSON.parse(localStorage.getItem('bigdata_settings')) || {};
      const response = await fetch('http://localhost:8000/api/run-mapreduce/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
              hadoop_host: settings.hadoopIp || '192.168.10.10',
              hadoop_user: settings.hadoopUser || 'hadoopthuc',
              input_dir: `/user/hadoopthuc/project/input_${tableName}`,
              output_dir: `/user/hadoopthuc/project/output_${outputName}`
          })
      });
      const data = await response.json();
      setActionLoading(false);
      if (data.status === "success") {
          alert("Chạy MapReduce thành công!\n\nKết quả (10 dòng đầu):\n" + data.logs.substring(0, 500));
      } else {
          alert("Lỗi khi chạy MapReduce:\n\n" + data.error_logs);
      }
    } catch (error) {
      setActionLoading(false);
      alert("Lỗi kết nối tới Server: " + error);
    }
  };

  const handleRunSqoopExport = async () => {
    const tableName = activeTab === 'Laptop' ? 'laptop_stats' : activeTab === 'Keyboard' ? 'keyboard_stats' : 'monitor_stats';
    alert(`Đang bắt đầu sao lưu dữ liệu (Sqoop Export) từ HDFS về MySQL cho bảng: ${tableName}...\nVui lòng chờ, quá trình này có thể mất vài phút.`);
    setActionLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/run-sqoop-export/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
              table_name: tableName,
              export_dir: `/user/hadoopthuc/project/output_${tableName}`
          })
      });
      const data = await response.json();
      setActionLoading(false);
      if (data.status === "success") {
          alert("Sao lưu (Sqoop Export) thành công!\nLog: " + data.logs.substring(0, 500));
      } else {
          alert("Lỗi khi Export:\n\n" + data.error_logs);
      }
    } catch (error) {
      setActionLoading(false);
      alert("Lỗi kết nối tới Server: " + error);
    }
  };

  const loadData = () => {
    setLoadingData(true);
    fetch(`http://localhost:8000/api/data-table/?category=${activeTab}&page=${page}&limit=${limit}`)
      .then(res => res.json())
      .then(data => {
        setTableData(data.data || []);
        setTotalRecords(data.total || 0);
        setLoadingData(false);
      })
      .catch(err => {
        console.error("Lỗi lấy data-table:", err);
        setLoadingData(false);
      });
  };

  const handleAdd = () => {
    if(activeTab === 'All') return alert("Vui lòng chọn 1 loại dữ liệu cụ thể (Laptop/Keyboard/Monitor) để thêm!");
    setModalMode('add');
    setFormData({ sku: '', name: '', brand: '', price: '' });
    setShowModal(true);
  };

  const handleEdit = (row) => {
    if(activeTab === 'All') return alert("Vui lòng chuyển qua tab dữ liệu cụ thể để sửa!");
    setModalMode('edit');
    setFormData({ 
      sku: row.sku, 
      name: row.name, 
      brand: row.brand, 
      price: row.price.replace(/,/g, '') 
    });
    setShowModal(true);
  };
  
  const handleSave = async (e) => {
    e.preventDefault();
    if(!formData.sku || !formData.name || !formData.brand || !formData.price) return;
    
    setActionLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/data-record/', {
        method: modalMode === 'add' ? 'POST' : 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          category: activeTab, 
          ...formData, 
          price: parseInt(formData.price.toString().replace(/\D/g,'')) 
        })
      });
      if(res.ok) { 
        setShowModal(false);
        loadData(); 
      }
      else alert("Lỗi khi lưu dữ liệu!");
    } catch(e) { alert("Lỗi kết nối: " + e); }
    setActionLoading(false);
  };

  const handleDelete = async (row) => {
    if(activeTab === 'All') return alert("Vui lòng chuyển qua tab dữ liệu cụ thể để xóa!");
    if(!window.confirm(`Bạn có chắc muốn xóa SKU: ${row.sku}?`)) return;
    
    setActionLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/data-record/', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category: activeTab, sku: row.sku })
      });
      if(res.ok) { alert("Xóa thành công!"); loadData(); }
      else alert("Lỗi khi xóa!");
    } catch(e) { alert(e); }
    setActionLoading(false);
  };

  
  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Dữ Liệu Thu Thập (Data Table)</h1>
          <p className="text-slate-400 mt-1">Danh sách sản phẩm được thu thập từ các nguồn (HDFS/Hive).</p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={handleAdd}
            disabled={actionLoading || activeTab === 'All'}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600/20 text-emerald-400 rounded-lg hover:bg-emerald-600/30 transition-colors border border-emerald-500/30 shadow-[0_0_10px_rgba(16,185,129,0.2)] disabled:opacity-50">
            <Plus size={16} />
            Thêm Mới
          </button>
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
        {/* Tabs and Actions */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-700/50 pr-4">
          <div className="flex">
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
          
          {activeTab !== 'All' && (
            <div className="flex items-center gap-2 mt-2 sm:mt-0 pb-2 sm:pb-0 px-4 sm:px-0">
              <button 
                onClick={() => handleRunSqoop()}
                disabled={actionLoading}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600/20 text-emerald-400 hover:bg-emerald-600/40 rounded border border-emerald-500/30 transition-colors text-sm font-medium disabled:opacity-50"
              >
                <Database size={14} /> Sqoop Import
              </button>
              <button 
                onClick={() => handleRunMapReduce()}
                disabled={actionLoading}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600/20 text-indigo-400 hover:bg-indigo-600/40 rounded border border-indigo-500/30 transition-colors text-sm font-medium disabled:opacity-50"
              >
                <Database size={14} /> Chạy MapReduce
              </button>
              <button 
                onClick={() => handleRunSqoopExport()}
                disabled={actionLoading}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-amber-600/20 text-amber-400 hover:bg-amber-600/40 rounded border border-amber-500/30 transition-colors text-sm font-medium disabled:opacity-50"
              >
                <Database size={14} /> Sao lưu MySQL
              </button>
            </div>
          )}
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
              {loadingData ? (
                <tr>
                  <td colSpan="7" className="px-6 py-10 text-center text-slate-400">
                    <RefreshCw className="animate-spin inline-block mr-2" size={20} />
                    Đang tải dữ liệu từ CSDL...
                  </td>
                </tr>
              ) : tableData.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-10 text-center text-slate-500">
                    Chưa có dữ liệu. Vui lòng chạy Sqoop Import trước.
                  </td>
                </tr>
              ) : (
                tableData.map((row, i) => (
                  <tr key={row.id} className={`border-b border-slate-700/50 hover:bg-slate-800/50 transition-colors ${i % 2 === 0 ? 'bg-transparent' : 'bg-slate-800/20'}`}>
                    <td className="px-6 py-4 font-medium text-slate-200">{row.sku}</td>
                    <td className="px-6 py-4 max-w-xs truncate" title={row.name}>{row.name}</td>
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
                      <div className="flex items-center justify-center gap-2">
                        <button onClick={() => handleEdit(row)} className="p-1.5 text-indigo-400 hover:text-indigo-300 hover:bg-indigo-500/20 rounded-md transition-colors" title="Sửa">
                          <Edit2 size={16} />
                        </button>
                        <button onClick={() => handleDelete(row)} className="p-1.5 text-rose-400 hover:text-rose-300 hover:bg-rose-500/20 rounded-md transition-colors" title="Xóa">
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        
        {/* Pagination */}
        <div className="p-4 border-t border-slate-700/50 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-slate-400">
          <div className="flex items-center gap-4">
            <div>
              Hiển thị {totalRecords > 0 ? (page - 1) * limit + 1 : 0} đến {Math.min(page * limit, totalRecords)} trong số <span className="font-medium text-slate-200">{totalRecords.toLocaleString()}</span> kết quả
            </div>
            <div className="flex items-center gap-2">
              <span>Số dòng/trang:</span>
              <select 
                value={limit} 
                onChange={(e) => { setLimit(Number(e.target.value)); setPage(1); }}
                className="bg-slate-800 border border-slate-700 text-slate-300 rounded px-2 py-1 outline-none focus:border-indigo-500"
              >
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </div>
          </div>
          <div className="flex gap-1">
            <button 
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Trang trước
            </button>
            <button className="px-3 py-1 rounded bg-indigo-600 text-white shadow-[0_0_10px_rgba(79,70,229,0.3)]">{page}</button>
            <button 
              onClick={() => setPage(p => p + 1)}
              disabled={page * limit >= totalRecords}
              className="px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Trang sau
            </button>
          </div>
        </div>
      </div>

      {/* CRUD Modal Form */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-slate-800 border border-slate-700 rounded-xl shadow-2xl w-full max-w-md p-6">
            <h3 className="text-xl font-semibold text-white mb-4">
              {modalMode === 'add' ? 'Thêm Dữ Liệu Mới' : 'Cập Nhật Dữ Liệu'}
            </h3>
            <form onSubmit={handleSave} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">SKU (Mã SP)</label>
                <input 
                  type="text" 
                  value={formData.sku} 
                  onChange={(e) => setFormData({...formData, sku: e.target.value})}
                  disabled={modalMode === 'edit'}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-indigo-500 disabled:opacity-50"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Tên Sản Phẩm</label>
                <input 
                  type="text" 
                  value={formData.name} 
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Thương Hiệu</label>
                <input 
                  type="text" 
                  value={formData.brand} 
                  onChange={(e) => setFormData({...formData, brand: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Giá Bán (VNĐ)</label>
                <input 
                  type="text" 
                  value={formData.price} 
                  onChange={(e) => setFormData({...formData, price: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-indigo-500"
                  required
                />
              </div>
              <div className="flex gap-3 justify-end pt-4 border-t border-slate-700/50 mt-6">
                <button 
                  type="button" 
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-slate-700 text-slate-300 rounded-lg hover:bg-slate-600 transition-colors"
                >
                  Hủy Bỏ
                </button>
                <button 
                  type="submit" 
                  disabled={actionLoading}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 transition-colors shadow-[0_0_15px_rgba(79,70,229,0.3)] disabled:opacity-50 flex items-center gap-2"
                >
                  {actionLoading ? <RefreshCw size={16} className="animate-spin" /> : null}
                  {modalMode === 'add' ? 'Lưu Dữ Liệu' : 'Cập Nhật'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};

export default DataTable;
