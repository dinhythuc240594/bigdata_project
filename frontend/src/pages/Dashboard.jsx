import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area
} from 'recharts';
import { Activity, Users, FileText, Database, ArrowUpRight, ArrowDownRight, CloudDownload, Server, CheckCircle2, XCircle, Play } from 'lucide-react';

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'];
const CHART_TEXT_COLOR = '#94a3b8';
const CHART_GRID_COLOR = '#e2e8f0';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-slate-200 p-3 rounded shadow-sm">
        <p className="text-slate-800 font-medium mb-1">{label}</p>
        {payload.map((entry, index) => (
          <p key={index} style={{ color: entry.color }} className="text-sm font-semibold flex items-center gap-2">
            <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: entry.color }}></span>
            {entry.name}: {typeof entry.value === 'number' && entry.value > 1000 ? entry.value.toLocaleString('vi-VN') : entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [clusterData, setClusterData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [runningJob, setRunningJob] = useState(null);

  const fetchDashboardData = () => {
    return fetch(`http://${window.location.hostname}:8000/api/dashboard-stats/`).then(res => res.json());
  };

  useEffect(() => {
    Promise.all([
      fetchDashboardData(),
      fetch(`http://${window.location.hostname}:8000/api/cluster-status/`).then(res => res.json())
    ])
    .then(([stats, cluster]) => {
      setData(stats);
      setClusterData(cluster.nodes || []);
      setLoading(false);
    })
    .catch(err => {
      console.error("Error fetching dashboard data", err);
      setLoading(false);
    });
  }, []);

  const handleRunJob = (jobId, jobName) => {
    setRunningJob(jobId);
    fetch(`http://${window.location.hostname}:8000/api/run-dashboard-job/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_id: jobId })
    })
    .then(res => res.json())
    .then(result => {
      if (result.status === 'success') {
        alert(result.message);
        // Refresh data
        fetchDashboardData().then(stats => {
          setData(stats);
          setRunningJob(null);
        });
      } else {
        alert(`Lỗi chạy Job: ${result.message}`);
        setRunningJob(null);
      }
    })
    .catch(err => {
      alert(`Lỗi mạng: ${err}`);
      setRunningJob(null);
    });
  };

  if (loading || !data) {
    return <div className="text-slate-800 text-center py-20 text-xl font-medium animate-pulse">Đang tải dữ liệu từ Hadoop...</div>;
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-10">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">

        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Trung Tâm Phân Tích Big Data</h1>
          <p className="text-slate-500 mt-1">Các biểu đồ so sánh đối thủ cạnh tranh (TGDĐ vs Phong Vũ)</p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Tổng Dữ Liệu" value={data.kpis?.totalData} icon={<Database />} trend={data.kpis?.totalDataTrend} isUp={true} />
        <StatCard title="Tiến Trình MapReduce" value={data.kpis?.mapReduceQueries} icon={<Activity />} trend={data.kpis?.mapReduceTrend} isUp={true} />
        <StatCard title="Phân Tích Đối Thủ" value="TGDĐ / Phong Vũ" icon={<Users />} trend="Real-time" isUp={true} />
        <StatCard title="Trạng Thái Report" value={data.kpis?.reportsGenerated} icon={<FileText />} trend={data.kpis?.reportsTrend} isUp={true} />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Chart 1: Grouped Bar (Price Comparison) */}
        <div className="bg-white border border-slate-200 p-6 rounded shadow-sm relative overflow-hidden">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-semibold text-slate-800">1. So sánh Giá bán (TGDĐ vs Phong Vũ)</h2>
            <button 
              onClick={() => handleRunJob(1, 'So sánh Giá bán')}
              disabled={runningJob !== null}
              className="bg-orange-500 hover:bg-orange-600 disabled:opacity-50 text-white px-3 py-1.5 rounded text-sm font-medium transition-all flex items-center gap-2">
              {runningJob === 1 ? <Activity className="animate-spin w-4 h-4" /> : <Play className="w-4 h-4" />}
              Chạy MapReduce
            </button>
          </div>
          <div className="h-72">
            {data.chart1 && data.chart1.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.chart1}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={CHART_GRID_COLOR} />
                  <XAxis dataKey="name" stroke="#64748b" tick={{fill: "#64748b"}} />
                  <YAxis stroke="#64748b" tick={{fill: "#64748b"}} tickFormatter={(val) => `${(val/1000000).toFixed(0)}M`} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Bar dataKey="tgdd" name="TGDĐ (VNĐ)" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="pv" name="Phong Vũ (VNĐ)" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded">
                Chưa có dữ liệu. Vui lòng bấm Chạy MapReduce.
              </div>
            )}
          </div>
        </div>

        {/* Chart 2: Doughnut (Volume Comparison) */}
        <div className="bg-white border border-slate-200 p-6 rounded shadow-sm relative overflow-hidden">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-semibold text-slate-800">2. So sánh Kho Hàng (Sản phẩm)</h2>
            <button 
              onClick={() => handleRunJob(2, 'So sánh Kho Hàng')}
              disabled={runningJob !== null}
              className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-3 py-1.5 rounded text-sm font-medium transition-all flex items-center gap-2">
              {runningJob === 2 ? <Activity className="animate-spin w-4 h-4" /> : <Play className="w-4 h-4" />}
              Chạy MapReduce
            </button>
          </div>
          <div className="h-72">
            {data.chart2 && data.chart2.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={data.chart2} cx="50%" cy="50%" innerRadius={70} outerRadius={110} dataKey="value" paddingAngle={5}>
                    {data.chart2.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={index === 0 ? '#f59e0b' : '#3b82f6'} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded">
                Chưa có dữ liệu. Vui lòng bấm Chạy MapReduce.
              </div>
            )}
          </div>
        </div>

        {/* Chart 3: Area Chart (Rating Trend) */}
        <div className="bg-white border border-slate-200 p-6 rounded shadow-sm relative overflow-hidden lg:col-span-2">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-semibold text-slate-800">3. Xu Hướng Điểm Đánh Giá (Rating) Theo Hãng</h2>
            <button 
              onClick={() => handleRunJob(3, 'Rating Trend')}
              disabled={runningJob !== null}
              className="bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white px-3 py-1.5 rounded text-sm font-medium transition-all flex items-center gap-2">
              {runningJob === 3 ? <Activity className="animate-spin w-4 h-4" /> : <Play className="w-4 h-4" />}
              Chạy MapReduce
            </button>
          </div>
          <div className="h-80">
            {data.chart3 && data.chart3.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data.chart3}>
                  <defs>
                    <linearGradient id="colorRating" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.5}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={CHART_GRID_COLOR} />
                  <XAxis dataKey="name" stroke="#64748b" />
                  <YAxis stroke="#64748b" domain={[0, 5]} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="value" name="Điểm Đánh Giá (Sao)" stroke="#10b981" fillOpacity={1} fill="url(#colorRating)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded">
                Chưa có dữ liệu. Vui lòng bấm Chạy MapReduce.
              </div>
            )}
          </div>
        </div>

        {/* Chart 4: Radar (Top Brands) */}
        <div className="bg-white border border-slate-200 p-6 rounded shadow-sm relative overflow-hidden">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-semibold text-slate-800">4. Độ Phủ Thương Hiệu (Radar)</h2>
            <button 
              onClick={() => handleRunJob(4, 'Độ Phủ Thương Hiệu')}
              disabled={runningJob !== null}
              className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white px-3 py-1.5 rounded text-sm font-medium transition-all flex items-center gap-2">
              {runningJob === 4 ? <Activity className="animate-spin w-4 h-4" /> : <Play className="w-4 h-4" />}
              Chạy MapReduce
            </button>
          </div>
          <div className="h-72">
            {data.chart4 && data.chart4.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="70%" data={data.chart4}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="name" />
                  <PolarRadiusAxis />
                  <Radar name="Số Lượng Mẫu Mã" dataKey="value" stroke="#6366f1" fill="#6366f1" fillOpacity={0.6} />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded">
                Chưa có dữ liệu. Vui lòng bấm Chạy MapReduce.
              </div>
            )}
          </div>
        </div>

        {/* Chart 5: Category Dist */}
        <div className="bg-white border border-slate-200 p-6 rounded shadow-sm relative overflow-hidden">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-semibold text-slate-800">5. Tỷ Trọng Danh Mục Toàn Cụm</h2>
            <button 
              onClick={() => handleRunJob(5, 'Danh Mục')}
              disabled={runningJob !== null}
              className="bg-pink-600 hover:bg-pink-700 disabled:opacity-50 text-white px-3 py-1.5 rounded text-sm font-medium transition-all flex items-center gap-2">
              {runningJob === 5 ? <Activity className="animate-spin w-4 h-4" /> : <Play className="w-4 h-4" />}
              Chạy MapReduce
            </button>
          </div>
          <div className="h-72">
            {data.chart5 && data.chart5.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={data.chart5} cx="50%" cy="50%" outerRadius={100} dataKey="value" label>
                    {data.chart5.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded">
                Chưa có dữ liệu. Vui lòng bấm Chạy MapReduce.
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Danger Zone */}
      <div className="mt-12 pt-8 border-t border-slate-200 flex justify-end">
        <button 
          onClick={() => handleRunJob('reset', 'Xóa toàn bộ biểu đồ')}
          disabled={runningJob !== null}
          className="bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 disabled:opacity-50 px-5 py-2.5 rounded font-medium transition-all shadow-sm flex items-center gap-2">
          <XCircle size={18} />
          Reset Dashboard (Xóa Data)
        </button>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon, trend, isUp }) => (
  <div className="bg-white border border-slate-200 p-6 rounded shadow-sm">
    <div className="flex items-start justify-between">
      <div>
        <p className="text-slate-500 font-medium mb-1">{title}</p>
        <h3 className="text-3xl font-bold text-slate-900 font-heading">{value || '0'}</h3>
      </div>
      <div className="p-3 bg-blue-50 text-blue-600 rounded">
        {icon}
      </div>
    </div>
    <div className="mt-4 flex items-center gap-1">
      <span className={`flex items-center text-sm font-semibold ${isUp ? 'text-emerald-600' : 'text-red-600'}`}>
        {isUp ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
        {trend}
      </span>
    </div>
  </div>
);

export default Dashboard;

