import React, { useState } from 'react';
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area
} from 'recharts';
import { Activity, Users, FileText, Database, ArrowUpRight, ArrowDownRight } from 'lucide-react';

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
  const [data] = useState({
    barData: [
      { name: 'Loại A', total: 4000 }, { name: 'Loại B', total: 3000 },
      { name: 'Loại C', total: 2000 }, { name: 'Loại D', total: 2780 },
    ],
    lineData: [
      { month: 'T1', success: 240, error: 40 },
      { month: 'T2', success: 139, error: 30 },
      { month: 'T3', success: 380, error: 20 },
      { month: 'T4', success: 390, error: 27 },
      { month: 'T5', success: 480, error: 18 },
      { month: 'T6', success: 520, error: 15 },
    ],
    pieData1: [
      { name: 'Đã xử lý', value: 75 }, { name: 'Chờ xử lý', value: 25 }
    ],
    pieData2: [
      { name: 'Hà Nội', value: 45 }, { name: 'TP.HCM', value: 35 }, { name: 'Đà Nẵng', value: 20 }
    ],
    areaData: [
      { time: '00:00', traffic: 1200 }, { time: '04:00', traffic: 800 },
      { time: '08:00', traffic: 3200 }, { time: '12:00', traffic: 4500 },
      { time: '16:00', traffic: 3900 }, { time: '20:00', traffic: 2800 },
    ]
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Hệ Thống Phân Tích</h1>
          <p className="text-slate-400 mt-1">Tổng quan dữ liệu thời gian thực từ cụm Hadoop.</p>
        </div>
        <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-lg font-medium transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)] hover:shadow-[0_0_25px_rgba(79,70,229,0.5)] flex items-center gap-2">
          <Database size={18} />
          Chạy MapReduce Mới
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Tổng Lượng Dữ Liệu" value="124.5 GB" icon={<Database />} trend="+12.5%" isUp={true} />
        <StatCard title="Truy Vấn MapReduce" value="1,432" icon={<Activity />} trend="+8.2%" isUp={true} />
        <StatCard title="Tài Khoản Đang Active" value="8,924" icon={<Users />} trend="-2.4%" isUp={false} />
        <StatCard title="Báo Cáo Đã Tạo" value="356" icon={<FileText />} trend="+15.3%" isUp={true} />
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
