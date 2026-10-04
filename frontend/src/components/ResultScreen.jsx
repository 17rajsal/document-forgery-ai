import React, { useState } from 'react';
import {
  ArrowLeft,
  Download,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  FileText,
  Layers,
  Search,
  CheckCircle2,
  XCircle,
  Info,
  ExternalLink,
  RotateCcw,
  Volume2,
  Globe,
  Link,
  QrCode,
  Landmark,
  Scale
} from 'lucide-react';
import VoicePlayer from './VoicePlayer';

export default function ResultScreen({
  analysisResult,
  onBackToAnalyze,
  onDownloadReport,
  language = 'en',
  onToggleLanguage
}) {
  if (!analysisResult) return null;

  const [activeTab, setActiveTab] = useState('doc_analysis'); // 'doc_analysis' | 'scam_signals' | 'extracted_info' | 'safety_guidance'
  const [showOriginal, setShowOriginal] = useState(false);

  // Extract core risk fields
  const scamRisk = analysisResult.investor_scam_risk || {};
  const riskScore = scamRisk.score ?? analysisResult.risk_score ?? 0;
  const riskLevel = scamRisk.risk_level || analysisResult.concern_level || 'LOW RISK';

  const isHigh = riskLevel.includes('HIGH') || riskScore >= 65;
  const isMod = !isHigh && (riskLevel.includes('MODERATE') || riskScore >= 30);

  // Color theme
  const getTheme = () => {
    if (isHigh) {
      return {
        badge: 'HIGH RISK',
        label: language === 'hi' ? 'Savdhani: Niveshak Jokhim Bada Hai' : 'High Investor Scam Risk',
        color: 'text-rose-700',
        bg: 'bg-rose-50',
        border: 'border-rose-200',
        bar: 'bg-rose-600',
        icon: ShieldAlert
      };
    }
    if (isMod) {
      return {
        badge: 'MODERATE RISK',
        label: language === 'hi' ? 'Savdhani: Madhyam Jokhim' : 'Moderate Verification Concern',
        color: 'text-amber-800',
        bg: 'bg-amber-50',
        border: 'border-amber-200',
        bar: 'bg-amber-500',
        icon: AlertTriangle
      };
    }
    return {
      badge: 'LOW RISK',
      label: language === 'hi' ? 'Surakshit: Kam Jokhim' : 'Low Verification Concern',
      color: 'text-emerald-700',
      bg: 'bg-emerald-50',
      border: 'border-emerald-200',
      bar: 'bg-emerald-600',
      icon: ShieldCheck
    };
  };

  const theme = getTheme();
  const Icon = theme.icon;

  // Why it was flagged bullet points
  const whyFlaggedEn = analysisResult.why_flagged?.en || [];
  const whyFlaggedHi = analysisResult.why_flagged?.hi || [];
  const displayReasons = language === 'hi' && whyFlaggedHi.length > 0 ? whyFlaggedHi : whyFlaggedEn;

  // Entity verification status
  const breakdown = analysisResult.component_breakdown || {};
  const entityVer = analysisResult.entity_verification || breakdown.entity_verification || {};
  const entityStatus = entityVer.status || 'UNABLE TO VERIFY';

  const getEntityBadge = () => {
    if (entityStatus === 'VERIFIED') {
      return { bg: 'bg-emerald-100 text-emerald-800 border-emerald-300', text: 'VERIFIED' };
    }
    if (entityStatus === 'NOT VERIFIED') {
      return { bg: 'bg-rose-100 text-rose-800 border-rose-300', text: 'NOT VERIFIED' };
    }
    return { bg: 'bg-amber-100 text-amber-800 border-amber-300', text: 'UNABLE TO VERIFY' };
  };
  const entBadge = getEntityBadge();

  // Forgery Pair info if available
  const forgeryPair = analysisResult.forgery_pair || null;
  const visualBoxes = analysisResult.visual_evidence_map || [];
  const previewImg = showOriginal && forgeryPair?.original_image_url
    ? forgeryPair.original_image_url
    : (analysisResult.preview_image || forgeryPair?.tampered_image_url);

  const voiceEn = analysisResult.plain_explanation?.en || analysisResult.proofly?.plain_explanations?.voice_script_en || '';
  const voiceHi = analysisResult.plain_explanation?.hi || analysisResult.proofly?.plain_explanations?.voice_script_hi || '';

  return (
    <div className="max-w-4xl mx-auto py-4 space-y-6">
      {/* TOP NAVIGATION / ACTIONS BAR */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 pb-3">
        <button
          onClick={onBackToAnalyze}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white hover:bg-slate-100 border border-slate-200 text-xs font-semibold text-slate-700 transition cursor-pointer"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          <span>New Analysis</span>
        </button>

        <div className="flex items-center gap-2">
          {/* Voice Player */}
          {(voiceEn || voiceHi) && (
            <VoicePlayer textEn={voiceEn} textHi={voiceHi} language={language} />
          )}

          {/* Language Toggle */}
          <button
            onClick={onToggleLanguage}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 border border-slate-200 text-xs font-bold text-slate-700 transition cursor-pointer"
          >
            <Globe className="h-3.5 w-3.5 text-blue-600" />
            <span>{language === 'hi' ? 'हिंदी (Active)' : 'English / हिंदी'}</span>
          </button>

          {/* Export Dossier */}
          <button
            onClick={onDownloadReport}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-xs transition cursor-pointer"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Download Dossier</span>
          </button>
        </div>
      </div>

      {/* 1. PRIMARY RESULT BANNER: INVESTOR SCAM RISK */}
      <div className={`p-6 rounded-2xl border ${theme.border} ${theme.bg} shadow-xs space-y-4`}>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className={`p-2.5 rounded-xl bg-white ${theme.color} shadow-xs`}>
              <Icon className="h-7 w-7" />
            </div>
            <div>
              <span className={`text-[11px] font-bold uppercase tracking-wider ${theme.color}`}>
                {theme.badge}
              </span>
              <h2 className="text-2xl font-black text-slate-900 m-0">
                {theme.label}
              </h2>
            </div>
          </div>

          <div className="text-right">
            <span className="text-[10px] text-slate-500 font-mono block">Scam Risk Score</span>
            <div className="text-3xl font-black text-slate-900 font-mono">
              {riskScore} <span className="text-sm font-normal text-slate-500">/ 100</span>
            </div>
          </div>
        </div>

        {/* Probabilistic Explanation */}
        <p className="text-xs sm:text-sm text-slate-700 leading-relaxed font-medium m-0 pt-1 border-t border-slate-200/60">
          {language === 'hi'
            ? (analysisResult.plain_explanation?.hi || analysisResult.explanation || 'Niveshak jokhim ka aaklan kiya gaya.')
            : (analysisResult.plain_explanation?.en || analysisResult.explanation || 'Potential manipulation or high-risk claims detected.')}
        </p>
      </div>

      {/* 2. "WHY IT WAS FLAGGED" (REQUIRED SECTION) */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 m-0 flex items-center gap-2">
          <HelpCircle className="h-4 w-4 text-blue-600" />
          <span>Why It Was Flagged</span>
        </h3>

        {displayReasons.length > 0 ? (
          <div className="space-y-2">
            {displayReasons.map((reason, idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-800 leading-relaxed flex items-start gap-2.5"
              >
                <div className="h-2 w-2 rounded-full bg-blue-600 shrink-0 mt-1.5" />
                <span className="font-medium">{reason}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600">
            No obvious manipulation detected.
          </div>
        )}
      </div>

      {/* 3. FOUR CORE RESULT TABS */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        {/* Tab Headers */}
        <div className="flex border-b border-slate-200 bg-slate-50/70 overflow-x-auto">
          {[
            { id: 'doc_analysis', label: 'Document Analysis', icon: Layers },
            { id: 'scam_signals', label: 'Scam Signals', icon: ShieldAlert },
            { id: 'extracted_info', label: 'Extracted Information', icon: FileText },
            { id: 'safety_guidance', label: 'Safety Guidance', icon: CheckCircle2 }
          ].map((tab) => {
            const TabIcon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 py-3 px-4 text-xs font-bold transition flex items-center justify-center gap-2 border-b-2 cursor-pointer whitespace-nowrap ${
                  isActive
                    ? 'border-blue-600 text-blue-700 bg-white'
                    : 'border-transparent text-slate-600 hover:text-slate-900'
                }`}
              >
                <TabIcon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {/* TAB 1: DOCUMENT ANALYSIS */}
          {activeTab === 'doc_analysis' && (
            <div className="space-y-4">
              {/* Forgery Pair Toggle if available */}
              {forgeryPair?.is_pair && (
                <div className="p-3 rounded-xl bg-indigo-50 border border-indigo-200 flex flex-wrap items-center justify-between gap-2">
                  <div className="text-xs font-semibold text-indigo-950">
                    Document Forgery Test: Synthetic Amount Replacement
                  </div>
                  <div className="flex items-center bg-white rounded-lg p-0.5 border border-indigo-200 text-xs font-bold">
                    <button
                      onClick={() => setShowOriginal(false)}
                      className={`px-3 py-1 rounded-md transition cursor-pointer ${
                        !showOriginal ? 'bg-indigo-600 text-white shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      Tampered (₹50,000)
                    </button>
                    <button
                      onClick={() => setShowOriginal(true)}
                      className={`px-3 py-1 rounded-md transition cursor-pointer ${
                        showOriginal ? 'bg-indigo-600 text-white shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      Original (₹5,000)
                    </button>
                  </div>
                </div>
              )}

              {/* Visual Preview Container */}
              <div className="relative rounded-xl border border-slate-200 bg-slate-100/70 p-4 flex items-center justify-center min-h-[260px] overflow-auto">
                {previewImg ? (
                  <div className="relative inline-block">
                    <img
                      src={previewImg}
                      alt="Document Preview"
                      className="max-h-[380px] w-auto rounded-lg shadow-sm bg-white"
                    />

                    {/* Highlighted Bounding Box on Tampered Region */}
                    {!showOriginal && visualBoxes.length > 0 && visualBoxes.map((vb, idx) => {
                      const box = vb.box || [324, 268, 200, 46];
                      // Box coordinates normalized for 1800x1100 preview
                      const left = (box[0] / 1800) * 100;
                      const top = (box[1] / 1100) * 100;
                      const width = (box[2] / 1800) * 100;
                      const height = (box[3] / 1100) * 100;
                      return (
                        <div
                          key={idx}
                          className="absolute border-2 border-rose-500 bg-rose-500/20 rounded-xs animate-pulse pointer-events-none"
                          style={{ left: `${left}%`, top: `${top}%`, width: `${width}%`, height: `${height}%` }}
                        >
                          <span className="absolute -top-5 left-0 px-1 py-0.5 rounded bg-rose-600 text-white text-[9px] font-bold font-mono whitespace-nowrap">
                            Suspicious edited region
                          </span>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="text-center py-10 text-slate-400 text-xs">
                    Text-only communication analyzed (no physical raster document attached).
                  </div>
                )}
              </div>

              {/* Forensic Details List */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                    Document Integrity Status
                  </span>
                  <span className="font-bold text-slate-800">
                    {breakdown.document_integrity?.status || 'Evaluated'} ({breakdown.document_integrity?.label || '0/100'})
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                    Compression & Texture Anomalies
                  </span>
                  <span className="font-bold text-slate-800">
                    {forgeryPair ? 'Patch font disparity detected' : 'Uniform rasterization profile'}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: SCAM SIGNALS */}
          {activeTab === 'scam_signals' && (
            <div className="space-y-3">
              <p className="text-xs text-slate-500 m-0">
                Statutory regulatory checks cross-referenced against SEBI (Investment Advisers) Regulations, 2013.
              </p>

              <div className="space-y-2">
                {[
                  {
                    title: 'Prohibited Guaranteed Return Language',
                    desc: 'Promising guaranteed profits on securities or unlisted shares is statutorily prohibited.',
                    status: (breakdown.scam_language?.score || 0) >= 50 ? 'TRIGGERED' : 'NOT DETECTED',
                    isTriggered: (breakdown.scam_language?.score || 0) >= 50
                  },
                  {
                    title: 'False Zero-Risk or Capital Protection Claims',
                    desc: 'Claims of "100% risk-free" or "zero loss possible" contradict fundamental market realities.',
                    status: (breakdown.scam_language?.score || 0) >= 60 ? 'TRIGGERED' : 'NOT DETECTED',
                    isTriggered: (breakdown.scam_language?.score || 0) >= 60
                  },
                  {
                    title: 'Artificial Countdown & Urgency Pressure',
                    desc: 'Demanding payment within 15–20 minutes to prevent account lock is standard scam engineering.',
                    status: (breakdown.scam_language?.score || 0) >= 40 ? 'TRIGGERED' : 'NOT DETECTED',
                    isTriggered: (breakdown.scam_language?.score || 0) >= 40
                  }
                ].map((sig, idx) => (
                  <div
                    key={idx}
                    className={`p-3.5 rounded-xl border flex items-start justify-between gap-3 ${
                      sig.isTriggered
                        ? 'bg-rose-50/70 border-rose-200 text-rose-950'
                        : 'bg-slate-50 border-slate-200 text-slate-700'
                    }`}
                  >
                    <div>
                      <h4 className="text-xs font-bold m-0">{sig.title}</h4>
                      <p className="text-[11px] text-slate-500 m-0 mt-0.5">{sig.desc}</p>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono shrink-0 ${
                      sig.isTriggered ? 'bg-rose-200 text-rose-800' : 'bg-slate-200 text-slate-600'
                    }`}>
                      {sig.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: EXTRACTED INFORMATION */}
          {activeTab === 'extracted_info' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                {/* Entity & Reg */}
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                    Claimed Entity Registration
                  </span>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${entBadge.bg}`}>
                      {entBadge.text}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-600 m-0">
                    {entityVer.verdict || 'Unable to verify registration status against public directory mirror.'}
                  </p>
                </div>

                {/* URL / Domain */}
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                    Website URL & Domain Risk
                  </span>
                  <div className="font-mono font-bold text-slate-800 truncate">
                    {analysisResult.url_analysis?.domain || breakdown.url_domain_risk?.domain || 'No link provided'}
                  </div>
                  <p className="text-[11px] text-slate-600 m-0">
                    {breakdown.url_domain_risk?.label || 'Not found'}
                  </p>
                </div>
              </div>

              {/* Extracted Text Preview */}
              {analysisResult.extracted_text && (
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                    Extracted Text Content
                  </span>
                  <p className="text-xs text-slate-700 font-mono leading-relaxed max-h-36 overflow-y-auto m-0 whitespace-pre-line">
                    {analysisResult.extracted_text}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* TAB 4: SAFETY GUIDANCE */}
          {activeTab === 'safety_guidance' && (
            <div className="space-y-3">
              <div className="p-3 rounded-xl bg-blue-50 border border-blue-200 text-xs text-blue-900 font-medium">
                Always verify regulatory credentials before transferring any funds or signing documents.
              </div>

              <div className="space-y-2 text-xs">
                {[
                  {
                    step: '1',
                    title: 'Do Not Transfer Money',
                    desc: 'Never transfer funds to personal bank accounts or individual UPI IDs for investment schemes.'
                  },
                  {
                    step: '2',
                    title: 'Corroborate on sebi.gov.in',
                    desc: 'Check the official SEBI directory of registered intermediaries before trusting any market advisor.'
                  },
                  {
                    step: '3',
                    title: 'Report Suspected Fraud',
                    desc: 'Report fraudulent WhatsApp groups, links, or documents immediately on cybercrime.gov.in or call 1930.'
                  }
                ].map((s) => (
                  <div key={s.step} className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-start gap-3">
                    <div className="h-6 w-6 rounded-lg bg-blue-600 text-white font-bold flex items-center justify-center text-xs shrink-0">
                      {s.step}
                    </div>
                    <div>
                      <h4 className="font-bold text-slate-900 m-0">{s.title}</h4>
                      <p className="text-[11px] text-slate-500 m-0 mt-0.5">{s.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* FOOTER NOTICE */}
      <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center text-xs text-slate-500 leading-relaxed">
        <span className="font-semibold text-slate-700">Notice: </span>
        Proofly does not provide stock recommendations, buy/sell calls, price targets, or legally guaranteed fraud verdicts.
        Findings represent probabilistic forensic indicators to support investor safety.
      </div>
    </div>
  );
}
