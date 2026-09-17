import React, { useState } from 'react';
import {
  AlertTriangle,
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
  Layers,
  ShieldAlert,
  Sparkles,
  ChevronRight
} from 'lucide-react';
import ChecklistRows from './ChecklistRows';

export default function ResultTabs({ analysisResult, onDownloadReport }) {
  const [activeTab, setActiveTab] = useState('issues'); // 'issues', 'ocr', 'metadata', 'ela', 'report'
  const [visualSpectrum, setVisualSpectrum] = useState('heatmap'); // 'heatmap', 'diff', 'noise'
  const [zoomLevel, setZoomLevel] = useState(1);
  const [copiedKey, setCopiedKey] = useState(null);
  const [ocrFilter, setOcrFilter] = useState('');

  if (!analysisResult) return null;

  const fa = analysisResult.forgery_analysis || {};
  const ela = fa.ela_analysis || {};
  const noise = fa.noise_analysis || {};
  const meta = fa.metadata_forensics || {};
  const indicators = analysisResult.indicators || fa.indicators || [];

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
    { id: 'issues', label: 'Detected Issues', count: indicators.length, icon: AlertTriangle },
    { id: 'ocr', label: 'OCR Text', icon: FileText },
    { id: 'metadata', label: 'Metadata & Container', icon: Search },
    { id: 'ela', label: 'ELA Analysis', icon: Cpu },
    { id: 'report', label: 'Detailed Report', icon: FileCheck2 },
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
              {t.count !== undefined && t.count > 0 && (
                <span
                  className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono ${
                    isActive ? 'bg-blue-100 text-blue-700' : 'bg-slate-200/80 text-slate-700'
                  }`}
                >
                  {t.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* TAB PANELS */}
      <div className="p-6">
        {/* 1. DETECTED ISSUES */}
        {activeTab === 'issues' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-900 m-0">
                  Forensic Findings & Tampering Indicators
                </h3>
                <p className="text-xs text-slate-500 m-0">
                  Telemetry detected across compression boundaries, noise distribution, and container metadata.
                </p>
              </div>
              <span className="text-xs font-mono text-slate-500 font-medium">
                {indicators.length} recorded signals
              </span>
            </div>

            {indicators.length > 0 ? (
              <div className="space-y-3">
                {indicators.map((ind, i) => {
                  const isCrit = ind.severity === 'CRITICAL';
                  const isWarn = ind.severity === 'WARNING';
                  const isVerif = ind.severity === 'VERIFIED';
                  return (
                    <div
                      key={i}
                      className={`p-4 rounded-xl border text-xs leading-relaxed transition ${
                        isCrit
                          ? 'bg-rose-50/60 border-rose-200'
                          : isWarn
                          ? 'bg-amber-50/60 border-amber-200'
                          : isVerif
                          ? 'bg-emerald-50/60 border-emerald-200'
                          : 'bg-slate-50 border-slate-200'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2 mb-1.5">
                        <span
                          className={`font-bold text-xs ${
                            isCrit ? 'text-rose-900' : isWarn ? 'text-amber-900' : isVerif ? 'text-emerald-900' : 'text-slate-900'
                          }`}
                        >
                          {ind.title}
                        </span>
                        <div className="flex items-center gap-2">
                          {ind.weight !== undefined && (
                            <span className="text-[10px] font-mono text-slate-500">
                              Weight: +{ind.weight}
                            </span>
                          )}
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                              isCrit
                                ? 'bg-rose-200/80 text-rose-900'
                                : isWarn
                                ? 'bg-amber-200/80 text-amber-900'
                                : isVerif
                                ? 'bg-emerald-200/80 text-emerald-900'
                                : 'bg-slate-200 text-slate-700'
                            }`}
                          >
                            {ind.severity}
                          </span>
                        </div>
                      </div>
                      <p className="text-slate-600 m-0 leading-relaxed">
                        {ind.description}
                      </p>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="p-8 text-center bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-500">
                No anomalous tampering indicators flagged for this document.
              </div>
            )}
          </div>
        )}

        {/* 2. OCR TEXT */}
        {activeTab === 'ocr' && (
          <div className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-3">
              <div className="flex items-center gap-4">
                <div>
                  <span className="text-[11px] text-slate-400 font-medium">Average OCR Confidence</span>
                  <div className="text-lg font-bold font-mono text-blue-600">
                    {analysisResult.ocr_confidence ? `${analysisResult.ocr_confidence}%` : 'N/A'}
                  </div>
                </div>
                <div className="h-7 w-px bg-slate-200" />
                <div>
                  <span className="text-[11px] text-slate-400 font-medium">Total Words Extracted</span>
                  <div className="text-lg font-bold font-mono text-slate-800">
                    {analysisResult.ocr_words?.length || 0}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleDownloadOcrTxt}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold border border-slate-200 transition cursor-pointer"
                >
                  <Download className="h-3.5 w-3.5" />
                  <span>Download .txt</span>
                </button>
                <button
                  onClick={() => handleCopy('ocr_all', analysisResult.extracted_text)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-semibold border border-blue-200 transition cursor-pointer"
                >
                  {copiedKey === 'ocr_all' ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
                  <span>Copy Text</span>
                </button>
              </div>
            </div>

            {/* Filter Input */}
            <input
              type="text"
              placeholder="Search or filter recognized lines..."
              value={ocrFilter}
              onChange={(e) => setOcrFilter(e.target.value)}
              className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white transition"
            />

            {/* Extracted Text Content Box */}
            <div className="p-4 rounded-xl bg-slate-50/70 border border-slate-200 font-mono text-xs text-slate-700 leading-relaxed max-h-80 overflow-y-auto whitespace-pre-wrap select-all">
              {analysisResult.extracted_text ? (
                ocrFilter ? (
                  analysisResult.extracted_text
                    .split('\n')
                    .filter((line) => line.toLowerCase().includes(ocrFilter.toLowerCase()))
                    .join('\n') || 'No matching lines found.'
                ) : (
                  analysisResult.extracted_text
                )
              ) : (
                'No textual content recognized by OCR engine.'
              )}
            </div>
          </div>
        )}

        {/* 3. METADATA & CONTAINER */}
        {activeTab === 'metadata' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Image / Container Properties */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 m-0">
                Container Properties
              </h4>
              <div className="rounded-xl border border-slate-200 overflow-hidden text-xs">
                <div className="flex justify-between p-3 bg-white border-b border-slate-100">
                  <span className="text-slate-500 font-medium">Claimed Format:</span>
                  <span className="font-mono font-bold text-slate-800">
                    {fa.image_analysis?.format || 'UNKNOWN'}
                  </span>
                </div>
                <div className="flex justify-between p-3 bg-slate-50/50 border-b border-slate-100">
                  <span className="text-slate-500 font-medium">Dimensions:</span>
                  <span className="font-mono text-slate-800">
                    {fa.image_analysis?.width} × {fa.image_analysis?.height} px
                  </span>
                </div>
                <div className="flex justify-between p-3 bg-white border-b border-slate-100">
                  <span className="text-slate-500 font-medium">Hardware / Camera EXIF:</span>
                  <span className="font-medium text-slate-800">
                    {meta.camera_model || 'None specified / Stripped'}
                  </span>
                </div>
                <div className="flex justify-between p-3 bg-slate-50/50">
                  <span className="text-slate-500 font-medium">EXIF Capture Timestamp:</span>
                  <span className="font-mono text-slate-800">
                    {meta.date_time_original || 'Not stamped'}
                  </span>
                </div>
              </div>
            </div>

            {/* Software Traces & Extended Metadata */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 m-0">
                Software & Manipulation Traces
              </h4>

              {meta.editing_software_detected ? (
                <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs space-y-1">
                  <div className="font-bold flex items-center gap-1.5">
                    <AlertTriangle className="h-4 w-4 text-rose-600" />
                    <span>Photo Manipulation Tool Signature Detected</span>
                  </div>
                  <p className="font-mono font-semibold text-rose-900 m-0">
                    {meta.detected_software_name}
                  </p>
                </div>
              ) : (
                <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs">
                  <span className="font-bold">✓ Clean Container: </span>
                  No known photo-editing signatures (Photoshop, Canva, GIMP, Photopea) detected in file headers.
                </div>
              )}

              {/* DOCX Package Properties if DOCX */}
              {meta.docx_properties && (
                <div className="rounded-xl border border-slate-200 p-3 bg-slate-50/50 space-y-1.5 text-xs">
                  <span className="font-bold text-slate-800 block">DOCX Core Package:</span>
                  <div className="text-slate-600">Author: <span className="font-mono font-medium text-slate-900">{meta.docx_properties.author}</span></div>
                  <div className="text-slate-600">Modified By: <span className="font-mono font-medium text-slate-900">{meta.docx_properties.last_modified_by}</span></div>
                  <div className="text-slate-600">Revisions: <span className="font-mono font-medium text-slate-900">{meta.docx_properties.revision}</span></div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 4. ELA ANALYSIS (Multi-Spectrum Visual Inspector) */}
        {activeTab === 'ela' && (
          <div className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-3">
              {/* Spectrum selector buttons */}
              <div className="flex gap-1.5">
                <button
                  onClick={() => setVisualSpectrum('heatmap')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                    visualSpectrum === 'heatmap'
                      ? 'bg-rose-50 text-rose-700 border border-rose-200'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200 border border-transparent'
                  }`}
                >
                  🔥 Thermal ELA Heatmap
                </button>
                <button
                  onClick={() => setVisualSpectrum('diff')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                    visualSpectrum === 'diff'
                      ? 'bg-purple-50 text-purple-700 border border-purple-200'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200 border border-transparent'
                  }`}
                >
                  Grayscale Delta (15x)
                </button>
                <button
                  onClick={() => setVisualSpectrum('noise')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                    visualSpectrum === 'noise'
                      ? 'bg-amber-50 text-amber-700 border border-amber-200'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200 border border-transparent'
                  }`}
                >
                  Noise Splicing Map
                </button>
              </div>

              {/* Zoom controls */}
              <div className="flex items-center bg-slate-100 px-2 py-1 rounded-lg border border-slate-200 text-xs">
                <button
                  onClick={() => setZoomLevel((z) => Math.max(0.6, z - 0.2))}
                  className="p-1 text-slate-600 hover:text-blue-600 cursor-pointer"
                  title="Zoom Out"
                >
                  <ZoomOut className="h-3.5 w-3.5" />
                </button>
                <span className="font-mono text-slate-600 w-10 text-center text-[11px]">
                  {Math.round(zoomLevel * 100)}%
                </span>
                <button
                  onClick={() => setZoomLevel((z) => Math.min(2.5, z + 0.2))}
                  className="p-1 text-slate-600 hover:text-blue-600 cursor-pointer"
                  title="Zoom In"
                >
                  <ZoomIn className="h-3.5 w-3.5" />
                </button>
                <button
                  onClick={() => setZoomLevel(1)}
                  className="text-[10px] text-slate-400 hover:text-slate-700 ml-1.5 pl-1.5 border-l border-slate-300 cursor-pointer"
                >
                  Reset
                </button>
              </div>
            </div>

            {/* Spectrum Render Canvas */}
            <div className="rounded-xl bg-slate-900 overflow-auto min-h-[320px] max-h-[500px] flex items-center justify-center p-4">
              <div
                className="transition-transform duration-200 origin-center"
                style={{ transform: `scale(${zoomLevel})` }}
              >
                {visualSpectrum === 'heatmap' && (
                  ela.heatmap_image ? (
                    <img src={ela.heatmap_image} alt="ELA Heatmap" className="max-h-[440px] w-auto rounded shadow-md" />
                  ) : (
                    <p className="text-slate-400 text-xs">ELA Heatmap not generated for this format.</p>
                  )
                )}

                {visualSpectrum === 'diff' && (
                  ela.diff_image ? (
                    <img src={ela.diff_image} alt="ELA Difference" className="max-h-[440px] w-auto rounded shadow-md" />
                  ) : (
                    <p className="text-slate-400 text-xs">ELA Grayscale difference not available.</p>
                  )
                )}

                {visualSpectrum === 'noise' && (
                  noise.noise_map_image ? (
                    <img src={noise.noise_map_image} alt="Noise Map" className="max-h-[440px] w-auto rounded shadow-md" />
                  ) : (
                    <p className="text-slate-400 text-xs">Noise splicing map not available.</p>
                  )
                )}
              </div>
            </div>

            {/* Visual Interpretation Caption */}
            <div className="p-3 rounded-xl bg-blue-50/50 border border-blue-100 text-xs text-slate-600 flex items-center gap-2">
              <Info className="h-4 w-4 text-blue-600 shrink-0" />
              <span>
                {visualSpectrum === 'heatmap' && 'Thermal Jet Colormap: Localized red/yellow clusters signify high compression deviation indicative of pasted or digitally edited layers.'}
                {visualSpectrum === 'diff' && 'Amplified 15x pixel delta against baseline recompression to uncover hidden JPEG block boundary mismatches.'}
                {visualSpectrum === 'noise' && 'Red bounding boxes flag tiles whose noise variance deviates by >2.5σ from median background grain.'}
              </span>
            </div>
          </div>
        )}

        {/* 5. DETAILED REPORT */}
        {activeTab === 'report' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900 m-0">
                  Comprehensive 6-Point Forensic Audit Checklist
                </h3>
                <p className="text-xs text-slate-500 m-0">
                  Systematic verification across all primary forensic tampering vectors.
                </p>
              </div>

              <button
                onClick={onDownloadReport}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-xs transition cursor-pointer"
              >
                <Download className="h-3.5 w-3.5" />
                <span>Export Audit JSON</span>
              </button>
            </div>

            {/* Checklist Rows Component */}
            <ChecklistRows analysisResult={analysisResult} />

            {/* Structured Extracted Domain Data (if any) */}
            {analysisResult.extracted_fields && Object.keys(analysisResult.extracted_fields).length > 0 && (
              <div className="pt-4 border-t border-slate-100 space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 m-0">
                  Extracted Document Fields ({analysisResult.document_type})
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5">
                  {Object.entries(analysisResult.extracted_fields)
                    .filter(([k]) => !['validations', 'numbers', 'dates', 'names'].includes(k))
                    .map(([key, val]) => {
                      if (!val) return null;
                      const label = key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
                      return (
                        <div key={key} className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-xs flex justify-between items-center">
                          <span className="text-slate-500 font-medium">{label}:</span>
                          <span className="font-mono font-semibold text-slate-800">{String(val)}</span>
                        </div>
                      );
                    })}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
