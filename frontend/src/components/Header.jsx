import React from 'react';
import {
  Menu,
  FilePlus,
  HelpCircle,
  Shield,
  User,
  Sparkles,
  Globe,
  Lightbulb,
  CheckCircle2
} from 'lucide-react';
import VoicePlayer from './VoicePlayer';

export default function Header({
  onNewAnalysis,
  onOpenHowItWorks,
  onOpenFormats,
  setMobileOpen,
  backendStatus,
  language = 'en',
  onToggleLanguage,
  isSimpleMode = false,
  onToggleSimpleMode,
  voiceTextEn = '',
  voiceTextHi = ''
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
            <h1 className="text-lg sm:text-xl font-black tracking-tight text-slate-900 m-0 flex items-center gap-1.5">
              <span>Proofly</span>
              <span className="text-blue-600 font-extrabold text-sm">•</span>
            </h1>
            <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-100">
              <Shield className="h-3 w-3" />
              Document & Message Verification Platform
            </span>
          </div>
          <p className="text-xs text-slate-500 font-medium m-0 hidden sm:block">
            Verify before you trust. Verification Safety & Scam Detection Platform
          </p>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* VOICE PLAYER (IF TEXT AVAILABLE) */}
        {(voiceTextEn || voiceTextHi) && (
          <VoicePlayer
            textEn={voiceTextEn}
            textHi={voiceTextHi}
            language={language}
          />
        )}

        {/* BHARAT-FIRST LANGUAGE TOGGLE */}
        <button
          onClick={onToggleLanguage}
          className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer border ${
            language === 'hi'
              ? 'bg-amber-50 text-amber-900 border-amber-300 shadow-2xs'
              : 'bg-slate-100 text-slate-700 border-slate-200 hover:bg-slate-200'
          }`}
          title="Switch language: English / हिंदी (Bharat-First)"
        >
          <Globe className="h-3.5 w-3.5 text-blue-600" />
          <span>{language === 'hi' ? 'हिंदी (Active)' : 'English / हिंदी'}</span>
        </button>

        {/* EXPLAIN LIKE I'M NEW TOGGLE */}
        <button
          onClick={onToggleSimpleMode}
          className={`hidden md:flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer border ${
            isSimpleMode
              ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
              : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
          }`}
          title="Toggle simplified jargon-free explanation mode"
        >
          <Lightbulb className={`h-3.5 w-3.5 ${isSimpleMode ? 'text-emerald-600' : 'text-slate-400'}`} />
          <span>{isSimpleMode ? "Simple Mode: ON" : "Simple Mode"}</span>
        </button>

        {/* Supported Formats Badge Button */}
        <button
          onClick={onOpenFormats}
          className="hidden xl:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-50 hover:bg-slate-100 border border-slate-200/80 text-xs font-medium text-slate-600 transition cursor-pointer"
          title="View Supported File Formats"
        >
          <Shield className="h-3.5 w-3.5 text-blue-600" />
          <span>8 Formats</span>
        </button>

        {/* Quick Help Modal Trigger */}
        <button
          onClick={onOpenHowItWorks}
          className="p-2 rounded-lg text-slate-500 hover:text-blue-600 hover:bg-blue-50 transition cursor-pointer"
          title="How Proofly Works & Philosophy"
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
          <div className="h-8 w-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-600 text-xs font-semibold" title="Proofly Workspace">
            <User className="h-4 w-4" />
          </div>
        </div>
      </div>
    </header>
  );
}
