import React, { useState, useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import FeatureCards from './components/FeatureCards';
import UploadPanel from './components/UploadPanel';
import DocumentPreview from './components/DocumentPreview';
import AnalysisResult from './components/AnalysisResult';
import ResultTabs from './components/ResultTabs';
import SampleDocuments from './components/SampleDocuments';
import Modals from './components/Modals';

const API_BASE = import.meta.env.VITE_API_URL || '';

export default function App() {
  const [backendStatus, setBackendStatus] = useState(null);
  const [samples, setSamples] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStep, setAnalysisStep] = useState(0);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [history, setHistory] = useState([]);

  // UI Navigation & Modals
  const [activeNav, setActiveNav] = useState('new-analysis');
  const [activeModal, setActiveModal] = useState(null); // 'formats', 'how-it-works', 'history', 'settings'
  const [mobileOpen, setMobileOpen] = useState(false);
  const [showOcrBoxes, setShowOcrBoxes] = useState(false);

  // Analysis steps simulation for responsive UX feedback
  const pipelineSteps = [
    'Ingesting & rasterizing document container...',
    'Executing tri-pass OCR & word boundary detection...',
    'Performing spatial Error Level Analysis (ELA)...',
    'Analyzing noise variance & copy-move feature clusters...',
    'Checking mathematical checksums & synthesizing 4-tier verdict...'
  ];

  // Fetch health and samples on mount
  useEffect(() => {
    fetch(`${API_BASE}/api/health`)
      .then((res) => res.json())
      .then((data) => setBackendStatus(data))
      .catch(() => setBackendStatus({ status: 'OFFLINE' }));

    fetch(`${API_BASE}/api/samples`)
      .then((res) => res.json())
      .then((data) => setSamples(data.samples || []))
      .catch(() => setSamples([]));
  }, []);

  // Handle sidebar navigation clicks
  const handleNavClick = (navId) => {
    setActiveNav(navId);
    if (navId === 'formats') setActiveModal('formats');
    else if (navId === 'how-it-works') setActiveModal('how-it-works');
    else if (navId === 'history') setActiveModal('history');
    else if (navId === 'settings') setActiveModal('settings');
    else if (navId === 'samples') {
      const el = document.getElementById('sample-documents-section');
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleFileSelected = (file) => {
    const validExtensions = ['.jpg', '.jpeg', '.png', '.webp', '.pdf', '.tif', '.tiff', '.bmp', '.docx'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!validExtensions.includes(ext)) {
      setErrorMessage(`Unsupported file format (${ext}). Supported formats: JPG, PNG, WEBP, PDF, TIFF, BMP, DOCX.`);
      return;
    }
    setErrorMessage(null);
    setSelectedFile(file);
  };

  const handleRemoveSelectedFile = () => {
    setSelectedFile(null);
    setErrorMessage(null);
  };

  const uploadAndAnalyze = async () => {
    if (!selectedFile) return;

    setIsAnalyzing(true);
    setAnalysisResult(null);
    setAnalysisStep(0);
    setErrorMessage(null);

    const stepInterval = setInterval(() => {
      setAnalysisStep((prev) => (prev < 4 ? prev + 1 : prev));
    }, 600);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      });

      clearInterval(stepInterval);

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: 'Analysis failed' }));
        throw new Error(errData.detail || `Server returned code ${response.status}`);
      }

      const data = await response.json();
      setAnalysisResult(data);

      // Add to session history
      setHistory((prev) => [data, ...prev.filter((h) => h.filename !== data.filename)]);
    } catch (err) {
      clearInterval(stepInterval);
      setErrorMessage(err.message || 'Error occurred while communicating with forensic backend.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const analyzeSampleDoc = async (sampleName) => {
    setIsAnalyzing(true);
    setAnalysisResult(null);
    setSelectedFile(null);
    setErrorMessage(null);
    setAnalysisStep(0);

    const stepInterval = setInterval(() => {
      setAnalysisStep((prev) => (prev < 4 ? prev + 1 : prev));
    }, 550);

    try {
      const response = await fetch(`${API_BASE}/api/analyze-sample/${encodeURIComponent(sampleName)}`, {
        method: 'POST',
      });

      clearInterval(stepInterval);

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: 'Sample analysis failed' }));
        throw new Error(errData.detail || `Server returned code ${response.status}`);
      }

      const data = await response.json();
      setAnalysisResult(data);

      // Add to session history
      setHistory((prev) => [data, ...prev.filter((h) => h.filename !== data.filename)]);

      // Scroll smoothly to results
      window.scrollTo({ top: 120, behavior: 'smooth' });
    } catch (err) {
      clearInterval(stepInterval);
      setErrorMessage(err.message || 'Failed to analyze sample document.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const resetAnalysis = () => {
    setAnalysisResult(null);
    setSelectedFile(null);
    setErrorMessage(null);
    setActiveNav('new-analysis');
  };

  const downloadJsonReport = () => {
    if (!analysisResult) return;
    const blob = new Blob([JSON.stringify(analysisResult, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `docshield_audit_${analysisResult.filename || 'report'}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans selection:bg-blue-100 selection:text-blue-900">
      <div className="flex flex-1">
        {/* LEFT SIDEBAR */}
        <Sidebar
          activeNav={activeNav}
          setActiveNav={handleNavClick}
          historyCount={history.length}
          backendStatus={backendStatus}
          onNewAnalysis={resetAnalysis}
          mobileOpen={mobileOpen}
          setMobileOpen={setMobileOpen}
        />

        {/* MAIN BODY AREA */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* TOP HEADER */}
          <Header
            onNewAnalysis={resetAnalysis}
            onOpenHowItWorks={() => setActiveModal('how-it-works')}
            onOpenFormats={() => setActiveModal('formats')}
            setMobileOpen={setMobileOpen}
            backendStatus={backendStatus}
          />

          {/* DASHBOARD CONTENT */}
          <main className="flex-1 p-4 sm:p-8 max-w-7xl w-full mx-auto space-y-6">
            {/* TOP FEATURE CARDS */}
            <FeatureCards
              onOpenFormats={() => setActiveModal('formats')}
              onOpenHowItWorks={() => setActiveModal('how-it-works')}
            />

            {/* MAIN 3-COLUMN WORKSPACE */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-stretch">
              {/* 1. UPLOAD PANEL (LEFT) */}
              <div className="h-full">
                <UploadPanel
                  selectedFile={selectedFile}
                  onFileSelected={handleFileSelected}
                  onRemoveSelectedFile={handleRemoveSelectedFile}
                  onAnalyze={uploadAndAnalyze}
                  isAnalyzing={isAnalyzing}
                  analysisStep={analysisStep}
                  pipelineSteps={pipelineSteps}
                  errorMessage={errorMessage}
                  isDragging={isDragging}
                  setIsDragging={setIsDragging}
                />
              </div>

              {/* 2. DOCUMENT PREVIEW (CENTER) */}
              <div className="h-full">
                <DocumentPreview
                  previewImage={analysisResult?.preview_image}
                  filename={analysisResult?.filename || selectedFile?.name}
                  documentType={analysisResult?.document_type}
                  imageProps={analysisResult?.forgery_analysis?.image_analysis}
                  ocrWords={analysisResult?.ocr_words}
                  totalPages={analysisResult?.total_pages || 1}
                  showOcrBoxes={showOcrBoxes}
                  setShowOcrBoxes={setShowOcrBoxes}
                />
              </div>

              {/* 3. ANALYSIS VERDICT RESULT (RIGHT) */}
              <div className="h-full">
                <AnalysisResult
                  analysisResult={analysisResult}
                  onReset={resetAnalysis}
                  onDownloadReport={downloadJsonReport}
                />
              </div>
            </div>

            {/* EXPANDED DETAILED RESULT TABS (WHEN AVAILABLE) */}
            {analysisResult && (
              <ResultTabs
                analysisResult={analysisResult}
                onDownloadReport={downloadJsonReport}
              />
            )}

            {/* SAMPLE DOCUMENTS SECTION */}
            <div id="sample-documents-section">
              <SampleDocuments
                samples={samples}
                onSelectSample={analyzeSampleDoc}
                isAnalyzing={isAnalyzing}
              />
            </div>
          </main>

          {/* FOOTER */}
          <footer className="border-t border-slate-200/80 bg-white px-6 py-6 text-xs text-slate-500 mt-auto">
            <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-slate-700">DocShield AI</span>
                <span>•</span>
                <span>AI-Powered Document Authenticity & Forgery Verification System</span>
              </div>
              <div className="text-slate-400">
                PyTesseract • Spatial ELA • Laplacian Noise Variance • FastAPI
              </div>
            </div>
          </footer>
        </div>
      </div>

      {/* POPUP MODALS */}
      <Modals
        activeModal={activeModal}
        onClose={() => setActiveModal(null)}
        history={history}
        onSelectHistoryItem={(item) => setAnalysisResult(item)}
        backendStatus={backendStatus}
      />
    </div>
  );
}
