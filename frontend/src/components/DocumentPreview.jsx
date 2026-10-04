import React, { useState } from 'react';
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  FileText,
  Eye,
  Layers,
  Sparkles,
  Maximize2,
  MessageSquare,
  Globe,
  AlertTriangle,
  ShieldAlert,
  Link
} from 'lucide-react';

export default function DocumentPreview({
  previewImage,
  filename,
  documentType,
  imageProps,
  ocrWords = [],
  totalPages = 1,
  showOcrBoxes,
  setShowOcrBoxes,
  analysisResult
}) {
  const [zoomLevel, setZoomLevel] = useState(1);

  const handleZoomIn = () => setZoomLevel((prev) => Math.min(2.5, prev + 0.2));
  const handleZoomOut = () => setZoomLevel((prev) => Math.max(0.6, prev - 0.2));
  const handleResetZoom = () => setZoomLevel(1);

  const isTextMode = analysisResult?.mode === 'TEXT_URL_ANALYSIS';
  const scamIndicators = analysisResult?.scam_indicators || [];
  const urlAnalysis = analysisResult?.url_analysis || {};

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs p-6 flex flex-col justify-between h-full">
      <div>
        {/* Header bar with controls */}
        <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-xs">
              2
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider m-0">
                {isTextMode ? 'Message & Link Inspection' : 'Document Preview'}
              </h2>
              {filename && (
                <p className="text-[11px] text-slate-500 font-mono truncate max-w-[200px] m-0">
                  {filename}
                </p>
              )}
            </div>
          </div>

          {/* Zoom Controls (Document Mode) */}
          {previewImage && !isTextMode && (
            <div className="flex items-center gap-2">
              <label className="hidden sm:flex items-center gap-1.5 text-[11px] text-slate-600 cursor-pointer select-none mr-1">
                <input
                  type="checkbox"
                  checked={showOcrBoxes}
                  onChange={(e) => setShowOcrBoxes(e.target.checked)}
                  className="rounded border-slate-300 text-blue-600 focus:ring-0 cursor-pointer"
                />
                <span>OCR Boxes</span>
              </label>

              <div className="flex items-center bg-slate-100 px-2 py-1 rounded-lg border border-slate-200 text-xs">
                <button
                  onClick={handleZoomOut}
                  className="p-1 text-slate-600 hover:text-blue-600 transition cursor-pointer"
                  title="Zoom Out"
                >
                  <ZoomOut className="h-3.5 w-3.5" />
                </button>
                <span className="font-mono text-slate-600 w-10 text-center text-[11px]">
                  {Math.round(zoomLevel * 100)}%
                </span>
                <button
                  onClick={handleZoomIn}
                  className="p-1 text-slate-600 hover:text-blue-600 transition cursor-pointer"
                  title="Zoom In"
                >
                  <ZoomIn className="h-3.5 w-3.5" />
                </button>
                <button
                  onClick={handleResetZoom}
                  className="text-[10px] text-slate-400 hover:text-slate-700 ml-1.5 pl-1.5 border-l border-slate-300 cursor-pointer"
                  title="Reset Zoom"
                >
                  Reset
                </button>
              </div>
            </div>
          )}
        </div>

        {/* PREVIEW CONTAINER */}
        <div className="relative rounded-xl bg-slate-50/80 border border-slate-200/80 overflow-auto min-h-[280px] max-h-[440px] flex items-center justify-center p-4">
          {isTextMode ? (
            /* TEXT / LINK ANALYSIS PREVIEW */
            <div className="w-full space-y-3">
              {/* Message Box */}
              <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1">
                    <MessageSquare className="h-3 w-3 text-blue-600" />
                    Incoming Investment Communication
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-50 text-blue-700 font-semibold">
                    {scamIndicators.length} Triggers
                  </span>
                </div>
                <p className="text-xs text-slate-800 leading-relaxed font-sans m-0">
                  {analysisResult.text_preview || analysisResult.extracted_text || 'Text analysis payload'}
                </p>
              </div>

              {/* URL / Link Card if available */}
              {urlAnalysis.url && (
                <div className="p-3 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1">
                      <Globe className="h-3 w-3 text-indigo-600" />
                      Attached Website Link
                    </span>
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase ${
                      urlAnalysis.level === 'HIGH' ? 'bg-rose-100 text-rose-800' : 'bg-emerald-100 text-emerald-800'
                    }`}>
                      {urlAnalysis.level} Risk Link
                    </span>
                  </div>
                  <div className="text-xs font-mono font-semibold text-slate-900 truncate">
                    {urlAnalysis.url}
                  </div>
                  {urlAnalysis.concerns && urlAnalysis.concerns.length > 0 && (
                    <div className="space-y-1 mt-1">
                      {urlAnalysis.concerns.map((c, i) => (
                        <div key={i} className="text-[10px] text-rose-600 flex items-start gap-1">
                          <AlertTriangle className="h-3 w-3 shrink-0 mt-0.5" />
                          <span>{c}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : previewImage ? (
            /* IMAGE PREVIEW */
            <div
              className="transition-transform duration-200 origin-center relative inline-block"
              style={{ transform: `scale(${zoomLevel})` }}
            >
              <img
                src={previewImage}
                alt={filename || 'Document Preview'}
                className="max-h-[380px] w-auto rounded-lg shadow-sm object-contain bg-white"
              />

              {/* OCR Word Boxes overlay */}
              {showOcrBoxes && ocrWords && ocrWords.length > 0 && (
                <div className="absolute inset-0 pointer-events-none">
                  {ocrWords.slice(0, 75).map((w, i) => (
                    <div
                      key={i}
                      className="absolute border border-blue-500/70 bg-blue-500/10 rounded-[2px]"
                      style={{
                        left: `${(w.x / 1200) * 100}%`,
                        top: `${(w.y / 1600) * 100}%`,
                        width: `${(w.w / 1200) * 100}%`,
                        height: `${(w.h / 1600) * 100}%`
                      }}
                      title={`${w.text} (${w.confidence}%)`}
                    />
                  ))}
                </div>
              )}
            </div>
          ) : (
            /* EMPTY STATE */
            <div className="text-center py-12 px-4 space-y-3">
              <div className="h-14 w-14 rounded-2xl bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-400 mx-auto">
                <FileText className="h-7 w-7" />
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-700 mb-0.5">
                  No Document Loaded
                </p>
                <p className="text-[11px] text-slate-400 max-w-[220px] mx-auto m-0">
                  Upload a document or choose a sample to inspect the high-resolution raster preview.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* FOOTER BADGES */}
      {(previewImage || isTextMode) && (
        <div className="mt-4 pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-500 font-mono">
          <div className="flex items-center gap-1.5">
            <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-semibold">
              {isTextMode ? 'Direct Message / URL' : (documentType || 'General Document')}
            </span>
            {totalPages > 1 && (
              <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                {totalPages} Pages
              </span>
            )}
          </div>

          {imageProps && !isTextMode && (
            <span className="text-slate-400">
              {imageProps.width} × {imageProps.height} px • {imageProps.format || 'RASTER'}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
