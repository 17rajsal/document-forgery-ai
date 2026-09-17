import React from 'react';
import {
  Layers,
  Cpu,
  Search,
  Lock,
  ArrowRight
} from 'lucide-react';

export default function FeatureCards({ onOpenFormats, onOpenHowItWorks }) {
  const features = [
    {
      title: 'Multi-Format Support',
      desc: 'Ingests PDF, DOCX, TIFF, BMP, WEBP, PNG, and JPEG with strict binary magic-byte verification.',
      icon: Layers,
      accent: 'blue',
      badge: '7 Formats',
      action: onOpenFormats
    },
    {
      title: 'AI Forensic Engine',
      desc: 'Combines spatial ELA compression delta, noise variance splicing, and ORB copy-move duplication detection.',
      icon: Cpu,
      accent: 'indigo',
      badge: '4-Tier Risk',
      action: onOpenHowItWorks
    },
    {
      title: 'Tri-Pass Adaptive OCR',
      desc: 'Multi-variant neural OCR (contrast, Otsu binarization, adaptive Gaussian) with word-level confidence and bounding boxes.',
      icon: Search,
      accent: 'violet',
      badge: 'Multi-Pass',
      action: onOpenHowItWorks
    },
    {
      title: 'Enterprise Security',
      desc: 'In-memory processing with automatic transient raster cleanup. Zero public exposure and zero data retention.',
      icon: Lock,
      accent: 'slate',
      badge: 'SOC2-Ready',
      action: null
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
                <span>Learn more</span>
                <ArrowRight className="h-3 w-3 group-hover:translate-x-0.5 transition-transform" />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
