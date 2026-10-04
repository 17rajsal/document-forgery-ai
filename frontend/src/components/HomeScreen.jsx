import React from 'react';
import {
  FileText,
  Image,
  MessageSquare,
  QrCode,
  ArrowRight,
  ShieldCheck,
  Search,
  Eye,
  CheckCircle,
  Lock,
  Globe,
  FileCheck
} from 'lucide-react';

export default function HomeScreen({
  onNavigateToAnalyze,
  onNavigateToSection,
  language = 'en'
}) {
  return (
    <div className="space-y-16 max-w-4xl mx-auto py-6">
      {/* HOMEPAGE HERO */}
      <section className="text-center space-y-4 pt-6 pb-2">
        <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight leading-tight m-0">
          Proofly
        </h1>

        <p className="text-xl sm:text-2xl font-semibold text-blue-600 m-0">
          Verify before you trust.
        </p>

        <p className="text-sm sm:text-base text-slate-600 max-w-2xl mx-auto leading-relaxed m-0">
          Analyze suspicious documents, screenshots, messages, links and QR codes for potential fraud and manipulation indicators before taking action.
        </p>

        {/* PRIMARY CALL TO ACTION BUTTONS */}
        <div className="pt-4 flex flex-wrap items-center justify-center gap-3">
          <button
            onClick={onNavigateToAnalyze}
            className="flex items-center gap-2 px-6 py-3 rounded-lg bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-semibold text-sm transition cursor-pointer shadow-xs"
          >
            <span>Analyze Now</span>
            <ArrowRight className="h-4 w-4" />
          </button>

          <button
            onClick={() => onNavigateToSection && onNavigateToSection('how-it-works')}
            className="flex items-center gap-2 px-5 py-3 rounded-lg bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 font-semibold text-sm transition cursor-pointer"
          >
            <span>How It Works</span>
          </button>
        </div>
      </section>

      {/* SECTION 1 — What You Can Check */}
      <section className="space-y-6">
        <div className="text-center space-y-1">
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 m-0">
            What You Can Check
          </h2>
          <p className="text-xs text-slate-500 m-0">
            Comprehensive multi-format inspection across common vectors.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-2.5">
            <div className="h-9 w-9 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center">
              <FileText className="h-4 w-4" />
            </div>
            <h3 className="text-sm font-bold text-slate-900 m-0">Documents</h3>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              PDFs, notices, agreements, certificates, statements, and forms checked for tampering.
            </p>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-2.5">
            <div className="h-9 w-9 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center">
              <Image className="h-4 w-4" />
            </div>
            <h3 className="text-sm font-bold text-slate-900 m-0">Screenshots</h3>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Chat logs, transaction receipts, app captures, and camera photos of printed records.
            </p>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-2.5">
            <div className="h-9 w-9 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center">
              <MessageSquare className="h-4 w-4" />
            </div>
            <h3 className="text-sm font-bold text-slate-900 m-0">Messages</h3>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              SMS, WhatsApp, and Telegram text checked for urgency pressure and scam language.
            </p>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-2.5">
            <div className="h-9 w-9 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center">
              <QrCode className="h-4 w-4" />
            </div>
            <h3 className="text-sm font-bold text-slate-900 m-0">URLs & QR Codes</h3>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Lookalike domains, deceptive links, and QR codes decoded for security anomalies.
            </p>
          </div>
        </div>
      </section>

      {/* SECTION 2 — How It Works */}
      <section id="how-it-works" className="bg-white rounded-xl border border-slate-200 p-6 sm:p-8 space-y-6">
        <div className="text-center space-y-1">
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 m-0">
            How It Works
          </h2>
          <p className="text-xs text-slate-500 m-0">
            A transparent four-step forensic verification process.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 pt-2">
          <div className="space-y-2">
            <div className="h-8 w-8 rounded-lg bg-blue-50 text-blue-600 font-bold flex items-center justify-center text-sm font-mono">
              1
            </div>
            <h4 className="text-sm font-bold text-slate-900 m-0">
              Upload or capture
            </h4>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Upload a document file, take a photo with your camera, or paste suspicious text and links.
            </p>
          </div>

          <div className="space-y-2">
            <div className="h-8 w-8 rounded-lg bg-blue-50 text-blue-600 font-bold flex items-center justify-center text-sm font-mono">
              2
            </div>
            <h4 className="text-sm font-bold text-slate-900 m-0">
              Analyze risk indicators
            </h4>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Automated forensic analysis checks pixel consistency, OCR text, and domain risk signals.
            </p>
          </div>

          <div className="space-y-2">
            <div className="h-8 w-8 rounded-lg bg-blue-50 text-blue-600 font-bold flex items-center justify-center text-sm font-mono">
              3
            </div>
            <h4 className="text-sm font-bold text-slate-900 m-0">
              Review evidence
            </h4>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Examine visual evidence maps, suspicious wording highlights, and detailed findings.
            </p>
          </div>

          <div className="space-y-2">
            <div className="h-8 w-8 rounded-lg bg-blue-50 text-blue-600 font-bold flex items-center justify-center text-sm font-mono">
              4
            </div>
            <h4 className="text-sm font-bold text-slate-900 m-0">
              Verify independently
            </h4>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Follow official verification steps to confirm authenticity through authoritative channels.
            </p>
          </div>
        </div>
      </section>

      {/* SECTION 3 — Why Proofly */}
      <section className="space-y-6">
        <div className="text-center space-y-1">
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 m-0">
            Why Proofly
          </h2>
          <p className="text-xs text-slate-500 m-0">
            Designed for clarity, privacy, and actionable verification.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-2">
            <div className="flex items-center gap-2">
              <Eye className="h-4 w-4 text-blue-600" />
              <h3 className="text-sm font-bold text-slate-900 m-0">Explainable findings</h3>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Clear, transparent explanations showing exact reasons behind flagged indicators, never an unexplained score.
            </p>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-2">
            <div className="flex items-center gap-2">
              <Lock className="h-4 w-4 text-blue-600" />
              <h3 className="text-sm font-bold text-slate-900 m-0">Privacy-first processing</h3>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Strict client-side validation, isolated processing environments, and automatic temporary file cleanup.
            </p>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-2">
            <div className="flex items-center gap-2">
              <Globe className="h-4 w-4 text-blue-600" />
              <h3 className="text-sm font-bold text-slate-900 m-0">English & Hindi guidance</h3>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Accessible plain-language explanations and optional audio readout in both English and Hindi.
            </p>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-2">
            <div className="flex items-center gap-2">
              <FileCheck className="h-4 w-4 text-blue-600" />
              <h3 className="text-sm font-bold text-slate-900 m-0">Evidence-focused analysis</h3>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Empowers users with verifiable facts, visual evidence bounding boxes, and independent corroboration paths.
            </p>
          </div>
        </div>
      </section>

      {/* SECTION 4 — Safety */}
      <section id="safety" className="bg-slate-50 rounded-xl border border-slate-200 p-6 space-y-2">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 m-0">
          Safety & Verification Policy
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed m-0">
          Proofly provides risk indicators and educational safety guidance. It does not guarantee authenticity or replace official verification.
        </p>
        <p className="text-[11px] text-slate-500 leading-relaxed m-0 pt-1 border-t border-slate-200/60">
          All findings are probabilistic and intended to highlight potential risks or anomalies requiring independent verification through official channels. Proofly does not provide financial advice, legal guarantees, or conclusive fraud determinations.
        </p>
      </section>

      {/* SECTION 5 — About */}
      <section id="about" className="bg-white rounded-xl border border-slate-200 p-6 sm:p-8 space-y-3">
        <h3 className="text-lg font-bold text-slate-900 m-0">About Proofly</h3>
        <p className="text-xs text-slate-600 leading-relaxed m-0">
          Proofly helps users inspect suspicious digital documents and messages using document forensics, OCR, scam-pattern analysis and explainable risk indicators.
        </p>
      </section>
    </div>
  );
}
