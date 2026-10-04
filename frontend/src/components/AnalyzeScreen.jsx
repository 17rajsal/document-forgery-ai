import React, { useRef, useState } from 'react';
import {
  UploadCloud,
  FileText,
  MessageSquare,
  Link,
  ArrowRight,
  Loader2,
  X,
  AlertCircle,
  Camera,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import CameraCapture from './CameraCapture';

export default function AnalyzeScreen({
  onAnalyzeFile,
  onAnalyzeText,
  onRunSample,
  isAnalyzing,
  analysisStep,
  pipelineSteps = [],
  errorMessage,
  language = 'en'
}) {
  const [activeTab, setActiveTab] = useState('document'); // 'document' | 'message'
  const [documentInputMode, setDocumentInputMode] = useState('upload'); // 'upload' | 'camera'
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [pastedText, setPastedText] = useState('');
  const [pastedUrl, setPastedUrl] = useState('');
  const [showSamples, setShowSamples] = useState(false);
  const fileInputRef = useRef(null);

  const sampleOptions = [
    {
      id: 'guaranteed_return',
      title: 'Guaranteed Return Offer',
      desc: 'High-risk yield proposal promising fixed returns with artificial urgency.',
      tag: 'Sample data'
    },
    {
      id: 'broker_impersonation',
      title: 'Impersonated Authority Notice',
      desc: 'Falsely claimed official clearance notice demanding fee payments.',
      tag: 'Sample data'
    },
    {
      id: 'educational_control',
      title: 'Educational Advisory Material',
      desc: 'Standard risk education material explaining fee comparisons.',
      tag: 'Sample data'
    },
    {
      id: 'tampered_demo',
      title: 'Altered Document Record',
      desc: 'Demonstration of localized amount modification and typography disparity.',
      tag: 'Sample data'
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
    if (activeTab === 'document' && selectedFile) {
      onAnalyzeFile(selectedFile);
    } else if (activeTab === 'message') {
      onAnalyzeText({ text: pastedText, url: pastedUrl });
    }
  };

  const handlePhotoCaptured = (file) => {
    setSelectedFile(file);
    setDocumentInputMode('upload');
    onAnalyzeFile(file);
  };

  const isReady =
    activeTab === 'document'
      ? !!selectedFile
      : pastedText.trim().length > 0 || pastedUrl.trim().length > 0;

  return (
    <div className="max-w-3xl mx-auto py-4 space-y-6">
      {/* Title */}
      <div className="text-center space-y-1">
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight m-0">
          Analyze Document or Message
        </h2>
        <p className="text-xs text-slate-500 m-0">
          Inspect suspicious documents, messages, links, and QR codes for fraud indicators.
        </p>
      </div>

      {/* MAIN INPUT CARD */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-5 shadow-xs">
        {/* Main Tab Toggle: Document vs Message / URL */}
        <div className="flex items-center bg-slate-100 p-1 rounded-lg border border-slate-200">
          <button
            onClick={() => setActiveTab('document')}
            className={`flex-1 py-2 rounded-md text-xs font-semibold transition cursor-pointer flex items-center justify-center gap-2 ${
              activeTab === 'document'
                ? 'bg-white text-blue-600 shadow-2xs font-bold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <FileText className="h-4 w-4" />
            <span>Document</span>
          </button>

          <button
            onClick={() => setActiveTab('message')}
            className={`flex-1 py-2 rounded-md text-xs font-semibold transition cursor-pointer flex items-center justify-center gap-2 ${
              activeTab === 'message'
                ? 'bg-white text-blue-600 shadow-2xs font-bold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <MessageSquare className="h-4 w-4" />
            <span>Message / URL</span>
          </button>
        </div>

        {/* TAB 1: DOCUMENT */}
        {activeTab === 'document' ? (
          <div className="space-y-4">
            {/* Input Method Selector: Upload File vs Use Camera */}
            <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
              <button
                type="button"
                onClick={() => setDocumentInputMode('upload')}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-1.5 ${
                  documentInputMode === 'upload'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                <UploadCloud className="h-4 w-4" />
                <span>Upload File</span>
              </button>

              <button
                type="button"
                onClick={() => setDocumentInputMode('camera')}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-1.5 ${
                  documentInputMode === 'camera'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                <Camera className="h-4 w-4" />
                <span>Use Camera</span>
              </button>
            </div>

            {documentInputMode === 'camera' ? (
              <CameraCapture
                onPhotoCaptured={handlePhotoCaptured}
                onCancel={() => setDocumentInputMode('upload')}
                isAnalyzing={isAnalyzing}
              />
            ) : (
              <div>
                {!selectedFile ? (
                  <div
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                    className={`border-2 border-dashed rounded-xl p-8 text-center transition cursor-pointer flex flex-col items-center justify-center min-h-[200px] ${
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
                    <div className="h-11 w-11 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
                      <UploadCloud className="h-5 w-5" />
                    </div>
                    <p className="text-xs font-semibold text-slate-800 mb-1">
                      Drag and drop document here, or <span className="text-blue-600 underline">browse</span>
                    </p>
                    <p className="text-[11px] text-slate-400 m-0">
                      Supported formats: PDF, DOCX, JPG, PNG, WEBP, TIFF, BMP (Max 30MB)
                    </p>
                  </div>
                ) : (
                  <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 flex items-center justify-between">
                    <div className="flex items-center gap-3 overflow-hidden">
                      <div className="h-9 w-9 rounded-lg bg-blue-600 text-white flex items-center justify-center shrink-0">
                        <FileText className="h-4 w-4" />
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
                        className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 transition cursor-pointer"
                        title="Remove file"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          /* TAB 2: MESSAGE / URL */
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-800 mb-1.5">
                Paste suspicious message
              </label>
              <textarea
                value={pastedText}
                onChange={(e) => setPastedText(e.target.value)}
                placeholder="Example: 'Invest ₹50,000 to receive ₹80,000 in 30 days! Guaranteed returns. Pay immediately to UPI...'"
                rows={4}
                className="w-full text-xs p-3 rounded-lg border border-slate-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-hidden font-sans bg-slate-50/50"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-800 mb-1.5 flex items-center gap-1">
                <Link className="h-3.5 w-3.5 text-slate-500" />
                <span>Paste URL</span>
              </label>
              <input
                type="url"
                value={pastedUrl}
                onChange={(e) => setPastedUrl(e.target.value)}
                placeholder="https://example-bonus-portal.com/activate"
                className="w-full text-xs px-3 py-2.5 rounded-lg border border-slate-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 font-mono outline-hidden bg-slate-50/50"
              />
            </div>
          </div>
        )}

        {/* Error message */}
        {errorMessage && (
          <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-start gap-2">
            <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-rose-600" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Progress indicator while analyzing */}
        {isAnalyzing && (
          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 space-y-2.5">
            <div className="flex items-center justify-between text-xs font-medium text-slate-700">
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />
                <span>Running Proofly Analysis...</span>
              </div>
              <span className="font-mono text-[11px] text-blue-600">
                Step {analysisStep + 1}/{pipelineSteps.length || 6}
              </span>
            </div>
            <p className="text-[11px] text-slate-500 font-mono m-0 truncate">
              {pipelineSteps[analysisStep] || 'Evaluating evidence indicators...'}
            </p>
            <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
              <div
                className="bg-blue-600 h-1.5 transition-all duration-300 rounded-full"
                style={{ width: `${((analysisStep + 1) / (pipelineSteps.length || 6)) * 100}%` }}
              />
            </div>
          </div>
        )}

        {/* PRIMARY ACTION BUTTON (When not in live camera capture mode) */}
        {!(activeTab === 'document' && documentInputMode === 'camera') && (
          <button
            onClick={handleStartAnalysis}
            disabled={!isReady || isAnalyzing}
            className={`w-full py-3 px-4 rounded-lg text-xs font-semibold transition flex items-center justify-center gap-2 cursor-pointer shadow-xs ${
              !isReady || isAnalyzing
                ? 'bg-slate-100 text-slate-400 border border-slate-200 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white'
            }`}
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Analyzing Evidence...</span>
              </>
            ) : (
              <>
                <span>Analyze</span>
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </button>
        )}
      </div>

      {/* SAMPLE DATA ACCESS: SMALL SECONDARY LINK BELOW INPUT CONTROLS */}
      <div className="text-center space-y-3 pt-1">
        <button
          type="button"
          onClick={() => setShowSamples(!showSamples)}
          className="text-xs text-slate-500 hover:text-slate-800 transition cursor-pointer inline-flex items-center gap-1.5"
        >
          <span>Need an example?</span>
          <span className="text-blue-600 underline font-medium">Try sample data</span>
          {showSamples ? <ChevronUp className="h-3.5 w-3.5 text-slate-400" /> : <ChevronDown className="h-3.5 w-3.5 text-slate-400" />}
        </button>

        {/* REVEALED SAMPLE DATA SECTION */}
        {showSamples && (
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-left space-y-3 transition">
            <div className="flex items-center justify-between text-[11px] text-slate-500 border-b border-slate-200 pb-2">
              <span className="font-semibold text-slate-700">Sample data for demonstration</span>
              <span>Click any case to test analysis</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {sampleOptions.map((s) => (
                <button
                  key={s.id}
                  onClick={() => onRunSample(s.id)}
                  disabled={isAnalyzing}
                  className="p-3 rounded-lg bg-white hover:bg-blue-50/40 border border-slate-200 hover:border-blue-300 text-left transition cursor-pointer flex flex-col justify-between gap-1.5 shadow-2xs disabled:opacity-50"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-bold text-slate-800">{s.title}</span>
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200 shrink-0 font-medium">
                      {s.tag}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 m-0 leading-normal">
                    {s.desc}
                  </p>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
