import React from 'react';
import {
  FileText,
  Sparkles,
  ArrowRight,
  ShieldAlert,
  CreditCard,
  GraduationCap,
  Landmark,
  FileCheck,
  Receipt,
  UserCheck,
  AlertTriangle,
  Cpu
} from 'lucide-react';

export default function SampleDocuments({
  samples = [],
  onSelectSample,
  onSelectDemoScenario,
  isAnalyzing,
  language = 'en'
}) {
  const demoScenarios = [
    {
      id: 'official_authority_50k_80k_certificate',
      title: "Sample: Guaranteed Return Allotment Scheme (₹50k -> ₹80k)",
      title_hi: "Sample Case: Guaranteed Allotment Scheme (₹50k -> ₹80k)",
      persona: "Promised ₹80,000 return in 30 days for ₹50,000; fake regulatory reg INZ999888777, personal UPI QR vikram.personal88@okaxis",
      persona_hi: "30 din mein ₹50,000 se ₹80,000 ka wada, jhoothi regulatory reg aur personal UPI QR",
      tag: "Sample Analysis",
      tag_color: "bg-rose-100 text-rose-800 border-rose-200",
      signals: ["₹50k -> ₹80k (60% 30-day)", "Fake Reg INZ999888777", "Personal UPI QR", "Digital Splicing", "DEMO SAMPLE Watermark"],
      icon: ShieldAlert,
      badge: "High Risk (95/100)"
    },
    {
      id: 'kavita_whatsapp_scam',
      title: "Kavita's Case: WhatsApp Pre-IPO Scam PDF",
      title_hi: "Kavita Ka Case: WhatsApp Pre-IPO Scam PDF",
      persona: "Tier-2 retail investor receives WhatsApp pre-IPO letter with personal UPI QR",
      persona_hi: "WhatsApp par mila jhootha pre-IPO allotment letter jisme personal UPI QR laga hai",
      tag: "WhatsApp Scam Case",
      tag_color: "bg-rose-100 text-rose-800 border-rose-200",
      signals: ["Guaranteed 30% Return", "Fake Regulatory Authority Approved", "Personal UPI QR", "Urgency: 5 Slots Left"],
      icon: ShieldAlert,
      badge: "High Concern"
    },
    {
      id: 'traditional_altered_bank_slip',
      title: "Traditional Tampering: Overwritten Amount Deposit Slip",
      title_hi: "Purana Splicing: Badli Hui Rakam Ka Bank Slip",
      persona: "Cash deposit slip where numeric amount was overwritten (₹90,000 vs ten thousand words)",
      persona_hi: "Cash deposit slip jahan ank badla gaya hai (₹90,000 vs ten thousand words)",
      tag: "Semantic Amount Tampering",
      tag_color: "bg-amber-100 text-amber-800 border-amber-200",
      signals: ["₹90,000 vs 10,000 words", "Pasted First Digit", "Boundary Sharpness Disparity"],
      icon: Landmark,
      badge: "High Concern"
    },
    {
      id: 'ai_erased_dividend_receipt',
      title: "AI Erase & Inpainting: Generative Fill Dividend Certificate",
      title_hi: "AI Inpainting: Mita Kar Likha Hua Dividend Certificate",
      persona: "Dividend credit warrant with AI-erased account digits and generative background smoothing",
      persona_hi: "AI erase se saaf kiya gaya bank account aur dubara likha gaya text",
      tag: "Generative AI Erase",
      tag_color: "bg-teal-100 text-teal-800 border-teal-200",
      signals: ["High-Frequency Noise Loss", "Unnatural Paper Smoothing", "DCT Energy Anomaly"],
      icon: Cpu,
      badge: "Moderate Concern"
    },
    {
      id: 'genuine_mutual_fund_statement',
      title: "Genuine Baseline: HDFC AMC Mutual Fund Statement",
      title_hi: "Asli Baseline: HDFC Mutual Fund Statement",
      persona: "Authentic quarterly statement with statutory risk disclaimer and consistent typography",
      persona_hi: "Asli account statement jisme Regulatory Authority statutory warning aur ek jaisa font hai",
      tag: "Authentic Document",
      tag_color: "bg-emerald-100 text-emerald-800 border-emerald-200",
      signals: ["Consistent Rasterization", "Official Regulatory Authority Regn", "Zero Scam Language"],
      icon: ShieldCheck,
      badge: "Low Concern"
    }
  ];

  return (
    <div className="space-y-6 mb-8">
      {/* CURATED SAMPLE SCENARIOS */}
      <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-950 text-white rounded-2xl p-6 shadow-sm border border-slate-700">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-5 border-b border-slate-700/80 pb-4">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-blue-600/30 border border-blue-400/40 flex items-center justify-center text-blue-400">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold uppercase tracking-wider text-white m-0">
                  {language === 'hi' ? 'Niveshak Suraksha Sample Scenarios' : 'Curated Verification Safety Sample Scenarios'}
                </h3>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-400/30">
                  Sample Data
                </span>
              </div>
              <p className="text-xs text-slate-300 m-0">
                {language === 'hi'
                  ? 'Niveshakon ki suraksha ke liye banaye gaye synthetic sample cases. Sample data for demonstration purposes.'
                  : 'Curated synthetic sample cases reflecting common investor fraud patterns. Sample data for demonstration purposes.'}
              </p>
            </div>
          </div>

          <span className="text-[11px] font-mono text-slate-400">
            Instant 1-Click Evaluation
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {demoScenarios.map((demo) => {
            const Icon = demo.icon;
            return (
              <div
                key={demo.id}
                className="bg-slate-800/80 hover:bg-slate-800 border border-slate-700 hover:border-blue-400/60 rounded-xl p-4 transition flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${demo.tag_color}`}>
                      {demo.tag}
                    </span>
                    <span className="text-[10px] font-mono font-bold text-slate-400">
                      {demo.badge}
                    </span>
                  </div>

                  <h4 className="text-sm font-bold text-white mb-1">
                    {language === 'hi' ? demo.title_hi : demo.title}
                  </h4>
                  <p className="text-xs text-slate-300 leading-relaxed mb-3">
                    {language === 'hi' ? demo.persona_hi : demo.persona}
                  </p>

                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {demo.signals.map((sig, si) => (
                      <span
                        key={si}
                        className="px-2 py-0.5 rounded bg-slate-900/60 border border-slate-700 text-[10px] text-slate-300 font-mono"
                      >
                        {sig}
                      </span>
                    ))}
                  </div>
                </div>

                <button
                  onClick={() => onSelectDemoScenario(demo.id)}
                  disabled={isAnalyzing}
                  className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-xs transition cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span>{language === 'hi' ? 'Is Demo Ko Analyze Karein' : 'Analyze Demo Case'}</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* ADDITIONAL PRELOADED DOCUMENTS */}
      {samples.length > 0 && (
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs p-6">
          <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider m-0">
                Additional Preloaded Sample Documents
              </h3>
              <p className="text-xs text-slate-500 m-0">
                Inspect fictional demo documents; no real personal records
              </p>
            </div>
            <span className="text-xs font-mono text-slate-500">
              {samples.length} Files Available
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2.5">
            {samples.slice(0, 12).map((s) => (
              <button
                key={s.filename}
                onClick={() => onSelectSample(s.filename)}
                disabled={isAnalyzing}
                className="p-2.5 rounded-xl bg-slate-50 hover:bg-blue-50/50 border border-slate-200 hover:border-blue-300 text-left transition cursor-pointer disabled:opacity-50"
              >
                <div className="text-[11px] font-bold text-slate-900 truncate">
                  {s.label}
                </div>
                <div className="text-[10px] text-slate-500 font-mono mt-0.5 truncate">
                  {s.category}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
