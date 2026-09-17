import React from 'react';
import {
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  HelpCircle,
  Info,
  Download,
  RotateCcw,
  Sparkles,
  CheckCircle2,
  Clock
} from 'lucide-react';

export default function AnalysisResult({
  analysisResult,
  onReset,
  onDownloadReport
}) {
  if (!analysisResult) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs p-6 flex flex-col justify-between h-full">
        <div>
          <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <div className="h-7 w-7 rounded-lg bg-violet-50 text-violet-600 flex items-center justify-center font-bold text-xs">
                3
              </div>
              <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider m-0">
                Analysis Verdict
              </h2>
            </div>
            <span className="text-[11px] text-slate-400 font-mono">Awaiting Input</span>
          </div>

          <div className="text-center py-16 px-4 space-y-3">
            <div className="h-14 w-14 rounded-2xl bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-400 mx-auto">
              <ShieldCheck className="h-7 w-7" />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-700 mb-0.5">
                No Forensic Scan Yet
              </p>
              <p className="text-[11px] text-slate-400 max-w-[220px] mx-auto m-0">
                Upload a document on the left to generate digital compression, noise, and OCR audit telemetry.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-6 pt-4 border-t border-slate-100 text-center">
          <span className="text-[11px] text-slate-400">
            Powered by DocShield AI Multi-Spectrum Forensics
          </span>
        </div>
      </div>
    );
  }

  // 3-Tier Status Mapping
  const rawStatus = String(analysisResult.authenticity_status || analysisResult.classification || 'AUTHENTIC').toUpperCase();
  const score = analysisResult.risk_score ?? 0;
  const confidence = analysisResult.confidence_score ?? 85;

  const getStatusTheme = () => {
    if (rawStatus.includes('FORGED') || score >= 65) {
      return {
        label: 'Likely Forged',
        badge: 'HIGH TAMPERING RISK',
        color: 'text-rose-700',
        bg: 'bg-rose-50',
        border: 'border-rose-200',
        bar: 'bg-rose-600',
        icon: ShieldAlert
      };
    }
    if (rawStatus.includes('MANUAL') || rawStatus.includes('REVIEW') || rawStatus.includes('SUSPICIOUS') || score >= 29) {
      return {
        label: 'Needs Manual Review',
        badge: 'MANUAL REVIEW REQUIRED',
        color: 'text-amber-800',
        bg: 'bg-amber-50/70',
        border: 'border-amber-200',
        bar: 'bg-amber-500',
        icon: AlertTriangle
      };
    }
    return {
      label: 'Likely Genuine',
      badge: 'LIKELY GENUINE',
      color: 'text-emerald-700',
      bg: 'bg-emerald-50',
      border: 'border-emerald-200',
      bar: 'bg-emerald-600',
      icon: ShieldCheck
    };
  };

  const theme = getStatusTheme();
  const Icon = theme.icon;

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs p-6 flex flex-col justify-between h-full">
      <div className="space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-lg bg-violet-50 text-violet-600 flex items-center justify-center font-bold text-xs">
              3
            </div>
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider m-0">
              Analysis Verdict
            </h2>
          </div>

          <span className="text-[11px] font-semibold text-slate-500 font-mono">
            {analysisResult.document_type}
          </span>
        </div>

        {/* STATUS BADGE BANNER */}
        <div className={`p-4 rounded-xl border ${theme.border} ${theme.bg} flex items-start gap-3`}>
          <div className={`p-2 rounded-lg bg-white ${theme.color} shrink-0 shadow-xs`}>
            <Icon className="h-6 w-6" />
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between gap-2 mb-0.5">
              <span className={`text-xs font-bold uppercase tracking-wider ${theme.color}`}>
                {theme.badge}
              </span>
              <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-white/80 border border-slate-200 text-slate-700">
                Tier: {status}
              </span>
            </div>
            <h3 className="text-base font-bold text-slate-900 m-0">
              {theme.label}
            </h3>
            <p className="text-xs text-slate-600 mt-1 m-0 leading-relaxed">
              {analysisResult.verdict}
            </p>
          </div>
        </div>

        {/* METRICS ROW: RISK SCORE & CONFIDENCE GAUGE */}
        <div className="grid grid-cols-2 gap-3">
          {/* Risk Score */}
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80">
            <div className="text-[10px] uppercase font-semibold tracking-wider text-slate-500 mb-1">
              Forgery Risk Score
            </div>
            <div className="flex items-baseline gap-1">
              <span className={`text-2xl font-black font-mono ${theme.color}`}>
                {score}
              </span>
              <span className="text-xs text-slate-400 font-mono">/ 100</span>
            </div>
            <div className="w-full bg-slate-200 h-1.5 rounded-full mt-2 overflow-hidden">
              <div
                className={`h-full ${theme.bar} transition-all duration-500 rounded-full`}
                style={{ width: `${score}%` }}
              />
            </div>
          </div>

          {/* Confidence Score */}
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80">
            <div className="text-[10px] uppercase font-semibold tracking-wider text-slate-500 mb-1">
              Analysis Confidence
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-black font-mono text-blue-600">
                {confidence}
              </span>
              <span className="text-xs text-slate-400 font-mono">%</span>
            </div>
            <div className="w-full bg-slate-200 h-1.5 rounded-full mt-2 overflow-hidden">
              <div
                className="h-full bg-blue-600 transition-all duration-500 rounded-full"
                style={{ width: `${confidence}%` }}
              />
            </div>
          </div>
        </div>

        {/* PLAIN LANGUAGE EXPLANATION */}
        {analysisResult.explanation && (
          <div className="p-3.5 rounded-xl bg-blue-50/50 border border-blue-100 text-xs text-slate-700 leading-relaxed space-y-1">
            <div className="flex items-center gap-1.5 font-bold text-blue-900">
              <HelpCircle className="h-3.5 w-3.5 text-blue-600" />
              <span>Plain Language Summary</span>
            </div>
            <p className="text-[11px] text-slate-600 m-0 leading-relaxed">
              {analysisResult.explanation}
            </p>
          </div>
        )}

        {/* DISCLAIMER / LIMITATIONS CARD */}
        <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 text-[10px] text-slate-500 flex items-start gap-2">
          <Info className="h-3.5 w-3.5 text-slate-400 shrink-0 mt-0.5" />
          <p className="m-0 leading-relaxed">
            <span className="font-semibold text-slate-700">Forensic Notice: </span>
            {analysisResult.limitations || 'Automated AI checks are probabilistic and do not establish 100% certainty. Official or legal determinations should be confirmed through the issuing authority.'}
          </p>
        </div>
      </div>

      {/* QUICK ACTIONS FOOTER */}
      <div className="mt-6 pt-4 border-t border-slate-100 flex items-center gap-2">
        <button
          onClick={onDownloadReport}
          className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 active:bg-slate-300 text-slate-700 text-xs font-semibold border border-slate-200/80 transition cursor-pointer"
        >
          <Download className="h-3.5 w-3.5" />
          <span>Audit Report</span>
        </button>

        <button
          onClick={onReset}
          className="px-3 py-2.5 rounded-xl bg-white hover:bg-slate-50 active:bg-slate-100 text-slate-600 text-xs font-medium border border-slate-200 transition cursor-pointer"
          title="Reset Analysis"
        >
          <RotateCcw className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}
