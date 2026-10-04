import React, { useState } from 'react';
import {
  Layers,
  FileText,
  Search,
  Cpu,
  FileCheck2,
  Copy,
  Check,
  Download,
  Info,
  ZoomIn,
  ZoomOut,
  ShieldAlert,
  Sparkles,
  QrCode,
  ShieldCheck,
  AlertTriangle,
  ExternalLink,
  ChevronRight,
  Landmark
} from 'lucide-react';
import VisualEvidenceMap from './VisualEvidenceMap';
import SafeActionGuide from './SafeActionGuide';

export default function ResultTabs({
  analysisResult,
  onDownloadReport,
  language = 'en',
  isSimpleMode = false
}) {
  const [activeTab, setActiveTab] = useState('visual_map'); // 'visual_map', 'claims_evidence', 'qr_identity', 'safe_steps', 'technical', 'ocr', 'report'
  const [visualSpectrum, setVisualSpectrum] = useState('heatmap'); // 'heatmap', 'diff', 'noise'
  const [zoomLevel, setZoomLevel] = useState(1);
  const [copiedKey, setCopiedKey] = useState(null);
  const [ocrFilter, setOcrFilter] = useState('');

  if (!analysisResult) return null;

  const proofly = analysisResult.proofly || {};
  const fa = analysisResult.forgery_analysis || {};
  const ela = fa.ela_analysis || {};
  const noise = fa.noise_analysis || {};
  const meta = fa.metadata_forensics || {};
  const visualBoxes = analysisResult.visual_evidence_map || proofly.visual_evidence_map || [];
  const claims = proofly.claims || [];
  const evidenceVerifications = proofly.evidence_verification || [];
  const qrAnalysis = proofly.qr_analysis || [];
  const urlsAnalysis = proofly.urls_analysis || [];
  const identity = proofly.identity_consistency || {};
  const plainExp = proofly.plain_explanations || {};

  const handleCopy = (key, text) => {
    if (!text) return;
    navigator.clipboard.writeText(String(text));
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 1800);
  };

  const handleDownloadOcrTxt = () => {
    if (!analysisResult.extracted_text) return;
    const blob = new Blob([analysisResult.extracted_text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ocr_text_${analysisResult.filename || 'export'}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const tabs = [
    {
      id: 'visual_map',
      label: language === 'hi' ? 'Visual Evidence Map' : 'Visual Evidence Map',
      badge: visualBoxes.length,
      icon: Layers
    },
    {
      id: 'claims_evidence',
      label: language === 'hi' ? 'Bade Daawe aur Jaanch' : 'Financial Claims & Evidence',
      badge: claims.length,
      icon: AlertTriangle
    },
    {
      id: 'qr_identity',
      label: language === 'hi' ? 'QR Code aur Pehchan' : 'QR & Identity Audit',
      badge: (identity.mismatches?.length || 0) + (qrAnalysis.length || 0),
      icon: QrCode
    },
    {
      id: 'safe_steps',
      label: language === 'hi' ? 'Surakshit Kadam' : 'Safe Next Steps',
      icon: ShieldCheck
    },
    {
      id: 'technical',
      label: language === 'hi' ? 'Technical Forensics' : 'Technical Forensics (ELA/Noise)',
      icon: Cpu
    },
    {
      id: 'ocr',
      label: language === 'hi' ? 'OCR Text' : 'OCR Extracted Text',
      icon: FileText
    },
    {
      id: 'report',
      label: language === 'hi' ? 'Evidence Dossier' : 'Evidence Dossier',
      icon: FileCheck2
    }
  ];

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs overflow-hidden mt-8">
      {/* TABS HEADER */}
      <div className="border-b border-slate-200 bg-slate-50/70 px-4 sm:px-6 pt-3 flex overflow-x-auto gap-1">
        {tabs.map((t) => {
          const Icon = t.icon;
          const isActive = activeTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-t-xl text-xs font-semibold whitespace-nowrap transition cursor-pointer border-t border-x ${
                isActive
                  ? 'bg-white text-blue-600 border-slate-200 border-b-transparent shadow-2xs font-bold'
                  : 'text-slate-600 hover:text-slate-900 border-transparent hover:bg-slate-100/60'
              }`}
            >
              <Icon className={`h-4 w-4 ${isActive ? 'text-blue-600' : 'text-slate-400'}`} />
              <span>{t.label}</span>
              {t.badge !== undefined && t.badge > 0 && (
                <span
                  className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono ${
                    isActive ? 'bg-blue-100 text-blue-700' : 'bg-slate-200/80 text-slate-700'
                  }`}
                >
                  {t.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* TAB CONTENT PANELS */}
      <div className="p-6">
        {/* 1. VISUAL EVIDENCE MAP */}
        {activeTab === 'visual_map' && (
          <VisualEvidenceMap
            previewImage={analysisResult.preview_image}
            visualBoxes={visualBoxes}
            imageWidth={analysisResult.forgery_analysis?.image_analysis?.width || 1240}
            imageHeight={analysisResult.forgery_analysis?.image_analysis?.height || 1754}
            language={language}
          />
        )}

        {/* 2. FINANCIAL CLAIMS & EVIDENCE CHECKER */}
        {activeTab === 'claims_evidence' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider m-0">
                  {language === 'hi' ? 'Pehchane Gaye Daawe aur Niyamak Jaanch' : 'Extracted Financial Claims & Statutory Evidence'}
                </h3>
                <p className="text-xs text-slate-500 m-0">
                  {language === 'hi'
                    ? 'Document mein likhe gaye vaadon ko Regulatory Authority aur RBI niyamak sandarbh se cross-check kiya gaya hai.'
                    : 'Statements cross-referenced against statutory Regulatory Authorities market regulations.'}
                </p>
              </div>
              <span className="text-xs font-mono font-semibold px-2.5 py-1 rounded bg-slate-100 text-slate-600">
                {claims.length} Claims Identified
              </span>
            </div>

            {claims.length === 0 ? (
              <div className="text-center py-12 bg-slate-50 rounded-xl border border-slate-200/70 text-slate-500 text-xs">
                {language === 'hi' ? 'Is document mein koi aam scam ya guaranteed return ke daawe nahi mile.' : 'No overt high-risk financial promises or coercive urgency claims detected.'}
              </div>
            ) : (
              <div className="space-y-3">
                {claims.map((claim, idx) => {
                  const ev = evidenceVerifications.find((e) => e.claim_id === claim.claim_id);
                  const isConflicting = ev?.evidence_status === 'Conflicting evidence';
                  return (
                    <div
                      key={idx}
                      className={`p-4 rounded-xl border transition ${
                        isConflicting ? 'bg-rose-50/40 border-rose-200' : 'bg-amber-50/40 border-amber-200'
                      }`}
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                        <div className="flex items-center gap-2">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                              isConflicting ? 'bg-rose-600 text-white' : 'bg-amber-600 text-white'
                            }`}
                          >
                            {ev?.evidence_status || 'Under Review'}
                          </span>
                          <span className="font-bold text-xs text-slate-900">
                            {claim.title}
                          </span>
                        </div>
                        <span className="text-[10px] font-mono text-slate-500">
                          Category: {claim.category}
                        </span>
                      </div>

                      <div className="p-2.5 rounded-lg bg-white border border-slate-200/90 font-mono text-xs font-bold text-slate-800 mb-3">
                        "{claim.exact_text}"
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                        <div className="space-y-1">
                          <span className="font-semibold text-slate-700 block">
                            {language === 'hi' ? 'Niyamak Jaanch Mein Kya Paya Gaya:' : 'What Was Found in Official Regulations:'}
                          </span>
                          <p className="text-slate-600 text-[11px] leading-relaxed m-0">
                            {ev?.what_was_found || claim.explanation}
                          </p>
                        </div>

                        <div className="space-y-1">
                          <span className="font-semibold text-slate-700 block">
                            {language === 'hi' ? 'Official Authority Source:' : 'Authoritative Verification Source:'}
                          </span>
                          <p className="text-slate-500 font-mono text-[10px] m-0">
                            {ev?.official_source || claim.verification_source}
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* 3. QR & IDENTITY AUDIT */}
        {activeTab === 'qr_identity' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider m-0">
                {language === 'hi' ? 'QR Code aur Pehchan ki Aapsi Jaanch' : 'Embedded QR Codes, URLs & Entity Identity Audit'}
              </h3>
              <p className="text-xs text-slate-500 m-0">
                {language === 'hi'
                  ? 'Company ka naam, official website, payment recipient aur QR code destination ka aapsi milaan.'
                  : 'Cross-channel validation between claimed corporate identity, website domain, and payment endpoints.'}
              </p>
            </div>

            {/* IDENTITY MISMATCHES */}
            {identity.mismatches && identity.mismatches.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-rose-800 flex items-center gap-1.5">
                  <ShieldAlert className="h-4 w-4 text-rose-600" />
                  <span>Detected Identity Discrepancies ({identity.mismatches.length})</span>
                </h4>
                <div className="space-y-2">
                  {identity.mismatches.map((mm, i) => (
                    <div
                      key={i}
                      className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-xs space-y-1.5"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-rose-900">{mm.title}</span>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-200 text-rose-800">
                          {mm.severity}
                        </span>
                      </div>
                      <p className="text-rose-800 text-[11px] leading-relaxed m-0">
                        {mm.description}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* QR CODES LIST */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                <QrCode className="h-4 w-4 text-blue-600" />
                <span>Embedded QR Codes ({qrAnalysis.length})</span>
              </h4>

              {qrAnalysis.length === 0 ? (
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/70 text-slate-500 text-xs">
                  No QR codes were detected in this document.
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {qrAnalysis.map((qr, i) => (
                    <div key={i} className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-xs text-slate-900">QR Code #{qr.qr_index || i + 1}</span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 font-bold">
                          {qr.is_upi ? 'UPI Payment QR' : 'URL Destination'}
                        </span>
                      </div>

                      {qr.is_upi && qr.upi_details ? (
                        <div className="p-2.5 rounded-lg bg-slate-50 font-mono text-xs space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="text-slate-400">Payee Address:</span>
                            <span className="font-bold text-slate-800">{qr.upi_details.payee_address}</span>
                          </div>
                          {qr.upi_details.payee_name && (
                            <div className="flex items-center justify-between">
                              <span className="text-slate-400">Payee Name:</span>
                              <span className="font-bold text-slate-800">{qr.upi_details.payee_name}</span>
                            </div>
                          )}
                          {qr.upi_details.amount && (
                            <div className="flex items-center justify-between">
                              <span className="text-slate-400">Amount:</span>
                              <span className="font-bold text-rose-700 font-mono">₹{qr.upi_details.amount}</span>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="p-2.5 rounded-lg bg-slate-50 font-mono text-[11px] text-slate-700 break-all">
                          {qr.raw_content}
                        </div>
                      )}

                      {qr.risk_flags && qr.risk_flags.length > 0 && (
                        <div className="space-y-1 pt-1">
                          {qr.risk_flags.map((rf, rfi) => (
                            <div key={rfi} className="text-[11px] text-rose-700 flex items-start gap-1.5 font-medium">
                              <span className="h-1.5 w-1.5 rounded-full bg-rose-600 mt-1 shrink-0" />
                              <span>{rf.title}: {rf.description}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* EXTRACTED URLS */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                <ExternalLink className="h-4 w-4 text-blue-600" />
                <span>Extracted Web Domains & Links ({urlsAnalysis.length})</span>
              </h4>

              {urlsAnalysis.length === 0 ? (
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/70 text-slate-500 text-xs">
                  No hyperlinks or web addresses extracted from text.
                </div>
              ) : (
                <div className="space-y-2">
                  {urlsAnalysis.map((u, i) => (
                    <div key={i} className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex flex-wrap items-center justify-between gap-2 text-xs">
                      <div>
                        <span className="font-mono font-bold text-slate-900 block">{u.domain}</span>
                        <span className="text-[11px] text-slate-500 font-mono">{u.clean_url}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {u.typosquatting_detected && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-800">
                            Typosquatting Mimic
                          </span>
                        )}
                        {!u.is_https && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800">
                            HTTP Insecure
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* 4. SAFE NEXT STEPS */}
        {activeTab === 'safe_steps' && (
          <SafeActionGuide
            language={language}
            safeSteps={plainExp.safe_steps || []}
          />
        )}

        {/* 5. TECHNICAL FORENSICS (ELA / NOISE / INPAINTING) */}
        {activeTab === 'technical' && (
          <div className="space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider m-0">
                  Forensic Micro-Spectrums & Inpainting
                </h3>
                <p className="text-xs text-slate-500 m-0">
                  Pixel-level compression discrepancy (ELA), high-frequency noise gradients, and generative inpainting smoothing
                </p>
              </div>

              {/* SPECTRUM TOGGLE */}
              <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs">
                <button
                  onClick={() => setVisualSpectrum('heatmap')}
                  className={`px-3 py-1.5 rounded-lg font-medium transition cursor-pointer ${
                    visualSpectrum === 'heatmap' ? 'bg-white text-blue-700 shadow-2xs font-bold' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  ELA Heatmap
                </button>
                <button
                  onClick={() => setVisualSpectrum('diff')}
                  className={`px-3 py-1.5 rounded-lg font-medium transition cursor-pointer ${
                    visualSpectrum === 'diff' ? 'bg-white text-blue-700 shadow-2xs font-bold' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Difference Map
                </button>
                <button
                  onClick={() => setVisualSpectrum('noise')}
                  className={`px-3 py-1.5 rounded-lg font-medium transition cursor-pointer ${
                    visualSpectrum === 'noise' ? 'bg-white text-blue-700 shadow-2xs font-bold' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Noise Variance Map
                </button>
              </div>
            </div>

            {/* SPECTRUM CANVAS */}
            <div className="bg-slate-950 rounded-2xl p-4 flex items-center justify-center min-h-[340px] max-h-[480px] overflow-auto">
              {visualSpectrum === 'heatmap' && ela.heatmap_image ? (
                <img src={ela.heatmap_image} alt="ELA Heatmap" className="max-h-[420px] w-auto rounded-lg object-contain" />
              ) : visualSpectrum === 'diff' && ela.diff_image ? (
                <img src={ela.diff_image} alt="ELA Diff" className="max-h-[420px] w-auto rounded-lg object-contain" />
              ) : visualSpectrum === 'noise' && noise.noise_map_image ? (
                <img src={noise.noise_map_image} alt="Noise Map" className="max-h-[420px] w-auto rounded-lg object-contain" />
              ) : (
                <div className="text-center text-slate-400 text-xs">
                  Visual forensic spectrum not available for this file type.
                </div>
              )}
            </div>

            {/* TELEMETRY DATA GRID */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 block">Avg ELA Delta</span>
                <span className="text-base font-bold font-mono text-slate-800">{ela.average_difference ?? 'N/A'}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 block">Noise Anomaly</span>
                <span className="text-base font-bold font-mono text-slate-800">{noise.anomaly_detected ? 'Detected' : 'Normal'}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 block">AI Inpainting</span>
                <span className="text-base font-bold font-mono text-slate-800">{proofly.ai_inpainting?.inpainting_detected ? 'Flagged' : 'None'}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 block">Deep Learning</span>
                <span className="text-base font-bold font-mono text-slate-800">{fa.ml_inference?.prediction || 'Normal'}</span>
              </div>
            </div>
          </div>
        )}

        {/* 6. OCR EXTRACTED TEXT */}
        {activeTab === 'ocr' && (
          <div className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider m-0">
                  Extracted Document Text
                </h3>
                <p className="text-xs text-slate-500 m-0">
                  Confidence: {analysisResult.ocr_confidence ?? 0}% • {analysisResult.ocr_words?.length ?? 0} words localized
                </p>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleCopy('ocr', analysisResult.extracted_text)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-xs font-semibold text-slate-700 transition cursor-pointer"
                >
                  {copiedKey === 'ocr' ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
                  <span>{copiedKey === 'ocr' ? 'Copied' : 'Copy Text'}</span>
                </button>

                <button
                  onClick={handleDownloadOcrTxt}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-xs font-semibold text-slate-700 transition cursor-pointer"
                >
                  <Download className="h-3.5 w-3.5" />
                  <span>Export .txt</span>
                </button>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 font-mono text-xs text-slate-800 leading-relaxed whitespace-pre-wrap max-h-[400px] overflow-auto select-all">
              {analysisResult.extracted_text || 'No text extracted from this document.'}
            </div>
          </div>
        )}

        {/* 7. EVIDENCE DOSSIER / REPORT */}
        {activeTab === 'report' && (
          <div className="space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider m-0">
                  Proofly Case Evidence Dossier
                </h3>
                <p className="text-xs text-slate-500 m-0">
                  Formal audit record generated for investor protection & regulatory compliance
                </p>
              </div>

              <button
                onClick={onDownloadReport}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-xs transition cursor-pointer"
              >
                <Download className="h-4 w-4" />
                <span>Download Structured JSON</span>
              </button>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3 font-mono text-xs">
              <div className="flex items-center justify-between border-b border-slate-200/60 pb-2">
                <span className="text-slate-500">Document Filename:</span>
                <span className="font-bold text-slate-800">{analysisResult.filename}</span>
              </div>
              <div className="flex items-center justify-between border-b border-slate-200/60 pb-2">
                <span className="text-slate-500">SHA-256 Checksum:</span>
                <span className="text-[11px] text-slate-700 truncate max-w-[280px]">
                  {proofly.file_hash_sha256 || 'Calculated on upload'}
                </span>
              </div>
              <div className="flex items-center justify-between border-b border-slate-200/60 pb-2">
                <span className="text-slate-500">Verification Concern Level:</span>
                <span className="font-bold text-rose-700">
                  {proofly.assessment?.concern_level || analysisResult.concern_level || 'LOW'}
                </span>
              </div>
              <div className="flex items-center justify-between border-b border-slate-200/60 pb-2">
                <span className="text-slate-500">Total Flagged Evidence Regions:</span>
                <span className="font-bold text-slate-800">{visualBoxes.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Timestamp (UTC):</span>
                <span className="text-slate-700">{proofly.timestamp_utc || new Date().toISOString()}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
