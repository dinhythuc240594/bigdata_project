import React, { useState, useEffect } from 'react';
import { Save, Server, Database, Key, Shield } from 'lucide-react';

const Settings = () => {
  const [config, setConfig] = useState({
    hadoopIp: '192.168.1.100',
    hadoopUser: 'hadoop',
    hadoopKeyPath: '/home/hadoop/.ssh/id_rsa',
    mysqlHost: '127.0.0.1',
    mysqlPort: '3306',
    mysqlUser: 'root',
    mysqlPassword: '',
    mysqlDatabase: 'bigdata_project'
  });
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    // Attempt to load from localStorage if previously saved
    const saved = localStorage.getItem('bigdata_settings');
    if (saved) {
      try {
        setConfig(JSON.parse(saved));
      } catch (e) {
        console.error("Failed to parse settings", e);
      }
    }
  }, []);

  const handleChange = (e) => {
    setConfig({
      ...config,
      [e.target.name]: e.target.value
    });
  };

  const handleSave = () => {
    setIsSaving(true);
    // Simulate API call
    setTimeout(() => {
      localStorage.setItem('bigdata_settings', JSON.stringify(config));
      setIsSaving(false);
      alert('Đã lưu cấu hình hệ thống thành công!');
    }, 800);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-4xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Cài Đặt Hệ Thống</h1>
          <p className="text-slate-400 mt-1">Cấu hình kết nối SSH đến Hadoop và kết nối MySQL.</p>
        </div>
        <button 
          onClick={handleSave}
          disabled={isSaving}
          className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 transition-colors shadow-[0_0_15px_rgba(79,70,229,0.3)] disabled:opacity-50"
        >
          <Save size={18} />
          {isSaving ? 'Đang lưu...' : 'Lưu Thay Đổi'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Hadoop SSH Settings */}
        <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 rounded-2xl p-6 shadow-lg">
          <div className="flex items-center gap-3 mb-6 pb-4 border-b border-slate-700/50">
            <div className="p-2 bg-indigo-500/20 text-indigo-400 rounded-lg">
              <Server size={24} />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Cấu Hình Hadoop (SSH)</h2>
              <p className="text-sm text-slate-400">Tham số kết nối đến máy ảo Ubuntu</p>
            </div>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Địa chỉ IP (Hostname)</label>
              <input 
                type="text" 
                name="hadoopIp"
                value={config.hadoopIp}
                onChange={handleChange}
                className="w-full bg-slate-900/50 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-shadow"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Tài khoản (Username)</label>
              <input 
                type="text" 
                name="hadoopUser"
                value={config.hadoopUser}
                onChange={handleChange}
                className="w-full bg-slate-900/50 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-shadow"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Đường dẫn Private Key (id_rsa)</label>
              <div className="relative">
                <Key className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 w-4 h-4" />
                <input 
                  type="text" 
                  name="hadoopKeyPath"
                  value={config.hadoopKeyPath}
                  onChange={handleChange}
                  className="w-full bg-slate-900/50 border border-slate-700 text-white rounded-lg pl-10 pr-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-shadow"
                />
              </div>
            </div>
          </div>
        </div>

        {/* MySQL Settings */}
        <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 rounded-2xl p-6 shadow-lg">
          <div className="flex items-center gap-3 mb-6 pb-4 border-b border-slate-700/50">
            <div className="p-2 bg-emerald-500/20 text-emerald-400 rounded-lg">
              <Database size={24} />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Cấu Hình MySQL</h2>
              <p className="text-sm text-slate-400">Tham số kết nối đến Database Host</p>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div className="col-span-2">
                <label className="block text-sm font-medium text-slate-300 mb-1">Máy chủ (Host)</label>
                <input 
                  type="text" 
                  name="mysqlHost"
                  value={config.mysqlHost}
                  onChange={handleChange}
                  className="w-full bg-slate-900/50 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-shadow"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Port</label>
                <input 
                  type="text" 
                  name="mysqlPort"
                  value={config.mysqlPort}
                  onChange={handleChange}
                  className="w-full bg-slate-900/50 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-shadow"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Tài khoản</label>
                <input 
                  type="text" 
                  name="mysqlUser"
                  value={config.mysqlUser}
                  onChange={handleChange}
                  className="w-full bg-slate-900/50 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-shadow"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Mật khẩu</label>
                <div className="relative">
                  <Shield className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 w-4 h-4" />
                  <input 
                    type="password" 
                    name="mysqlPassword"
                    value={config.mysqlPassword}
                    onChange={handleChange}
                    className="w-full bg-slate-900/50 border border-slate-700 text-white rounded-lg pl-10 pr-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-shadow"
                  />
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Tên Database</label>
              <input 
                type="text" 
                name="mysqlDatabase"
                value={config.mysqlDatabase}
                onChange={handleChange}
                className="w-full bg-slate-900/50 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-shadow"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
