import React from 'react';
import {
  X,
  FileCode,
  HelpCircle,
  Settings,
  History,
  CheckCircle2,
  AlertTriangle,
  Cpu,
  Layers,
  Search,
  Lock,
  ExternalLink,
  RotateCcw
} from 'lucide-react';

export default function Modals({
  activeModal,
  onClose,
  history = [],
  onSelectHistoryItem,
  backendStatus
}) {
  if (!activeModal) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden animate-fadeIn">
        {/* MODAL HEADER */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            {activeModal === 'formats' && <FileCode className="h-5 w-5 text-blue-600" />}
            {activeModal === 'how-it-works' && <HelpCircle className="h-5 w-5 text-blue-600" />}
            {activeModal === 'history' && <History className="h-5 w-5 text-blue-600" />}
            {activeModal === 'settings' && <Settings className="h-5 w-5 text-blue-600" />}
            <h3 className="text-base font-bold text-slate-900 m-0">
              {activeModal === 'formats' && 'Supported Document Formats'}
              {activeModal === 'how-it-works' && 'How Proofly Investor Works'}
              {activeModal === 'history' && 'Analysis Session History'}
              {activeModal === 'settings' && 'System Configuration'}
            </h3>
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition cursor-pointer"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* MODAL CONTENT */}
        <div className="p-6 overflow-y-auto space-y-4 text-xs text-slate-600 leading-relaxed">
          {/* 1. SUPPORTED FORMATS */}
          {activeModal === 'formats' && (
            <div className="space-y-4">
              <p className="text-slate-600 m-0">
                Proofly Investor employs strict magic-byte binary header validation to ensure uploaded documents match their claimed extensions. Executables, scripts, and spoofed extensions are automatically rejected.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {[
                  { ext: 'PDF', name: 'Portable Document Format', desc: 'Vector & scanned multi-page documents rendered at high DPI (pypdfium2).' },
                  { ext: 'DOCX', name: 'Microsoft Word Document', desc: 'Extracts paragraphs, tables, core metadata, and renders preview snapshots.' },
                  { ext: 'TIFF / TIF', name: 'Tagged Image File Format', desc: 'High-fidelity scanner outputs with multi-frame frame unpacking.' },
                  { ext: 'PNG', name: 'Portable Network Graphics', desc: 'Digital screenshot and line art inspection with transparency handling.' },
                  { ext: 'JPG / JPEG', name: 'Joint Photographic Experts Group', desc: 'Standard photo and scanned document compression inspection.' },
                  { ext: 'WEBP', name: 'Modern Web Image Format', desc: 'RIFF container extraction and standardized baseline recompression.' },
                  { ext: 'BMP', name: 'Bitmap Image File', desc: 'Uncompressed raw raster images converted for spatial variance analysis.' },
                ].map((f) => (
                  <div key={f.ext} className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono font-bold text-blue-700">{f.ext}</span>
                      <span className="text-[10px] text-slate-400">Max 30MB</span>
                    </div>
                    <div className="font-semibold text-slate-800 mb-0.5">{f.name}</div>
                    <p className="text-[11px] text-slate-500 m-0">{f.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 2. HOW IT WORKS / PROOFLY PHILOSOPHY */}
          {activeModal === 'how-it-works' && (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-blue-50/60 border border-blue-200 text-blue-950 space-y-1">
                <span className="font-bold text-xs uppercase tracking-wider text-blue-700 block">Product Philosophy</span>
                <p className="text-xs leading-relaxed italic m-0 font-medium">
                  "Proofly does not ask users to trust AI. It shows them the evidence that made a document worth questioning."
                </p>
              </div>

              <div className="space-y-3">
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
                  <span className="font-bold text-blue-700 block mb-1">1. Generative AI Erase & Inpainting Detection</span>
                  <p className="text-slate-500 m-0">
                    Scans for localized high-frequency noise residual suppression, DCT energy decay, and gradient boundary breaks typical of AI object removal and generative fill.
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
                  <span className="font-bold text-indigo-700 block mb-1">2. Critical Financial Field & Semantic Audit</span>
                  <p className="text-slate-500 m-0">
                    Detects altered monetary amounts (₹), return percentages, and flags semantic contradictions between written verbal words (e.g. "ten thousand") and numeric figures (₹90,000).
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
                  <span className="font-bold text-amber-700 block mb-1">3. Regulatory Reality & Scam Language</span>
                  <p className="text-slate-500 m-0">
                    Identifies statutorily prohibited promises (guaranteed returns under SEBI regulations), false authority endorsements ("SEBI approved"), and artificial countdowns.
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
                  <span className="font-bold text-rose-700 block mb-1">4. Zero-Click QR & Identity Consistency</span>
                  <p className="text-slate-500 m-0">
                    Decodes QR codes to uncover direct money redirects to personal UPI IDs, flags lookalike domains, and exposes corporate entities using generic public emails.
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-950">
                  <span className="font-bold text-xs uppercase tracking-wider text-emerald-800 block mb-1">Strict Guardrail Compliance</span>
                  <p className="text-[11px] leading-relaxed text-emerald-800 m-0">
                    Proofly never gives stock tips, buy/sell recommendations, price predictions, or guaranteed legal fraud verdicts. It empowers first-time and Tier-2/3 investors to make safer decisions before sending funds.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* 3. SESSION HISTORY */}
          {activeModal === 'history' && (
            <div className="space-y-3">
              {history.length > 0 ? (
                history.map((h, i) => (
                  <div
                    key={i}
                    onClick={() => {
                      onSelectHistoryItem(h);
                      onClose();
                    }}
                    className="p-3.5 rounded-xl bg-slate-50 hover:bg-blue-50/50 border border-slate-200 hover:border-blue-300 transition cursor-pointer flex items-center justify-between"
                  >
                    <div>
                      <h4 className="font-bold text-slate-900 text-xs m-0">{h.filename}</h4>
                      <p className="text-[11px] text-slate-500 font-mono m-0">
                        {h.document_type} • Score: {h.risk_score}/100 • Conf: {h.confidence_score}%
                      </p>
                    </div>

                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase font-mono ${
                        h.risk_score >= 76
                          ? 'bg-rose-100 text-rose-800'
                          : h.risk_score >= 26
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-emerald-100 text-emerald-800'
                      }`}
                    >
                      {h.authenticity_status || h.classification}
                    </span>
                  </div>
                ))
              ) : (
                <div className="text-center py-12 text-slate-400">
                  No documents analyzed in this session yet.
                </div>
              )}
            </div>
          )}

          {/* 4. SETTINGS */}
          {activeModal === 'settings' && (
            <div className="space-y-4">
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                <span className="font-bold text-slate-800 block">Backend Endpoint Status</span>
                <div className="flex items-center justify-between text-slate-600">
                  <span>FastAPI Service:</span>
                  <span className="font-mono text-emerald-600 font-semibold">
                    {backendStatus?.status === 'HEALTHY' ? 'Online & Healthy' : 'Disconnected'}
                  </span>
                </div>
                <div className="flex items-center justify-between text-slate-600">
                  <span>Tesseract Engine:</span>
                  <span className="font-mono text-slate-700">
                    {backendStatus?.ocr_available ? 'Configured (v5.x)' : 'Not Found'}
                  </span>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                <span className="font-bold text-slate-800 block">Privacy & Storage Policy</span>
                <p className="text-slate-500 m-0">
                  Uploaded files are isolated using random UUIDs and erased following forensic processing. Previews are transmitted in transient base64 format.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* MODAL FOOTER */}
        <div className="px-6 py-3.5 border-t border-slate-100 bg-slate-50/60 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold shadow-xs transition cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
