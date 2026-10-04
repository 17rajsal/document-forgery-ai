import React from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  Info,
  Download,
  RotateCcw,
  Sparkles,
  Layers,
  QrCode,
  Volume2,
  FileCheck2,
  Globe,
  ExternalLink,
  CheckCircle2,
  XCircle,
  HelpCircle as QuestionIcon
} from 'lucide-react';
import VoicePlayer from './VoicePlayer';

export default function AnalysisResult({
  analysisResult,
  onReset,
  onDownloadReport,
  language = 'en',
  isSimpleMode = false
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
                Proofly Assessment
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
                No Input Analyzed Yet
              </p>
              <p className="text-[11px] text-slate-400 max-w-[240px] mx-auto m-0">
                Upload a document or paste a message to inspect image tampering, scam language, fake registration, and malicious URLs.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-6 pt-4 border-t border-slate-100 text-center">
          <span className="text-[11px] text-slate-400">
            Proofly Engine • Verification safety through explainable risk analysis.
          </span>
        </div>
      </div>
    );
  }

  // Extract risk & components
  const proofly = analysisResult.proofly || {};
  const assessment = proofly.assessment || {};
  const plainExp = proofly.plain_explanations || analysisResult.plain_explanation || {};
  const breakdown = analysisResult.component_breakdown || {};
  const entityVer = analysisResult.entity_verification || breakdown.entity_verification || {};

  // Composite Risk Score
  const scamRisk = analysisResult.investor_scam_risk || {};
  const riskScore = scamRisk.score ?? assessment.total_risk_score ?? analysisResult.risk_score ?? 0;
  const rawLevel = scamRisk.risk_level || assessment.concern_level || analysisResult.concern_level || 'LOW';

  const isHigh = rawLevel.includes('HIGH') || riskScore >= 65;
  const isMod = !isHigh && (rawLevel.includes('MODERATE') || riskScore >= 30);

  const getConcernTheme = () => {
    if (isHigh) {
      return {
        label: language === 'hi' ? 'Savdhani: Niveshak Jokhim Bada Hai (High Risk)' : 'Risk Assessment: High Risk',
        badge: 'HIGH RISK',
        color: 'text-rose-700',
        bg: 'bg-rose-50',
        border: 'border-rose-200',
        bar: 'bg-rose-600',
        icon: ShieldAlert
      };
    }
    if (isMod) {
      return {
        label: language === 'hi' ? 'Savdhani: Madhyam Jokhim (Moderate Risk)' : 'Risk Assessment: Moderate Risk',
        badge: 'MODERATE RISK',
        color: 'text-amber-800',
        bg: 'bg-amber-50/70',
        border: 'border-amber-200',
        bar: 'bg-amber-500',
        icon: AlertTriangle
      };
    }
    return {
      label: language === 'hi' ? 'Surakshit: Kam Jokhim (Low Risk)' : 'Risk Assessment: Low Risk',
      badge: 'LOW RISK',
      color: 'text-emerald-700',
      bg: 'bg-emerald-50',
      border: 'border-emerald-200',
      bar: 'bg-emerald-600',
      icon: ShieldCheck
    };
  };

  const theme = getConcernTheme();
  const Icon = theme.icon;

  // "Why this was flagged" items
  const whyFlaggedEn = analysisResult.why_flagged?.en || assessment.why_am_i_seeing_this || [];
  const whyFlaggedHi = analysisResult.why_flagged?.hi || [];
  const displayReasons = language === 'hi' && whyFlaggedHi.length > 0 ? whyFlaggedHi : whyFlaggedEn;

  // Entity status badge
  const entityStatus = entityVer.status || 'UNABLE TO VERIFY';
  const getEntityBadge = () => {
    if (entityStatus === 'VERIFIED') {
      return { bg: 'bg-emerald-100 text-emerald-800 border-emerald-200', icon: CheckCircle2, text: 'VERIFIED' };
    }
    if (entityStatus === 'NOT VERIFIED') {
      return { bg: 'bg-rose-100 text-rose-800 border-rose-200', icon: XCircle, text: 'NOT VERIFIED' };
    }
    return { bg: 'bg-amber-100 text-amber-800 border-amber-200', icon: QuestionIcon, text: 'UNABLE TO VERIFY' };
  };
  const entBadge = getEntityBadge();
  const EntIcon = entBadge.icon;

  const voiceScriptEn = plainExp.voice_script_en || plainExp.en || '';
  const voiceScriptHi = plainExp.voice_script_hi || plainExp.hi || '';

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs p-6 flex flex-col justify-between h-full">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-lg bg-violet-50 text-violet-600 flex items-center justify-center font-bold text-xs">
              3
            </div>
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider m-0">
              Proofly Assessment
            </h2>
          </div>

          <span className="text-[11px] font-semibold text-slate-500 font-mono truncate max-w-[140px]">
            {analysisResult.mode === 'TEXT_URL_ANALYSIS' ? 'Pasted Text/URL' : (analysisResult.document_type || 'Financial Doc')}
          </span>
        </div>

        {/* STATUS BANNER */}
        <div className={`p-4 rounded-xl border ${theme.border} ${theme.bg} flex items-start gap-3`}>
          <div className={`p-2 rounded-lg bg-white ${theme.color} shrink-0 shadow-xs`}>
            <Icon className="h-6 w-6" />
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between gap-2 mb-0.5">
              <span className={`text-[10px] font-bold uppercase tracking-wider ${theme.color}`}>
                {theme.badge}
              </span>
              <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-white/80 border border-slate-200 text-slate-700">
                Score: {riskScore}/100
              </span>
            </div>
            <h3 className="text-base font-bold text-slate-900 m-0">
              {theme.label}
            </h3>
            <p className="text-xs text-slate-600 mt-1 m-0 leading-relaxed">
              {language === 'hi'
                ? (plainExp.hi || plainExp.simple_explanation_hi || analysisResult.explanation)
                : (plainExp.en || plainExp.simple_explanation_en || analysisResult.explanation)}
            </p>
          </div>
        </div>

        {/* 4-COMPONENT RISK BREAKDOWN */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-700">
              4-Component Risk Breakdown
            </span>
            <span className="text-[10px] font-mono text-slate-400">Pillars</span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-[11px]">
            {/* 1. Document Integrity */}
            <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-400 block text-[10px] font-medium">Document Integrity</span>
              <span className="font-bold text-slate-800 font-mono">
                {breakdown.document_integrity?.label || `${breakdown.document_integrity?.score ?? 0}/100`}
              </span>
            </div>

            {/* 2. Scam Language */}
            <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-400 block text-[10px] font-medium">Scam Language</span>
              <span className={`font-bold font-mono ${
                (breakdown.scam_language?.score || 0) >= 60 ? 'text-rose-600' : 'text-slate-800'
              }`}>
                {breakdown.scam_language?.label || `${breakdown.scam_language?.score ?? 0}/100`}
              </span>
            </div>

            {/* 3. URL / Domain Risk */}
            <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-400 block text-[10px] font-medium">URL / Domain Risk</span>
              <span className={`font-bold font-mono truncate block ${
                (breakdown.url_domain_risk?.score || 0) >= 60 ? 'text-rose-600' : 'text-slate-800'
              }`}>
                {breakdown.url_domain_risk?.label || `${breakdown.url_domain_risk?.score ?? 0}/100`}
              </span>
            </div>

            {/* 4. Entity Verification */}
            <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-400 block text-[10px] font-medium">Entity Registration</span>
              <div className="flex items-center gap-1 mt-0.5">
                <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold uppercase border ${entBadge.bg}`}>
                  {entBadge.text}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* AUDIO VOICE SCRIPT PLAYER BUTTON */}
        {(voiceScriptEn || voiceScriptHi) && (
          <div className="p-3 rounded-xl bg-indigo-50/50 border border-indigo-100 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Volume2 className="h-4 w-4 text-indigo-600" />
              <span className="text-xs font-semibold text-indigo-950">
                {language === 'hi' ? 'Awaaz mein sunein (Voice Audio):' : 'Spoken Voice Summary:'}
              </span>
            </div>
            <VoicePlayer
              textEn={voiceScriptEn}
              textHi={voiceScriptHi}
              language={language}
            />
          </div>
        )}

        {/* "WHY WAS THIS FLAGGED?" SECTION */}
        {displayReasons.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 m-0 flex items-center gap-1.5">
              <HelpCircle className="h-3.5 w-3.5 text-blue-600" />
              <span>{language === 'hi' ? 'Yeh nateeja kyon dikh raha hai?' : 'Why was this flagged?'}</span>
            </h4>
            <div className="space-y-1.5 max-h-[160px] overflow-y-auto">
              {displayReasons.slice(0, 4).map((reason, idx) => (
                <div
                  key={idx}
                  className="p-2 rounded-lg bg-slate-50 border border-slate-200/80 text-[11px] text-slate-700 leading-relaxed flex items-start gap-2"
                >
                  <span className="h-1.5 w-1.5 rounded-full bg-blue-600 shrink-0 mt-1.5" />
                  <span>{reason}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* DISCLAIMER / LIMITATION */}
        <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-[10px] text-slate-500 flex items-start gap-2">
          <Info className="h-3.5 w-3.5 text-slate-400 shrink-0 mt-0.5" />
          <p className="m-0 leading-relaxed">
            <span className="font-semibold text-slate-700">Important Disclaimer: </span>
            Proofly does not provide stock recommendations, price targets, buy/sell calls, or legal fraud guarantees.
            It assists investors in identifying digital tampering, statutory red flags, and unverified credentials before sending money.
          </p>
        </div>
      </div>

      {/* QUICK ACTIONS FOOTER */}
      <div className="mt-5 pt-3 border-t border-slate-100 flex items-center gap-2">
        <button
          onClick={onDownloadReport}
          className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-xs transition cursor-pointer"
        >
          <Download className="h-3.5 w-3.5" />
          <span>{language === 'hi' ? 'Evidence Report' : 'Evidence Dossier'}</span>
        </button>

        <button
          onClick={onReset}
          className="px-3 py-2 rounded-xl bg-white hover:bg-slate-50 text-slate-600 text-xs font-medium border border-slate-200 transition cursor-pointer"
          title="Reset Analysis"
        >
          <RotateCcw className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}
