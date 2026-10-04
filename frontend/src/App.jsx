import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  FileSearch,
  Sparkles,
  Globe,
  Download,
  RotateCcw,
  ArrowLeft
} from 'lucide-react';
import HomeScreen from './components/HomeScreen';
import AnalyzeScreen from './components/AnalyzeScreen';
import ResultScreen from './components/ResultScreen';

const API_BASE = import.meta.env.VITE_API_URL || '';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('home'); // 'home' | 'analyze' | 'results'
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStep, setAnalysisStep] = useState(0);
  const [errorMessage, setErrorMessage] = useState(null);
  const [language, setLanguage] = useState('en'); // 'en' | 'hi'

  const pipelineSteps = [
    'Ingesting input and verifying format signature...',
    'Scanning for image splicing & AI inpainting anomalies...',
    'Detecting prohibited claims & guaranteed yield language...',
    'Cross-checking registration against SEBI/NSDL directory mirror...',
    'Passive URL lookalike and typosquatting inspection...',
    'Synthesizing multimodal evidence into explainable risk assessment...'
  ];

  const toggleLanguage = () => {
    setLanguage((prev) => (prev === 'en' ? 'hi' : 'en'));
  };

  // Upload and analyze physical document
  const handleAnalyzeFile = async (file) => {
    setIsAnalyzing(true);
    setAnalysisResult(null);
    setAnalysisStep(0);
    setErrorMessage(null);

    const stepInterval = setInterval(() => {
      setAnalysisStep((prev) => (prev < 5 ? prev + 1 : prev));
    }, 500);

    const formData = new FormData();
    formData.append('file', file);

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
      setCurrentScreen('results');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      clearInterval(stepInterval);
      setErrorMessage(err.message || 'Error occurred while analyzing document.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Analyze pasted text or URL
  const handleAnalyzeText = async ({ text, url }) => {
    setIsAnalyzing(true);
    setAnalysisResult(null);
    setAnalysisStep(0);
    setErrorMessage(null);

    const stepInterval = setInterval(() => {
      setAnalysisStep((prev) => (prev < 5 ? prev + 1 : prev));
    }, 400);

    try {
      const response = await fetch(`${API_BASE}/api/analyze-text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          url,
          language
        }),
      });

      clearInterval(stepInterval);

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: 'Text analysis failed' }));
        throw new Error(errData.detail || `Server returned code ${response.status}`);
      }

      const data = await response.json();
      data.extracted_text = text;
      data.document_type = 'Message & Link';
      setAnalysisResult(data);
      setCurrentScreen('results');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      clearInterval(stepInterval);
      setErrorMessage(err.message || 'Failed to analyze text message.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Run official Codex demo fixtures
  const handleRunCodexDemo = async (sampleId) => {
    setIsAnalyzing(true);
    setAnalysisResult(null);
    setAnalysisStep(0);
    setErrorMessage(null);
    setCurrentScreen('analyze');

    const stepInterval = setInterval(() => {
      setAnalysisStep((prev) => (prev < 5 ? prev + 1 : prev));
    }, 400);

    try {
      const response = await fetch(`${API_BASE}/api/codex-demos/analyze/${encodeURIComponent(sampleId)}`, {
        method: 'POST',
      });

      clearInterval(stepInterval);

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: 'Demo analysis failed' }));
        throw new Error(errData.detail || `Server returned code ${response.status}`);
      }

      const data = await response.json();
      setAnalysisResult(data);
      setCurrentScreen('results');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      clearInterval(stepInterval);
      setErrorMessage(err.message || 'Failed to execute Codex demo scenario.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDownloadReport = () => {
    if (!analysisResult) return;
    const blob = new Blob([JSON.stringify(analysisResult, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `proofly_evidence_dossier_${analysisResult.filename || 'report'}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans selection:bg-blue-100 selection:text-blue-900 text-slate-800">
      {/* TOP HEADER */}
      <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-sm border-b border-slate-200 px-4 sm:px-8 py-3.5 shadow-2xs">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          {/* Logo & Brand */}
          <div
            onClick={() => setCurrentScreen('home')}
            className="flex items-center gap-2.5 cursor-pointer select-none"
          >
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-violet-600 flex items-center justify-center text-white shadow-xs">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-black text-base tracking-tight text-slate-900">Proofly Investor</span>
                <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-blue-50 text-blue-700 border border-blue-100 font-mono">
                  SANGYAN
                </span>
              </div>
              <p className="text-[11px] text-slate-500 font-medium m-0 hidden sm:block">
                Verify before you trust.
              </p>
            </div>
          </div>

          {/* Simple Navigation Pills */}
          <nav className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200/80 text-xs font-semibold">
            <button
              onClick={() => setCurrentScreen('home')}
              className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                currentScreen === 'home'
                  ? 'bg-white text-blue-700 shadow-2xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Home
            </button>
            <button
              onClick={() => setCurrentScreen('analyze')}
              className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                currentScreen === 'analyze'
                  ? 'bg-white text-blue-700 shadow-2xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Analyze
            </button>
            {analysisResult && (
              <button
                onClick={() => setCurrentScreen('results')}
                className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                  currentScreen === 'results'
                    ? 'bg-white text-blue-700 shadow-2xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Results
              </button>
            )}
          </nav>

          {/* Right Controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleRunCodexDemo('guaranteed_return')}
              className="hidden md:flex items-center gap-1 px-3 py-1.5 rounded-xl bg-blue-50 hover:bg-blue-100 border border-blue-200 text-blue-700 text-xs font-bold transition cursor-pointer"
            >
              <Sparkles className="h-3.5 w-3.5 text-blue-600" />
              <span>Try Demo</span>
            </button>

            <button
              onClick={toggleLanguage}
              className={`px-2.5 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer border flex items-center gap-1 ${
                language === 'hi'
                  ? 'bg-amber-50 text-amber-900 border-amber-300'
                  : 'bg-slate-100 text-slate-700 border-slate-200 hover:bg-slate-200'
              }`}
            >
              <Globe className="h-3.5 w-3.5 text-blue-600" />
              <span>{language === 'hi' ? 'हिंदी' : 'EN'}</span>
            </button>
          </div>
        </div>
      </header>

      {/* MAIN SCREEN BODY */}
      <main className="flex-1 px-4 sm:px-8 py-6 max-w-6xl w-full mx-auto">
        {currentScreen === 'home' && (
          <HomeScreen
            onNavigateToAnalyze={() => setCurrentScreen('analyze')}
            onRunDemoScam={handleRunCodexDemo}
            onRunDemoForgery={handleRunCodexDemo}
            onRunDemoControl={handleRunCodexDemo}
            isAnalyzing={isAnalyzing}
            language={language}
          />
        )}

        {currentScreen === 'analyze' && (
          <AnalyzeScreen
            onAnalyzeFile={handleAnalyzeFile}
            onAnalyzeText={handleAnalyzeText}
            onRunDemo={handleRunCodexDemo}
            isAnalyzing={isAnalyzing}
            analysisStep={analysisStep}
            pipelineSteps={pipelineSteps}
            errorMessage={errorMessage}
            language={language}
          />
        )}

        {currentScreen === 'results' && analysisResult && (
          <ResultScreen
            analysisResult={analysisResult}
            onBackToAnalyze={() => setCurrentScreen('analyze')}
            onDownloadReport={handleDownloadReport}
            language={language}
            onToggleLanguage={toggleLanguage}
          />
        )}
      </main>

      {/* FOOTER */}
      <footer className="border-t border-slate-200 bg-white px-6 py-5 text-xs text-slate-500 mt-auto">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="font-black text-slate-900">Proofly Investor</span>
            <span>•</span>
            <span className="italic text-slate-600">Verify before you trust.</span>
            <span>•</span>
            <span>SANGYAN Hackathon (IIT BHU × SEBI × NSDL)</span>
          </div>
          <div className="text-slate-400 font-mono text-[11px]">
            Track A: Digital Fraud Resilience • Track E: Content Literacy
          </div>
        </div>
      </footer>
    </div>
  );
}
