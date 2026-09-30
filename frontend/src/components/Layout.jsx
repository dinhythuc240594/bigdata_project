import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Database, HardDrive, Settings, Search, Bell, User, RefreshCw, Menu } from 'lucide-react';

const Layout = ({ children }) => {
  const location = useLocation();
  const [activeTasks, setActiveTasks] = useState([]);
  const [showTasks, setShowTasks] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const res = await fetch('http://192.168.10.5:8000/api/active-tasks/');
        if(res.ok) {
          const data = await res.json();
          setActiveTasks(data);
        }
      } catch (err) {}
    };
    fetchTasks();
    const interval = setInterval(fetchTasks, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex h-screen bg-slate-50 text-slate-800 font-sans">
      {/* Sidebar */}
      <aside className={`bg-blue-900 text-blue-50 flex flex-col transition-all duration-300 shadow-xl z-20 ${isCollapsed ? 'w-20' : 'w-64'}`}>
        <div className={`h-16 flex items-center border-b border-blue-800 ${isCollapsed ? 'justify-center px-0' : 'px-4 justify-between'}`}>
          {!isCollapsed && (
            <div className="flex items-center gap-2 text-white font-bold text-xl tracking-tight">
              <Database className="w-6 h-6 flex-shrink-0" />
              <span>BigData</span>
            </div>
          )}
          <button 
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 text-blue-200 hover:text-white hover:bg-blue-800 rounded-lg transition-colors"
            title="Toggle Menu"
          >
            <Menu className="w-5 h-5" />
          </button>
        </div>
        
        <nav className="flex-1 py-6 px-4 flex flex-col gap-1">
          <NavItem icon={<LayoutDashboard size={20} />} label="Dashboard" to="/" active={location.pathname === '/'} isCollapsed={isCollapsed} />
          <NavItem icon={<Database size={20} />} label="Data Table" to="/data-table" active={location.pathname === '/data-table'} isCollapsed={isCollapsed} />
          <NavItem icon={<HardDrive size={20} />} label="Task Manager" to="/task-manager" active={location.pathname === '/task-manager'} isCollapsed={isCollapsed} />
          <NavItem icon={<Search size={20} />} label="Query Editor" to="/query-editor" active={location.pathname === '/query-editor'} isCollapsed={isCollapsed} />
          <NavItem icon={<Settings size={20} />} label="Settings" to="/settings" active={location.pathname === '/settings'} isCollapsed={isCollapsed} />
        </nav>
        
        <div className="p-4 border-t border-blue-800">
          <div className={`flex items-center ${isCollapsed ? 'justify-center p-0 w-10 h-10 mx-auto' : 'gap-3 p-2'} rounded-lg bg-blue-800/50 hover:bg-blue-800 transition-colors cursor-pointer`} title={isCollapsed ? "Admin User" : undefined}>
            <div className="w-10 h-10 rounded-full bg-white text-blue-900 flex items-center justify-center font-bold flex-shrink-0">
              AD
            </div>
            {!isCollapsed && (
              <div className="overflow-hidden">
                <p className="text-sm font-medium text-white whitespace-nowrap">Admin User</p>
                <p className="text-xs text-blue-300 whitespace-nowrap">System Admin</p>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden relative bg-slate-50">
        {/* Header */}
        <header className="h-16 flex items-center justify-end px-8 border-b border-slate-200 bg-white z-50 shadow-sm relative">
          
          <div className="flex items-center gap-4 relative">
            <button 
              onClick={() => setShowTasks(!showTasks)}
              className="p-2 text-slate-500 hover:text-slate-800 transition-colors relative"
            >
              <Bell className="w-5 h-5" />
              {activeTasks.length > 0 && (
                <span className="absolute top-0 right-0 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center text-[10px] font-bold text-white shadow-sm animate-pulse">
                  {activeTasks.length}
                </span>
              )}
            </button>

            {/* Dropdown thông báo Task */}
            {showTasks && (
              <div className="absolute top-full right-0 mt-2 w-72 bg-white border border-slate-200 rounded-xl shadow-lg overflow-hidden z-50">
                <div className="p-3 border-b border-slate-200 bg-slate-50 flex justify-between items-center">
                  <span className="text-sm font-semibold text-slate-800">Tiến trình đang chạy</span>
                  <span className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">{activeTasks.length} tasks</span>
                </div>
                <div className="max-h-64 overflow-y-auto custom-scrollbar">
                  {activeTasks.length === 0 ? (
                    <div className="p-4 text-center text-sm text-slate-500">
                      Không có tiến trình nào đang chạy.
                    </div>
                  ) : (
                    activeTasks.map(task => (
                      <div key={task.id} className="p-3 border-b border-slate-100 hover:bg-slate-50 transition-colors flex items-start gap-3">
                        <div className="mt-1">
                          <RefreshCw className="w-4 h-4 text-blue-600 animate-spin" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-slate-800 truncate pr-2">{task.name}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs text-slate-500">Bắt đầu: {task.startTime}</span>
                            <span className="text-[10px] font-mono bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded">RUNNING</span>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
        </header>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-8 z-10 custom-scrollbar">
          {children}
        </div>
      </main>
    </div>
  );
};

const NavItem = ({ icon, label, to, active, isCollapsed }) => {
  return (
    <Link to={to} className={`
      flex items-center ${isCollapsed ? 'justify-center px-0' : 'gap-3 px-4'} py-3 rounded transition-all duration-200 w-full text-left
      ${active 
        ? 'bg-blue-800/80 text-white font-semibold' 
        : 'text-blue-200 hover:bg-blue-800/40 hover:text-white'}
    `} title={isCollapsed ? label : undefined}>
      {icon}
      {!isCollapsed && <span className="font-medium text-sm whitespace-nowrap">{label}</span>}
    </Link>
  );
};

export default Layout;
