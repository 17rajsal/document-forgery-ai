import React from 'react';
import {
  Menu,
  FilePlus,
  HelpCircle,
  Search,
  CheckCircle2,
  Shield,
  User,
  Sparkles,
  Info
} from 'lucide-react';

export default function Header({
  onNewAnalysis,
  onOpenHowItWorks,
  onOpenFormats,
  setMobileOpen,
  backendStatus
}) {
  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-sm border-b border-slate-200/80 px-4 sm:px-8 py-3.5 flex items-center justify-between shadow-xs">
      {/* Left: Mobile hamburger & Page Title */}
      <div className="flex items-center gap-3 sm:gap-4">
        <button
          onClick={() => setMobileOpen(true)}
          className="p-2 rounded-xl text-slate-500 hover:text-slate-800 hover:bg-slate-100 lg:hidden cursor-pointer"
          title="Open Menu"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg sm:text-xl font-bold tracking-tight text-slate-900 m-0">
              Document Forgery Detection
            </h1>
            <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-50 text-blue-700 border border-blue-100">
              <Sparkles className="h-3 w-3" />
              SaaS v2.1
            </span>
          </div>
          <p className="text-xs text-slate-500 m-0 hidden sm:block">
            AI-powered document authenticity analysis, multi-spectrum ELA & tamper verification
          </p>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Supported Formats Badge Button */}
        <button
          onClick={onOpenFormats}
          className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-50 hover:bg-slate-100 border border-slate-200/80 text-xs font-medium text-slate-600 transition cursor-pointer"
          title="View Supported File Formats"
        >
          <Shield className="h-3.5 w-3.5 text-blue-600" />
          <span>7 Formats (PDF, DOCX, TIFF...)</span>
        </button>

        {/* Quick Help Modal Trigger */}
        <button
          onClick={onOpenHowItWorks}
          className="p-2 rounded-lg text-slate-500 hover:text-blue-600 hover:bg-blue-50 transition cursor-pointer"
          title="How It Works & Methodology"
        >
          <HelpCircle className="h-4.5 w-4.5" />
        </button>

        {/* Primary New Analysis Button */}
        <button
          onClick={onNewAnalysis}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white text-xs font-semibold shadow-xs shadow-blue-600/20 transition cursor-pointer"
        >
          <FilePlus className="h-4 w-4" />
          <span className="hidden sm:inline">New Analysis</span>
        </button>

        {/* User Profile Avatar */}
        <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
          <div className="h-8 w-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-600 text-xs font-semibold" title="Analyst Workspace">
            <User className="h-4 w-4" />
          </div>
        </div>
      </div>
    </header>
  );
}
