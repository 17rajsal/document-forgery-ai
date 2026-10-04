import React from 'react';
import {
  Layers,
  Cpu,
  Search,
  Lock,
  ArrowRight,
  QrCode,
  ShieldAlert,
  Sparkles,
  Landmark
} from 'lucide-react';

export default function FeatureCards({ onOpenFormats, onOpenHowItWorks, language = 'en' }) {
  const features = [
    {
      title: language === 'hi' ? 'Multimodal Forensics' : 'Multimodal Forensics',
      desc: language === 'hi'
        ? 'ELA compression, noise variance aur AI Inpainting / Erase detection ek sath.'
        : 'Error Level Analysis (ELA), high-frequency noise residuals, and generative AI inpainting detection.',
      icon: Cpu,
      accent: 'blue',
      badge: 'Vision AI',
      action: onOpenHowItWorks
    },
    {
      title: language === 'hi' ? 'Critical Financial Fields' : 'Critical Field Tampering',
      desc: language === 'hi'
        ? 'Rakam (₹), tareekh, aur ankon vs shabdon ka semantic mismatch check karta hai.'
        : 'Detects edited amounts (₹), return rates, and verbal-vs-numeric contradictions.',
      icon: Landmark,
      accent: 'indigo',
      badge: 'Field Audit',
      action: onOpenHowItWorks
    },
    {
      title: language === 'hi' ? 'Daawe aur Scam Language' : 'Claims & Scam Language',
      desc: language === 'hi'
        ? 'Guaranteed 30% return aur jhoothe SEBI approval ke daawon ko pakadta hai.'
        : 'Flags statutory violations like guaranteed returns, fake SEBI endorsements, and FOMO urgency.',
      icon: ShieldAlert,
      accent: 'violet',
      badge: 'SEBI/RBI Rules',
      action: onOpenHowItWorks
    },
    {
      title: language === 'hi' ? 'QR Code & Payment Audit' : 'QR & Payment Inspection',
      desc: language === 'hi'
        ? 'QR code decode karke personal UPI handle aur fake websites ko expose karta hai.'
        : 'Decodes QR codes to flag personal UPI accounts and typosquatting regulatory domains.',
      icon: QrCode,
      accent: 'slate',
      badge: 'Zero-Click QR',
      action: onOpenHowItWorks
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {features.map((f, idx) => {
        const Icon = f.icon;
        return (
          <div
            key={idx}
            onClick={f.action || undefined}
            className={`bg-white rounded-xl border border-slate-200/90 p-4 shadow-xs hover:shadow-sm hover:border-blue-300 transition flex flex-col justify-between ${
              f.action ? 'cursor-pointer group' : ''
            }`}
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className={`h-8 w-8 rounded-lg flex items-center justify-center ${
                  f.accent === 'blue' ? 'bg-blue-50 text-blue-600' :
                  f.accent === 'indigo' ? 'bg-indigo-50 text-indigo-600' :
                  f.accent === 'violet' ? 'bg-violet-50 text-violet-600' :
                  'bg-slate-100 text-slate-700'
                }`}>
                  <Icon className="h-4 w-4" />
                </div>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-100 text-slate-600 border border-slate-200/60 font-mono">
                  {f.badge}
                </span>
              </div>
              <h3 className="text-xs font-bold text-slate-900 mb-1 group-hover:text-blue-600 transition">
                {f.title}
              </h3>
              <p className="text-[11px] text-slate-500 leading-relaxed m-0">
                {f.desc}
              </p>
            </div>

            {f.action && (
              <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px] text-blue-600 font-medium group-hover:text-blue-700">
                <span>{language === 'hi' ? 'Aur janein' : 'View details'}</span>
                <ArrowRight className="h-3 w-3 group-hover:translate-x-0.5 transition-transform" />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
