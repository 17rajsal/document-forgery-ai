import React from 'react';
import {
  ShieldCheck,
  FilePlus,
  History,
  FolderOpen,
  FileCode,
  HelpCircle,
  Settings,
  Lock,
  ExternalLink,
  CheckCircle2,
  X
} from 'lucide-react';

export default function Sidebar({
  activeNav,
  setActiveNav,
  historyCount = 0,
  backendStatus,
  onNewAnalysis,
  mobileOpen,
  setMobileOpen
}) {
  const navItems = [
    { id: 'new-analysis', label: 'New Analysis', icon: FilePlus, action: onNewAnalysis },
    { id: 'history', label: 'Analysis History', icon: History, count: historyCount },
    { id: 'samples', label: 'Sample Documents', icon: FolderOpen },
    { id: 'formats', label: 'Supported Formats', icon: FileCode },
    { id: 'how-it-works', label: 'How It Works', icon: HelpCircle },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  const handleItemClick = (item) => {
    if (item.action) {
      item.action();
    } else {
      setActiveNav(item.id);
    }
    if (setMobileOpen) setMobileOpen(false);
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div
          onClick={() => setMobileOpen(false)}
          className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-40 lg:hidden"
        />
      )}

      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-white border-r border-slate-200/80 flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static ${
          mobileOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-violet-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-base tracking-tight text-slate-900">DocShield</span>
                <span className="text-xs font-semibold px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-100">
                  AI
                </span>
              </div>
              <p className="text-[11px] text-slate-500 font-medium truncate max-w-[130px]">
                Document Authenticity
              </p>
            </div>
          </div>

          {/* Close button on mobile */}
          <button
            onClick={() => setMobileOpen(false)}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 lg:hidden"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Primary Action Button */}
        <div className="p-4">
          <button
            onClick={() => {
              onNewAnalysis();
              if (setMobileOpen) setMobileOpen(false);
            }}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-medium text-sm shadow-sm shadow-blue-600/25 transition cursor-pointer"
          >
            <FilePlus className="h-4 w-4" />
            <span>New Analysis</span>
          </button>
        </div>

        {/* Navigation List */}
        <nav className="flex-1 px-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeNav === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleItemClick(item)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition cursor-pointer ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 font-semibold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`h-4 w-4 ${isActive ? 'text-blue-600' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>
                {item.count !== undefined && item.count > 0 && (
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-100 text-slate-600">
                    {item.count}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Backend & Security Status Box */}
        <div className="p-4 border-t border-slate-100 space-y-3">
          {/* Backend Status indicator */}
          <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200/60 flex items-center justify-between text-[11px]">
            <span className="text-slate-500 font-medium">Core Service</span>
            <div className="flex items-center gap-1.5">
              <span
                className={`h-2 w-2 rounded-full ${
                  backendStatus?.status === 'HEALTHY'
                    ? 'bg-emerald-500 animate-pulse'
                    : 'bg-rose-500'
                }`}
              />
              <span className="font-semibold text-slate-700">
                {backendStatus?.status === 'HEALTHY' ? 'Online (v2.1)' : 'Offline'}
              </span>
            </div>
          </div>

          {/* Privacy & Zero-Retention Note */}
          <div className="p-3 rounded-xl bg-blue-50/50 border border-blue-100/80 text-[11px] text-slate-600 space-y-1">
            <div className="flex items-center gap-1.5 font-semibold text-blue-900">
              <Lock className="h-3.5 w-3.5 text-blue-600" />
              <span>Zero Data Retention</span>
            </div>
            <p className="text-[10px] text-slate-500 leading-relaxed m-0">
              Documents are processed in ephemeral memory and discarded immediately. No data is stored or publicly exposed.
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}
