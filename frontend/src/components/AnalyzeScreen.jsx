import React, { useRef, useState } from 'react';
import {
  UploadCloud,
  FileText,
  MessageSquare,
  Link,
  ArrowRight,
  Loader2,
  X,
  Sparkles,
  AlertCircle,
  ShieldAlert,
  Layers,
  Scale
} from 'lucide-react';

export default function AnalyzeScreen({
  onAnalyzeFile,
  onAnalyzeText,
  onRunDemo,
  isAnalyzing,
  analysisStep,
  pipelineSteps = [],
  errorMessage,
  language = 'en'
}) {
  const [activeTab, setActiveTab] = useState('upload'); // 'upload' | 'text'
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [pastedText, setPastedText] = useState('');
  const [pastedUrl, setPastedUrl] = useState('');
  const fileInputRef = useRef(null);

  const demoOptions = [
    {
      id: 'guaranteed_return',
      label: 'Scam Demo (60% Guaranteed Return)',
      badge: 'Codex Scam',
      badgeColor: 'bg-rose-100 text-rose-800'
    },
    {
      id: 'broker_impersonation',
      label: 'CedarBridge Clearance (SEBI Impersonation)',
      badge: 'Codex Alert',
      badgeColor: 'bg-amber-100 text-amber-800'
    },
    {
      id: 'educational_control',
      label: 'Riverstone Handout (Low-Risk Control)',
      badge: 'Codex Control',
      badgeColor: 'bg-emerald-100 text-emerald-800'
    },
    {
      id: 'tampered_demo',
      label: 'Document Forgery Pair (₹5k -> ₹50k)',
      badge: 'Codex Forgery',
      badgeColor: 'bg-indigo-100 text-indigo-800'
    }
  ];

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
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleStartAnalysis = () => {
    if (activeTab === 'upload' && selectedFile) {
      onAnalyzeFile(selectedFile);
    } else if (activeTab === 'text') {
      onAnalyzeText({ text: pastedText, url: pastedUrl });
    }
  };

  const isReady = activeTab === 'upload' ? !!selectedFile : (pastedText.trim().length > 0 || pastedUrl.trim().length > 0);

  return (
    <div className="max-w-3xl mx-auto py-4 space-y-6">
      {/* Title */}
      <div className="text-center space-y-1">
        <h2 className="text-2xl font-black text-slate-900 tracking-tight m-0">
          Analyze Document or Message
        </h2>
        <p className="text-xs text-slate-500 m-0">
          Choose an input method or select one of the curated Codex demo cases below.
        </p>
      </div>

      {/* QUICK TRY DEMO ROW */}
      <div className="bg-gradient-to-r from-blue-50/60 to-indigo-50/60 border border-blue-200/80 rounded-2xl p-4 space-y-2.5">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-blue-950 flex items-center gap-1.5 uppercase tracking-wider">
            <Sparkles className="h-4 w-4 text-blue-600" />
            <span>Try Codex Demo Scenarios (Instant 1-Click)</span>
          </span>
          <span className="text-[10px] font-mono text-blue-600 font-semibold">
            SANGYAN QA Verified
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {demoOptions.map((d) => (
            <button
              key={d.id}
              onClick={() => onRunDemo(d.id)}
              disabled={isAnalyzing}
              className="p-2.5 rounded-xl bg-white hover:bg-blue-50 border border-slate-200 hover:border-blue-400 text-left transition cursor-pointer flex items-center justify-between gap-2 shadow-2xs disabled:opacity-50"
            >
              <div className="truncate">
                <div className="text-xs font-bold text-slate-800 truncate">{d.label}</div>
              </div>
              <span className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold shrink-0 ${d.badgeColor}`}>
                {d.badge}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* MAIN INPUT CARD */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-5">
        {/* Tab Toggle */}
        <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200/80">
          <button
            onClick={() => setActiveTab('upload')}
            className={`flex-1 py-2 rounded-lg text-xs font-bold transition cursor-pointer flex items-center justify-center gap-2 ${
              activeTab === 'upload'
                ? 'bg-white text-blue-700 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <FileText className="h-4 w-4" />
            <span>Upload Image / PDF Document</span>
          </button>

          <button
            onClick={() => setActiveTab('text')}
            className={`flex-1 py-2 rounded-lg text-xs font-bold transition cursor-pointer flex items-center justify-center gap-2 ${
              activeTab === 'text'
                ? 'bg-white text-blue-700 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <MessageSquare className="h-4 w-4" />
            <span>Paste Suspicious Text / Link</span>
          </button>
        </div>

        {/* TAB 1: UPLOAD */}
        {activeTab === 'upload' ? (
          <div>
            {!selectedFile ? (
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-xl p-8 text-center transition cursor-pointer flex flex-col items-center justify-center min-h-[220px] ${
                  isDragging
                    ? 'border-blue-500 bg-blue-50/50'
                    : 'border-slate-300 hover:border-blue-400 bg-slate-50/60 hover:bg-blue-50/20'
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  className="hidden"
                  accept=".jpg,.jpeg,.png,.webp,.pdf,.tif,.tiff,.bmp,.docx"
                  onChange={handleFileChange}
                />
                <div className="h-12 w-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
                  <UploadCloud className="h-6 w-6" />
                </div>
                <p className="text-xs font-semibold text-slate-800 mb-1">
                  Drag and drop document here, or <span className="text-blue-600 underline">browse</span>
                </p>
                <p className="text-[11px] text-slate-400 m-0">
                  Supported formats: PDF, DOCX, JPG, PNG, WEBP, TIFF, BMP (Max 30MB)
                </p>
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-blue-50/50 border border-blue-200 flex items-center justify-between">
                <div className="flex items-center gap-3 overflow-hidden">
                  <div className="h-10 w-10 rounded-xl bg-blue-600 text-white flex items-center justify-center shrink-0">
                    <FileText className="h-5 w-5" />
                  </div>
                  <div className="overflow-hidden">
                    <h4 className="text-xs font-bold text-slate-900 truncate m-0">{selectedFile.name}</h4>
                    <p className="text-[11px] text-slate-500 m-0">
                      {(selectedFile.size / 1024).toFixed(1)} KB • Ready for analysis
                    </p>
                  </div>
                </div>
                {!isAnalyzing && (
                  <button
                    onClick={() => setSelectedFile(null)}
                    className="p-1 rounded-lg text-slate-400 hover:text-rose-600 transition cursor-pointer"
                  >
                    <X className="h-4 w-4" />
                  </button>
                )}
              </div>
            )}
          </div>
        ) : (
          /* TAB 2: TEXT & URL */
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-800 mb-1">
                Paste Investment Message (WhatsApp / Telegram / SMS)
              </label>
              <textarea
                value={pastedText}
                onChange={(e) => setPastedText(e.target.value)}
                placeholder="Example: 'Invest ₹50,000 to receive ₹80,000 in 30 days! SEBI approved advisor. Pay immediately to UPI...'"
                rows={4}
                className="w-full text-xs p-3 rounded-xl border border-slate-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-hidden font-sans bg-slate-50/40"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-800 mb-1 flex items-center gap-1">
                <Link className="h-3.5 w-3.5 text-slate-500" />
                <span>Optional Website Link / URL</span>
              </label>
              <input
                type="url"
                value={pastedUrl}
                onChange={(e) => setPastedUrl(e.target.value)}
                placeholder="https://moonrise-fast-profit.example/activate"
                className="w-full text-xs px-3 py-2.5 rounded-xl border border-slate-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 font-mono outline-hidden bg-slate-50/40"
              />
            </div>
          </div>
        )}

        {/* Error message */}
        {errorMessage && (
          <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-start gap-2">
            <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-rose-600" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Progress indicator while analyzing */}
        {isAnalyzing && (
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2.5">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />
                <span>Running Proofly Multimodal Engine...</span>
              </div>
              <span className="font-mono text-[11px] text-blue-600">
                Step {analysisStep + 1}/{pipelineSteps.length || 6}
              </span>
            </div>
            <p className="text-[11px] text-slate-500 font-mono m-0 truncate">
              {pipelineSteps[analysisStep] || 'Correlating multimodal risk indicators...'}
            </p>
            <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
              <div
                className="bg-gradient-to-r from-blue-600 to-indigo-600 h-1.5 transition-all duration-300 rounded-full"
                style={{ width: `${((analysisStep + 1) / (pipelineSteps.length || 6)) * 100}%` }}
              />
            </div>
          </div>
        )}

        {/* ACTION BUTTON */}
        <button
          onClick={handleStartAnalysis}
          disabled={!isReady || isAnalyzing}
          className={`w-full py-3.5 px-4 rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 cursor-pointer shadow-sm ${
            !isReady || isAnalyzing
              ? 'bg-slate-100 text-slate-400 border border-slate-200 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 text-white shadow-blue-600/25'
          }`}
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Analyzing Evidence...</span>
            </>
          ) : (
            <>
              <span>Run Verification</span>
              <ArrowRight className="h-4 w-4" />
            </>
          )}
        </button>
      </div>
    </div>
  );
}
