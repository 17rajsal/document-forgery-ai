import React from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  FileSearch,
  ArrowRight,
  Sparkles,
  Lock,
  Layers,
  AlertTriangle,
  Scale,
  CheckCircle2,
  FileText,
  MessageSquare,
  Globe
} from 'lucide-react';

export default function HomeScreen({
  onNavigateToAnalyze,
  onRunDemoScam,
  onRunDemoForgery,
  onRunDemoControl,
  isAnalyzing,
  language = 'en'
}) {
  return (
    <div className="space-y-12 max-w-5xl mx-auto py-4">
      {/* HERO SECTION */}
      <section className="text-center space-y-4 pt-4 pb-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200 shadow-2xs">
          <ShieldCheck className="h-3.5 w-3.5 text-blue-600" />
          <span>Investor Safety & Scam Prevention</span>
        </div>

        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 tracking-tight leading-tight m-0">
          Proofly Investor <br className="hidden sm:inline" />
          <span className="text-blue-600">Verify before you trust.</span>
        </h1>

        <p className="text-sm sm:text-base text-slate-600 max-w-2xl mx-auto leading-relaxed m-0 font-normal">
          Analyze suspicious investment documents, messages, links and QR codes for potential fraud indicators before taking action.
        </p>

        {/* PRIMARY CALL TO ACTION BUTTONS */}
        <div className="pt-4 flex flex-wrap items-center justify-center gap-3">
          <button
            onClick={onNavigateToAnalyze}
            className="flex items-center gap-2 px-6 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-bold text-sm shadow-md shadow-blue-600/25 transition cursor-pointer"
          >
            <FileSearch className="h-4 w-4" />
            <span>Analyze Now</span>
            <ArrowRight className="h-4 w-4" />
          </button>

          <a
            href="#how-it-works"
            className="flex items-center gap-2 px-5 py-3.5 rounded-xl bg-white hover:bg-slate-50 text-slate-800 border border-slate-300 font-semibold text-sm shadow-2xs transition cursor-pointer"
          >
            <span>How It Works</span>
          </a>

          <button
            onClick={() => onRunDemoScam('guaranteed_return')}
            disabled={isAnalyzing}
            className="flex items-center gap-2 px-4 py-3.5 rounded-xl bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 font-semibold text-xs shadow-2xs transition cursor-pointer disabled:opacity-50"
          >
            <Sparkles className="h-3.5 w-3.5 text-blue-600" />
            <span>Try Sample (60% Return)</span>
          </button>
        </div>
      </section>

      {/* 3 CORE INTERACTIVE ENTRY CARDS */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Card 1: Analyze Input */}
        <div
          onClick={onNavigateToAnalyze}
          className="bg-white rounded-2xl border border-slate-200/90 p-6 shadow-xs hover:shadow-md hover:border-blue-400 transition cursor-pointer flex flex-col justify-between group"
        >
          <div>
            <div className="h-10 w-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
              <FileSearch className="h-5 w-5" />
            </div>
            <h3 className="text-base font-bold text-slate-900 mb-1 group-hover:text-blue-600 transition">
              Verify Document or Message
            </h3>
            <p className="text-xs text-slate-500 leading-relaxed m-0">
              Upload any PDF, screenshot, certificate, or paste suspicious WhatsApp / Telegram investment messages.
            </p>
          </div>
          <div className="mt-6 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-blue-600">
            <span>Open Analyze Screen</span>
            <ArrowRight className="h-3.5 w-3.5 group-hover:translate-x-1 transition-transform" />
          </div>
        </div>

        {/* Card 2: Sample Analysis */}
        <div
          onClick={() => onRunDemoScam('guaranteed_return')}
          className="bg-white rounded-2xl border border-slate-200/90 p-6 shadow-xs hover:shadow-md hover:border-rose-400 transition cursor-pointer flex flex-col justify-between group"
        >
          <div>
            <div className="h-10 w-10 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
              <ShieldAlert className="h-5 w-5" />
            </div>
            <div className="flex items-center gap-1.5 mb-1">
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-100 text-rose-800 font-mono">
                Sample Analysis
              </span>
            </div>
            <h3 className="text-base font-bold text-slate-900 mb-1 group-hover:text-rose-600 transition">
              Sample: Guaranteed 60% Return Scheme
            </h3>
            <p className="text-xs text-slate-500 leading-relaxed m-0">
              Instant evaluation of a synthetic Moonrise Growth Sprint plan promising ₹80,000 for ₹50,000 in 30 days.
            </p>
          </div>
          <div className="mt-6 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-rose-600">
            <span>Inspect Sample Analysis</span>
            <ArrowRight className="h-3.5 w-3.5 group-hover:translate-x-1 transition-transform" />
          </div>
        </div>

        {/* Card 3: Altered Amount Sample */}
        <div
          onClick={() => onRunDemoForgery('tampered_demo')}
          className="bg-white rounded-2xl border border-slate-200/90 p-6 shadow-xs hover:shadow-md hover:border-indigo-400 transition cursor-pointer flex flex-col justify-between group"
        >
          <div>
            <div className="h-10 w-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
              <Layers className="h-5 w-5" />
            </div>
            <div className="flex items-center gap-1.5 mb-1">
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-100 text-indigo-800 font-mono">
                Sample Analysis
              </span>
            </div>
            <h3 className="text-base font-bold text-slate-900 mb-1 group-hover:text-indigo-600 transition">
              Sample: Tampered Amount Record
            </h3>
            <p className="text-xs text-slate-500 leading-relaxed m-0">
              Interactive before/after inspection of original ₹5,000 baseline vs tampered ₹50,000 edited amount patch.
            </p>
          </div>
          <div className="mt-6 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-indigo-600">
            <span>Inspect Sample Analysis</span>
            <ArrowRight className="h-3.5 w-3.5 group-hover:translate-x-1 transition-transform" />
          </div>
        </div>
      </section>

      {/* SAMPLE DATA DISCLOSURE */}
      <div className="text-center text-[11px] text-slate-500 font-medium -mt-6">
        Sample data for demonstration purposes. Never present synthetic data as real financial evidence.
      </div>

      {/* HOW PROOFLY WORKS */}
      <section id="how-it-works" className="bg-white rounded-2xl border border-slate-200/90 p-8 shadow-xs space-y-6">
        <div className="text-center max-w-xl mx-auto space-y-1">
          <h2 className="text-xl font-bold text-slate-900 m-0">
            How Proofly Protects Retail Investors
          </h2>
          <p className="text-xs text-slate-500 m-0">
            Multi-signal verification designed to show the evidence, not ask for blind trust.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2">
          <div className="space-y-2">
            <div className="h-8 w-8 rounded-lg bg-blue-50 text-blue-600 font-bold flex items-center justify-center text-sm font-mono">
              1
            </div>
            <h4 className="text-sm font-bold text-slate-900 m-0">
              Multimodal Computer Vision
            </h4>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Performs Error Level Analysis (ELA), high-frequency noise residual mapping, and AI inpainting detection to spot spliced numbers and altered stamps.
            </p>
          </div>

          <div className="space-y-2">
            <div className="h-8 w-8 rounded-lg bg-indigo-50 text-indigo-600 font-bold flex items-center justify-center text-sm font-mono">
              2
            </div>
            <h4 className="text-sm font-bold text-slate-900 m-0">
              Regulatory Directory Cross-Check
            </h4>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Validates claimed SEBI registration numbers (INZ, INA, INH) and NSDL DP IDs against a regulated directory mirror to expose impersonation.
            </p>
          </div>

          <div className="space-y-2">
            <div className="h-8 w-8 rounded-lg bg-emerald-50 text-emerald-600 font-bold flex items-center justify-center text-sm font-mono">
              3
            </div>
            <h4 className="text-sm font-bold text-slate-900 m-0">
              Explainable Risk & Safe Steps
            </h4>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Generates a clear 4-component risk breakdown, plain-language English & Hindi explanations, voice audio summary, and official verification steps.
            </p>
          </div>
        </div>
      </section>

      {/* STATUTORY GUARDRAILS & DISCLAIMER */}
      <section id="safety" className="bg-slate-50 rounded-2xl border border-slate-200 p-6 flex flex-col sm:flex-row items-start gap-4">
        <div className="p-2.5 rounded-xl bg-slate-200 text-slate-700 shrink-0">
          <Scale className="h-6 w-6" />
        </div>
        <div className="space-y-1.5 text-xs text-slate-600 leading-relaxed">
          <h4 className="font-bold text-slate-900 uppercase tracking-wider text-[11px] m-0">
            Strict Statutory Guardrails & Non-Negotiable Boundaries
          </h4>
          <p className="m-0">
            Proofly is an independent investor-safety and forensic verification technology project.
            Proofly <span className="font-bold text-slate-800">does NOT</span> provide stock recommendations, buy/sell/hold calls, price targets, personalized investment advice, or legally guaranteed fraud verdicts.
            All verdicts are probabilistic and intended to alert users to anomalies requiring independent corroboration at <a href="https://www.sebi.gov.in" target="_blank" rel="noreferrer" className="text-blue-600 underline font-semibold">sebi.gov.in</a>.
          </p>
        </div>
      </section>

      {/* ABOUT SECTION */}
      <section id="about" className="bg-white rounded-2xl border border-slate-200/90 p-8 shadow-xs space-y-3">
        <h3 className="text-lg font-bold text-slate-900 m-0">About Proofly Investor</h3>
        <p className="text-xs text-slate-600 leading-relaxed m-0">
          Proofly Investor helps users inspect suspicious investment-related documents and messages using document forensics, OCR, scam-pattern analysis and explainable risk indicators.
        </p>
        <p className="text-[11px] text-slate-400 italic m-0 pt-3 border-t border-slate-100">
          An independent investor-safety technology project.
        </p>
      </section>
    </div>
  );
}
