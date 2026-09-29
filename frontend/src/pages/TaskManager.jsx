import React, { useState, useEffect } from 'react';
import { Play, CheckCircle2, XCircle, Clock, RefreshCw, AlertCircle, FileText } from 'lucide-react';

const TaskManager = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchTasks = () => {
    setLoading(true);
    fetch('http://localhost:8000/api/job-history/')
      .then(res => res.json())
      .then(data => {
        setTasks(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleRunTask = async (task) => {
    if (task.type === 'Sqoop') {
      alert(`Đang bắt đầu chạy: ${task.name} (Bảng: ${task.tableName})...\nVui lòng chờ, quá trình này có thể mất vài phút.`);
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
                table_name: task.tableName, // Lấy tên bảng linh động từ task
                target_dir: `/user/hadoopthuc/project/input_${task.tableName}`
            })
        });
        const data = await response.json();
        if (data.status === "success") {
            alert("Chạy Sqoop thành công!\n\nLog: " + data.logs);
        } else {
            alert("Lỗi khi chạy Sqoop:\n\n" + data.error_logs);
        }
      } catch (error) {
        alert("Lỗi kết nối tới Server: " + error);
      }
    } else if (task.type === 'MapReduce') {
      alert(`Đang bắt đầu chạy: ${task.name}...\nQuá trình xử lý MapReduce có thể mất vài phút.`);
      try {
        const settings = JSON.parse(localStorage.getItem('bigdata_settings')) || {};
        const response = await fetch('http://localhost:8000/api/run-mapreduce/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                hadoop_host: settings.hadoopIp || '192.168.10.10',
                hadoop_user: settings.hadoopUser || 'hadoopthuc',
                input_dir: `/user/hadoopthuc/project/input_laptop_products_common`,
                output_dir: `/user/hadoopthuc/project/output_laptop_stats`
            })
        });
        const data = await response.json();
        if (data.status === "success") {
            alert("Chạy MapReduce thành công!\n\nKết quả (10 dòng đầu):\n" + data.logs.substring(0, 500));
        } else {
            alert("Lỗi khi chạy MapReduce:\n\n" + data.error_logs);
        }
      } catch (error) {
        alert("Lỗi kết nối tới Server: " + error);
      }
    } else if (task.type === 'Hive') {
      alert(`Đang bắt đầu chạy: ${task.name}...\nQuá trình xử lý Hive có thể mất vài phút.`);
      try {
        const response = await fetch('http://localhost:8000/api/run-hive/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ table_name: task.tableName })
        });
        const data = await response.json();
        if (data.status === "success") {
            alert("Chạy Hive thành công!\n\nLogs:\n" + data.logs.substring(0, 500));
        } else {
            alert("Lỗi khi chạy Hive:\n\n" + data.error_logs);
        }
      } catch (error) {
        alert("Lỗi kết nối tới Server: " + error);
      }
    } else if (task.type === 'Pig') {
      alert(`Đang bắt đầu chạy: ${task.name}...\nQuá trình xử lý Pig có thể mất vài phút.`);
      try {
        const response = await fetch('http://localhost:8000/api/run-pig/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ table_name: task.tableName })
        });
        const data = await response.json();
        if (data.status === "success") {
            alert("Chạy Pig thành công!\n\nLogs:\n" + data.logs.substring(0, 500));
        } else {
            alert("Lỗi khi chạy Pig:\n\n" + data.error_logs);
        }
      } catch (error) {
        alert("Lỗi kết nối tới Server: " + error);
      }
    } else if (task.type === 'Spark') {
      alert(`Đang bắt đầu chạy: ${task.name}...\nQuá trình xử lý Spark có thể mất vài phút.`);
      try {
        const response = await fetch('http://localhost:8000/api/run-spark/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ table_name: task.tableName })
        });
        const data = await response.json();
        if (data.status === "success") {
            alert("Chạy Spark thành công!\n\nLogs:\n" + data.logs.substring(0, 500));
        } else {
            alert("Lỗi khi chạy Spark:\n\n" + data.error_logs);
        }
      } catch (error) {
        alert("Lỗi kết nối tới Server: " + error);
      }
    } else {
      alert("Chức năng đang được phát triển!");
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Quản Lý Tác Vụ (Task Manager)</h1>
          <p className="text-slate-400 mt-1">Theo dõi tiến trình MapReduce và Sqoop trên cụm Hadoop.</p>
        </div>
        <button onClick={fetchTasks} className="flex items-center gap-2 px-4 py-2 bg-slate-800 text-slate-200 rounded-lg hover:bg-slate-700 transition-colors border border-slate-700">
          <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
          Làm Mới
        </button>
      </div>

      {/* Stats Cards... */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 p-6 rounded-2xl flex items-center gap-4">
          <div className="p-3 bg-emerald-500/20 text-emerald-400 rounded-xl"><CheckCircle2 size={24} /></div>
          <div><p className="text-slate-400 text-sm font-medium">Hoàn thành</p><p className="text-2xl font-bold text-white">{tasks.filter(t => t.status === 'Completed').length}</p></div>
        </div>
        <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 p-6 rounded-2xl flex items-center gap-4">
          <div className="p-3 bg-indigo-500/20 text-indigo-400 rounded-xl"><RefreshCw size={24} className="animate-spin-slow" /></div>
          <div><p className="text-slate-400 text-sm font-medium">Đang chạy</p><p className="text-2xl font-bold text-white">{tasks.filter(t => t.status === 'Running' || t.status === 'Pending').length}</p></div>
        </div>
        <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 p-6 rounded-2xl flex items-center gap-4">
          <div className="p-3 bg-rose-500/20 text-rose-400 rounded-xl"><AlertCircle size={24} /></div>
          <div><p className="text-slate-400 text-sm font-medium">Thất bại</p><p className="text-2xl font-bold text-white">{tasks.filter(t => t.status === 'Failed').length}</p></div>
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
              {tasks.map((task, i) => (
                <tr key={task.id} className={`border-b border-slate-700/50 hover:bg-slate-800/50 transition-colors ${i % 2 === 0 ? 'bg-transparent' : 'bg-slate-800/20'}`}>
                  <td className="px-6 py-4 font-mono font-medium text-indigo-400">{task.id}</td>
                  <td className="px-6 py-4 font-medium text-slate-200">{task.name}</td>
                  <td className="px-6 py-4">
                    <span className="px-2.5 py-1 bg-slate-700/50 rounded-md text-xs font-medium border border-slate-600/50">{task.type}</span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {task.status === 'Completed' && <CheckCircle2 size={16} className="text-emerald-400" />}
                      {task.status === 'Running' && <RefreshCw size={16} className="text-indigo-400 animate-spin" />}
                      {task.status === 'Failed' && <XCircle size={16} className="text-rose-400" />}
                      {task.status === 'Pending' && <Clock size={16} className="text-slate-400" />}
                      <span className={`font-medium ${task.status === 'Completed' ? 'text-emerald-400' : task.status === 'Running' ? 'text-indigo-400' : task.status === 'Failed' ? 'text-rose-400' : 'text-slate-400'}`}>{task.status}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-slate-400">{task.startTime}</td>
                  <td className="px-6 py-4 text-slate-400 font-mono">{task.duration}</td>
                  <td className="px-6 py-4 text-center">
                    {task.status === 'Failed' || task.status === 'Completed' ? (
                      <button onClick={() => {
                        if(task.logs) {
                          alert(`Log chi tiết:\n\n${task.logs}`);
                        } else {
                          alert("Không có dữ liệu Log!");
                        }
                      }} className="flex items-center justify-center w-full gap-1 p-1.5 text-xs text-slate-300 hover:text-white bg-slate-700 hover:bg-slate-600 rounded transition-colors">
                        <FileText size={14} /> Xem Log
                      </button>
                    ) : (
                      <button className="flex items-center justify-center w-full gap-1 p-1.5 text-xs text-slate-400 bg-slate-800 rounded transition-colors cursor-not-allowed" disabled>
                        <Clock size={14} /> Đang chạy
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
