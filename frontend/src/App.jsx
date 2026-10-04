import React, { useState } from 'react';
import {
  ShieldCheck,
  Globe
} from 'lucide-react';
import HomeScreen from './components/HomeScreen';
import AnalyzeScreen from './components/AnalyzeScreen';
import ResultScreen from './components/ResultScreen';

const API_BASE = import.meta.env.VITE_API_URL || '';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('home'); // 'home' | 'analyze' | 'results'
  const [analyzeInitialMode, setAnalyzeInitialMode] = useState('upload'); // 'upload' | 'camera'
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStep, setAnalysisStep] = useState(0);
  const [errorMessage, setErrorMessage] = useState(null);
  const [language, setLanguage] = useState('en'); // 'en' | 'hi'

  const pipelineSteps = [
    'Ingesting input and verifying format signature...',
    'Scanning document structure & image layers...',
    'Detecting suspicious patterns and high-risk language...',
    'Checking claimed references against directory data...',
    'Analyzing link structures and domain indicators...',
    'Synthesizing findings into explainable risk assessment...'
  ];

  const toggleLanguage = () => {
    setLanguage((prev) => (prev === 'en' ? 'hi' : 'en'));
  };

  // Upload and analyze document (from file upload or camera capture)
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

  // Run sample fixtures (accessible from Analyze screen)
  const handleRunSample = async (sampleId) => {
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
        const errData = await response.json().catch(() => ({ detail: 'Sample analysis failed' }));
        throw new Error(errData.detail || `Server returned code ${response.status}`);
      }

      const data = await response.json();
      setAnalysisResult(data);
      setCurrentScreen('results');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      clearInterval(stepInterval);
      setErrorMessage(err.message || 'Failed to execute sample analysis.');
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
    a.download = `proofly_dossier_${analysisResult.filename || 'analysis'}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleNavigate = (target, mode = 'upload') => {
    if (target === 'analyze' || target === 'camera') {
      setAnalyzeInitialMode(target === 'camera' || mode === 'camera' ? 'camera' : 'upload');
      setCurrentScreen('analyze');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else if (target === 'home') {
      setCurrentScreen('home');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else if (target === 'how-it-works' || target === 'safety' || target === 'about') {
      if (currentScreen !== 'home') {
        setCurrentScreen('home');
        setTimeout(() => {
          const el = document.getElementById(target);
          if (el) el.scrollIntoView({ behavior: 'smooth' });
        }, 80);
      } else {
        const el = document.getElementById(target);
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }
    } else if (target === 'results') {
      setCurrentScreen('results');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans selection:bg-blue-100 selection:text-blue-900 text-slate-800">
      {/* TOP HEADER */}
      <header className="sticky top-0 z-30 bg-white border-b border-slate-200 px-4 sm:px-8 py-3.5 shadow-xs">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          {/* Logo & Brand */}
          <div
            onClick={() => handleNavigate('home')}
            className="flex items-center gap-2.5 cursor-pointer select-none"
          >
            <div className="h-9 w-9 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-xs">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-base tracking-tight text-slate-900">Proofly</span>
              </div>
              <p className="text-[11px] text-slate-500 font-normal m-0 hidden sm:block">
                Verify before you trust.
              </p>
            </div>
          </div>

          {/* Navigation Items */}
          <nav className="flex items-center gap-1 sm:gap-2 text-xs font-medium">
            <button
              onClick={() => handleNavigate('home')}
              className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                currentScreen === 'home'
                  ? 'bg-slate-100 text-blue-600 font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Proofly
            </button>
            <button
              onClick={() => handleNavigate('analyze')}
              className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                currentScreen === 'analyze'
                  ? 'bg-slate-100 text-blue-600 font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Analyze
            </button>
            <button
              onClick={() => handleNavigate('how-it-works')}
              className="px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition cursor-pointer hidden sm:inline-block"
            >
              How It Works
            </button>
            <button
              onClick={() => handleNavigate('safety')}
              className="px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition cursor-pointer hidden sm:inline-block"
            >
              Safety
            </button>
            <button
              onClick={() => handleNavigate('about')}
              className="px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition cursor-pointer hidden md:inline-block"
            >
              About
            </button>
            {analysisResult && (
              <button
                onClick={() => handleNavigate('results')}
                className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                  currentScreen === 'results'
                    ? 'bg-slate-100 text-blue-600 font-semibold'
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
              onClick={toggleLanguage}
              className={`px-2.5 py-1.5 rounded-lg text-xs font-medium transition cursor-pointer border flex items-center gap-1.5 ${
                language === 'hi'
                  ? 'bg-blue-50 text-blue-800 border-blue-200'
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
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
            onNavigateToAnalyze={() => handleNavigate('analyze', 'upload')}
            onNavigateToCamera={() => handleNavigate('camera', 'camera')}
            onNavigateToSection={handleNavigate}
            language={language}
          />
        )}

        {currentScreen === 'analyze' && (
          <AnalyzeScreen
            initialMode={analyzeInitialMode}
            onAnalyzeFile={handleAnalyzeFile}
            onAnalyzeText={handleAnalyzeText}
            onRunSample={handleRunSample}
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
      <footer className="border-t border-slate-200 bg-white px-6 py-8 text-xs text-slate-500 mt-auto">
        <div className="max-w-6xl mx-auto space-y-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-900 text-sm">Proofly</span>
              <span className="text-slate-300">•</span>
              <span className="text-slate-600">Verify before you trust.</span>
            </div>
            <div className="flex items-center gap-4 text-xs font-medium">
              <button
                onClick={() => handleNavigate('safety')}
                className="text-slate-600 hover:text-blue-600 transition cursor-pointer"
              >
                Privacy
              </button>
              <button
                onClick={() => handleNavigate('safety')}
                className="text-slate-600 hover:text-blue-600 transition cursor-pointer"
              >
                Safety
              </button>
              <a
                href="https://github.com/17rajsal/document-forgery-ai"
                target="_blank"
                rel="noreferrer"
                className="text-slate-600 hover:text-blue-600 transition"
              >
                GitHub
              </a>
            </div>
          </div>
          <div className="border-t border-slate-100 pt-3 text-[11px] text-slate-500 text-center sm:text-left">
            <p className="m-0">
              Proofly provides risk indicators and educational guidance and does not guarantee document authenticity.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
