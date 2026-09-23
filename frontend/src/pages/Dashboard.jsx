import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area
} from 'recharts';
import { Activity, Users, FileText, Database, ArrowUpRight, ArrowDownRight, CloudDownload } from 'lucide-react';

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'];
const CHART_TEXT_COLOR = '#94a3b8';
const CHART_GRID_COLOR = '#334155';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-900/90 backdrop-blur-md border border-slate-700 p-3 rounded-xl shadow-xl">
        <p className="text-slate-300 font-medium mb-1">{label}</p>
        {payload.map((entry, index) => (
          <p key={index} style={{ color: entry.color }} className="text-sm font-semibold flex items-center gap-2">
            <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: entry.color }}></span>
            {entry.name}: {entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    fetch('http://localhost:8000/api/dashboard-stats/')
      .then(res => res.json())
      .then(result => {
        setData(result);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching dashboard stats", err);
        setLoading(false);
      });
  }, []);

  const handleRunAction = (actionUrl, actionName) => {
    setActionLoading(true);
    fetch(`http://localhost:8000/api/${actionUrl}`, { method: 'POST' })
      .then(res => res.json())
      .then(result => {
        setActionLoading(false);
        if (result.status === 'success') {
          alert(`${actionName} thành công!\nLogs: ${result.logs || result.message}`);
        } else {
          alert(`${actionName} lỗi:\n${result.message}\n${result.error_logs}`);
        }
      })
      .catch(err => {
        setActionLoading(false);
        alert(`Lỗi khi gọi API ${actionName}: ${err}`);
      });
  };

  if (loading || !data) {
    return <div className="text-white text-center py-20 text-xl font-medium animate-pulse">Đang tải dữ liệu hệ thống...</div>;
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Hệ Thống Phân Tích</h1>
          <p className="text-slate-400 mt-1">Tổng quan dữ liệu thời gian thực từ cụm Hadoop.</p>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={() => handleRunAction('run-sqoop/', 'Sqoop Import')}
            disabled={actionLoading}
            className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white px-5 py-2.5 rounded-lg font-medium transition-all shadow-[0_0_15px_rgba(16,185,129,0.3)] hover:shadow-[0_0_25px_rgba(16,185,129,0.5)] flex items-center gap-2">
            <CloudDownload size={18} />
            Chạy Sqoop Import
          </button>
          <button 
            onClick={() => handleRunAction('run-mapreduce/', 'MapReduce')}
            disabled={actionLoading}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white px-5 py-2.5 rounded-lg font-medium transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)] hover:shadow-[0_0_25px_rgba(79,70,229,0.5)] flex items-center gap-2">
            <Database size={18} />
            Chạy MapReduce Mới
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Tổng Lượng Dữ Liệu" value={data.kpis?.totalData || "0 GB"} icon={<Database />} trend={data.kpis?.totalDataTrend || "+0%"} isUp={data.kpis?.totalDataIsUp ?? true} />
        <StatCard title="Truy Vấn MapReduce" value={data.kpis?.mapReduceQueries || "0"} icon={<Activity />} trend={data.kpis?.mapReduceTrend || "+0%"} isUp={data.kpis?.mapReduceIsUp ?? true} />
        <StatCard title="Tài Khoản Đang Active" value={data.kpis?.activeAccounts || "0"} icon={<Users />} trend={data.kpis?.activeAccountsTrend || "0%"} isUp={data.kpis?.activeAccountsIsUp ?? false} />
        <StatCard title="Báo Cáo Đã Tạo" value={data.kpis?.reportsGenerated || "0"} icon={<FileText />} trend={data.kpis?.reportsTrend || "+0%"} isUp={data.kpis?.reportsIsUp ?? true} />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Main Area Chart - Spans 2 cols */}
        <div className="lg:col-span-2 bg-slate-800/40 backdrop-blur-md border border-slate-700/50 p-6 rounded-2xl shadow-lg relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 to-purple-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <h2 className="text-lg font-semibold text-slate-200 mb-6 font-heading">Lưu Lượng Truy Cập Trực Tuyến (Area)</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.areaData}>
                <defs>
                  <linearGradient id="colorTraffic" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={CHART_GRID_COLOR} />
                <XAxis dataKey="time" stroke={CHART_TEXT_COLOR} tick={{fill: CHART_TEXT_COLOR}} axisLine={false} />
                <YAxis stroke={CHART_TEXT_COLOR} tick={{fill: CHART_TEXT_COLOR}} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="traffic" name="Truy cập" stroke="#6366f1" strokeWidth={3} fillOpacity={1} fill="url(#colorTraffic)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Status Pie Chart */}
        <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 p-6 rounded-2xl shadow-lg group relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-emerald-500 to-teal-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <h2 className="text-lg font-semibold text-slate-200 mb-6 font-heading">Tiến Độ Xử Lý HDFS (Pie)</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={data.pieData1} cx="50%" cy="50%" innerRadius={70} outerRadius={100} dataKey="value" stroke="none">
                  {data.pieData1.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={['#10b981', '#334155'][index % 2]} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ color: CHART_TEXT_COLOR }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none mt-6">
              <span className="text-3xl font-bold text-white">75%</span>
            </div>
          </div>
        </div>

        {/* Double Line Chart */}
        <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 p-6 rounded-2xl shadow-lg group relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-pink-500 to-rose-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <h2 className="text-lg font-semibold text-slate-200 mb-6 font-heading">Hiệu Suất Job (Line)</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.lineData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={CHART_GRID_COLOR} />
                <XAxis dataKey="month" stroke={CHART_TEXT_COLOR} tick={{fill: CHART_TEXT_COLOR}} axisLine={false} />
                <YAxis stroke={CHART_TEXT_COLOR} tick={{fill: CHART_TEXT_COLOR}} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ color: CHART_TEXT_COLOR, paddingTop: '10px' }} />
                <Line type="monotone" dataKey="success" name="Thành công" stroke="#10b981" strokeWidth={3} dot={{r: 4, strokeWidth: 2}} activeDot={{r: 6}} />
                <Line type="monotone" dataKey="error" name="Lỗi" stroke="#ec4899" strokeWidth={3} dot={{r: 4, strokeWidth: 2}} activeDot={{r: 6}} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Bar Chart */}
        <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 p-6 rounded-2xl shadow-lg group relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-amber-400 to-orange-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <h2 className="text-lg font-semibold text-slate-200 mb-6 font-heading">Phân Bổ Dữ Liệu (Bar)</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.barData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={CHART_GRID_COLOR} />
                <XAxis dataKey="name" stroke={CHART_TEXT_COLOR} tick={{fill: CHART_TEXT_COLOR}} axisLine={false} />
                <YAxis stroke={CHART_TEXT_COLOR} tick={{fill: CHART_TEXT_COLOR}} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} cursor={{fill: '#334155', opacity: 0.4}} />
                <Bar dataKey="total" name="Lượt xem" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pie Chart 2 */}
        <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 p-6 rounded-2xl shadow-lg group relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-cyan-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <h2 className="text-lg font-semibold text-slate-200 mb-6 font-heading">Khu Vực Máy Chủ (Pie)</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={data.pieData2} cx="50%" cy="50%" outerRadius={90} dataKey="value" stroke="none" label>
                  {data.pieData2.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ color: CHART_TEXT_COLOR }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon, trend, isUp }) => (
  <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 p-6 rounded-2xl shadow-lg group hover:bg-slate-800/60 transition-all cursor-default">
    <div className="flex items-start justify-between">
      <div>
        <p className="text-slate-400 font-medium mb-1">{title}</p>
        <h3 className="text-3xl font-bold text-white font-heading">{value}</h3>
      </div>
      <div className="p-3 bg-slate-700/50 text-indigo-400 rounded-xl group-hover:scale-110 transition-transform">
        {icon}
      </div>
    </div>
    <div className="mt-4 flex items-center gap-1">
      <span className={`flex items-center text-sm font-medium ${isUp ? 'text-emerald-400' : 'text-rose-400'}`}>
        {isUp ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
        {trend}
      </span>
      <span className="text-slate-500 text-sm ml-1">so với tháng trước</span>
    </div>
  </div>
);

export default Dashboard;
