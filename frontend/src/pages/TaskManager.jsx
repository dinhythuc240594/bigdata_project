import React from 'react';
import { Play, CheckCircle2, XCircle, Clock, RefreshCw, AlertCircle } from 'lucide-react';

const TASKS = [
  { id: 'JOB-9021', name: 'Sqoop Import: TheGioiDiDong_Laptop', type: 'Sqoop', status: 'Completed', startTime: '2023-11-15 08:30:00', duration: '2m 15s' },
  { id: 'JOB-9022', name: 'Sqoop Import: PhongVu_Laptop', type: 'Sqoop', status: 'Completed', startTime: '2023-11-15 08:35:00', duration: '1m 45s' },
  { id: 'JOB-9023', name: 'MapReduce: Clean_Laptop_Data', type: 'MapReduce', status: 'Running', startTime: '2023-11-15 08:40:00', duration: 'In Progress' },
  { id: 'JOB-9024', name: 'Sqoop Import: TheGioiDiDong_Keyboard', type: 'Sqoop', status: 'Pending', startTime: '-', duration: '-' },
  { id: 'JOB-9019', name: 'MapReduce: Aggregate_Monitor_Prices', type: 'MapReduce', status: 'Failed', startTime: '2023-11-14 22:00:00', duration: '45s' },
];

const TaskManager = () => {
  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Quản Lý Tác Vụ (Task Manager)</h1>
          <p className="text-slate-400 mt-1">Theo dõi tiến trình MapReduce và Sqoop trên cụm Hadoop.</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-slate-800 text-slate-200 rounded-lg hover:bg-slate-700 transition-colors border border-slate-700">
          <RefreshCw size={16} />
          Làm Mới
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 p-6 rounded-2xl flex items-center gap-4">
          <div className="p-3 bg-emerald-500/20 text-emerald-400 rounded-xl">
            <CheckCircle2 size={24} />
          </div>
          <div>
            <p className="text-slate-400 text-sm font-medium">Hoàn thành</p>
            <p className="text-2xl font-bold text-white">1,245</p>
          </div>
        </div>
        <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 p-6 rounded-2xl flex items-center gap-4">
          <div className="p-3 bg-indigo-500/20 text-indigo-400 rounded-xl">
            <RefreshCw size={24} className="animate-spin-slow" />
          </div>
          <div>
            <p className="text-slate-400 text-sm font-medium">Đang chạy</p>
            <p className="text-2xl font-bold text-white">1</p>
          </div>
        </div>
        <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 p-6 rounded-2xl flex items-center gap-4">
          <div className="p-3 bg-rose-500/20 text-rose-400 rounded-xl">
            <AlertCircle size={24} />
          </div>
          <div>
            <p className="text-slate-400 text-sm font-medium">Thất bại</p>
            <p className="text-2xl font-bold text-white">23</p>
          </div>
        </div>
      </div>

      <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 rounded-2xl shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="text-xs text-slate-400 uppercase bg-slate-800/50 border-b border-slate-700/50">
              <tr>
                <th className="px-6 py-4">Job ID</th>
                <th className="px-6 py-4">Tên Tác Vụ</th>
                <th className="px-6 py-4">Loại</th>
                <th className="px-6 py-4">Trạng Thái</th>
                <th className="px-6 py-4">Thời Gian Bắt Đầu</th>
                <th className="px-6 py-4">Thời Lượng</th>
                <th className="px-6 py-4 text-center">Hành Động</th>
              </tr>
            </thead>
            <tbody>
              {TASKS.map((task, i) => (
                <tr key={task.id} className={`border-b border-slate-700/50 hover:bg-slate-800/50 transition-colors ${i % 2 === 0 ? 'bg-transparent' : 'bg-slate-800/20'}`}>
                  <td className="px-6 py-4 font-mono font-medium text-indigo-400">{task.id}</td>
                  <td className="px-6 py-4 font-medium text-slate-200">{task.name}</td>
                  <td className="px-6 py-4">
                    <span className="px-2.5 py-1 bg-slate-700/50 rounded-md text-xs font-medium border border-slate-600/50">
                      {task.type}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {task.status === 'Completed' && <CheckCircle2 size={16} className="text-emerald-400" />}
                      {task.status === 'Running' && <RefreshCw size={16} className="text-indigo-400 animate-spin" />}
                      {task.status === 'Failed' && <XCircle size={16} className="text-rose-400" />}
                      {task.status === 'Pending' && <Clock size={16} className="text-slate-400" />}
                      
                      <span className={`font-medium ${
                        task.status === 'Completed' ? 'text-emerald-400' : 
                        task.status === 'Running' ? 'text-indigo-400' :
                        task.status === 'Failed' ? 'text-rose-400' : 'text-slate-400'
                      }`}>
                        {task.status}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-slate-400">{task.startTime}</td>
                  <td className="px-6 py-4 text-slate-400 font-mono">{task.duration}</td>
                  <td className="px-6 py-4 text-center">
                    {task.status === 'Failed' || task.status === 'Completed' ? (
                      <button className="flex items-center justify-center w-full gap-1 p-1.5 text-xs text-slate-300 hover:text-white bg-slate-700 hover:bg-slate-600 rounded transition-colors">
                        <Play size={14} /> Chạy lại
                      </button>
                    ) : (
                      <button className="flex items-center justify-center w-full gap-1 p-1.5 text-xs text-rose-400 hover:text-rose-300 bg-rose-500/10 hover:bg-rose-500/20 rounded transition-colors" disabled={task.status === 'Pending'}>
                        <XCircle size={14} /> Dừng
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default TaskManager;
