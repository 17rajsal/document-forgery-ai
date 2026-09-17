import React, { useRef } from 'react';
import {
  UploadCloud,
  FileText,
  X,
  ArrowRight,
  Loader2,
  CheckCircle2,
  AlertCircle,
  ShieldAlert
} from 'lucide-react';

export default function UploadPanel({
  selectedFile,
  onFileSelected,
  onRemoveSelectedFile,
  onAnalyze,
  isAnalyzing,
  analysisStep,
  pipelineSteps,
  errorMessage,
  isDragging,
  setIsDragging
}) {
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelected(e.dataTransfer.files[0]);
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs p-6 flex flex-col justify-between h-full">
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-xs">
              1
            </div>
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider m-0">
              Upload Document
            </h2>
          </div>
          <span className="text-[11px] text-slate-500 font-mono">Max 30MB</span>
        </div>

        {/* DRAG AND DROP ZONE */}
        {!selectedFile ? (
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-8 text-center transition cursor-pointer flex flex-col items-center justify-center min-h-[220px] ${
              isDragging
                ? 'border-blue-500 bg-blue-50/50 scale-[0.99]'
                : 'border-slate-300 hover:border-blue-400 bg-slate-50/60 hover:bg-blue-50/20'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              accept=".jpg,.jpeg,.png,.webp,.pdf,.tif,.tiff,.bmp,.docx"
              onChange={(e) => e.target.files?.[0] && onFileSelected(e.target.files[0])}
            />

            <div className="h-14 w-14 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600 mb-3 group-hover:scale-105 transition-transform">
              <UploadCloud className="h-7 w-7" />
            </div>

            <p className="text-xs font-semibold text-slate-800 mb-1">
              Drag and drop your document here
            </p>
            <p className="text-[11px] text-slate-500 mb-4">
              or <span className="text-blue-600 font-medium hover:underline">browse files</span> from your device
            </p>

            <div className="flex flex-wrap items-center justify-center gap-1 max-w-xs">
              {['PDF', 'DOCX', 'JPG', 'PNG', 'WEBP', 'TIFF', 'BMP'].map((ext) => (
                <span
                  key={ext}
                  className="px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold bg-white border border-slate-200 text-slate-600"
                >
                  {ext}
                </span>
              ))}
            </div>
          </div>
        ) : (
          /* FILE SELECTED VIEW */
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-blue-50/40 border border-blue-100 flex items-start justify-between gap-3">
              <div className="flex items-center gap-3 overflow-hidden">
                <div className="h-10 w-10 rounded-xl bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-xs">
                  <FileText className="h-5 w-5" />
                </div>
                <div className="overflow-hidden">
                  <h4 className="text-xs font-bold text-slate-900 truncate m-0">
                    {selectedFile.name}
                  </h4>
                  <p className="text-[11px] text-slate-500 m-0">
                    {formatFileSize(selectedFile.size)} • {selectedFile.name.split('.').pop()?.toUpperCase()} Document
                  </p>
                </div>
              </div>

              {!isAnalyzing && (
                <button
                  onClick={onRemoveSelectedFile}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition cursor-pointer"
                  title="Remove selected document"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>

            {/* Error Message if any */}
            {errorMessage && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-start gap-2">
                <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-rose-600" />
                <span>{errorMessage}</span>
              </div>
            )}

            {/* PROGRESS STATE WHILE ANALYZING */}
            {isAnalyzing && (
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-3">
                <div className="flex items-center justify-between text-xs font-medium text-slate-700">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />
                    <span>Analyzing Document...</span>
                  </div>
                  <span className="font-mono text-[11px] text-blue-600">
                    Step {analysisStep + 1}/5
                  </span>
                </div>

                <p className="text-[11px] text-slate-500 font-mono m-0 h-4 truncate">
                  {pipelineSteps[analysisStep] || 'Finalizing forensic synthesis...'}
                </p>

                <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-blue-600 to-indigo-600 h-1.5 transition-all duration-300 rounded-full"
                    style={{ width: `${((analysisStep + 1) / pipelineSteps.length) * 100}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* ACTION BUTTON */}
      <div className="mt-6 pt-4 border-t border-slate-100">
        <button
          onClick={onAnalyze}
          disabled={!selectedFile || isAnalyzing}
          className={`w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-xs font-semibold shadow-xs transition cursor-pointer ${
            !selectedFile || isAnalyzing
              ? 'bg-slate-100 text-slate-400 border border-slate-200 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white shadow-blue-600/20'
          }`}
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Running Forensics...</span>
            </>
          ) : (
            <>
              <span>Analyze Document</span>
              <ArrowRight className="h-4 w-4" />
            </>
          )}
        </button>
      </div>
    </div>
  );
}
