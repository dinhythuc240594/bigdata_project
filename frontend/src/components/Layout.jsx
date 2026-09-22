import React from 'react';
import { LayoutDashboard, Database, HardDrive, Settings, Search, Bell, User } from 'lucide-react';

const Layout = ({ children }) => {
  return (
    <div className="flex h-screen bg-slate-900 text-slate-100 font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-950/50 backdrop-blur-xl border-r border-slate-800/60 flex flex-col transition-all duration-300">
        <div className="h-16 flex items-center px-6 border-b border-slate-800/60">
          <div className="flex items-center gap-2 text-indigo-400 font-bold text-xl tracking-tight">
            <Database className="w-6 h-6" />
            <span>BigData Pro</span>
          </div>
        </div>
        
        <nav className="flex-1 py-6 px-4 flex flex-col gap-2">
          <NavItem icon={<LayoutDashboard size={20} />} label="Dashboard" active />
          <NavItem icon={<Database size={20} />} label="Data Table" />
          <NavItem icon={<HardDrive size={20} />} label="Task Manager" />
          <NavItem icon={<Settings size={20} />} label="Settings" />
        </nav>
        
        <div className="p-4 border-t border-slate-800/60">
          <div className="flex items-center gap-3 p-2 rounded-lg bg-slate-800/30">
            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center font-bold">
              AD
            </div>
            <div>
              <p className="text-sm font-medium">Admin User</p>
              <p className="text-xs text-slate-400">System Admin</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        {/* Decorative background gradients */}
        <div className="absolute top-0 inset-x-0 h-64 bg-gradient-to-b from-indigo-900/20 to-transparent -z-10" />
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-purple-500/10 blur-[100px] rounded-full -z-10 mix-blend-screen" />
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-blue-500/10 blur-[100px] rounded-full -z-10 mix-blend-screen" />

        {/* Header */}
        <header className="h-16 flex items-center justify-between px-8 border-b border-slate-800/30 bg-slate-900/50 backdrop-blur-md z-10">
          <div className="flex items-center bg-slate-800/50 border border-slate-700/50 rounded-full px-4 py-2 w-96 focus-within:ring-2 focus-within:ring-indigo-500/50 transition-all">
            <Search className="w-4 h-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search data, jobs..." 
              className="bg-transparent border-none outline-none text-sm text-slate-200 ml-2 w-full placeholder:text-slate-500"
            />
          </div>
          
          <div className="flex items-center gap-4">
            <button className="p-2 text-slate-400 hover:text-slate-200 transition-colors relative">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-pink-500 rounded-full"></span>
            </button>
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

const NavItem = ({ icon, label, active }) => {
  return (
    <button className={`
      flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 w-full text-left
      ${active 
        ? 'bg-gradient-to-r from-indigo-500/20 to-purple-500/10 text-indigo-300 border border-indigo-500/20 shadow-[0_0_15px_rgba(99,102,241,0.1)]' 
        : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'}
    `}>
      {icon}
      <span className="font-medium text-sm">{label}</span>
    </button>
  );
};

export default Layout;
