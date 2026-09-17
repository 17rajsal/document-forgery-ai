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
  Receipt
} from 'lucide-react';

export default function SampleDocuments({
  samples = [],
  onSelectSample,
  isAnalyzing
}) {
  if (!samples || samples.length === 0) return null;

  const getCategoryIcon = (category = '') => {
    const cat = category.toLowerCase();
    if (cat.includes('id') || cat.includes('government') || cat.includes('aadhaar')) {
      return CreditCard;
    }
    if (cat.includes('academic') || cat.includes('marksheet') || cat.includes('result')) {
      return GraduationCap;
    }
    if (cat.includes('bank')) {
      return Landmark;
    }
    if (cat.includes('invoice') || cat.includes('financial')) {
      return Receipt;
    }
    return FileText;
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '';
    const k = 1024;
    return (bytes / k).toFixed(0) + ' KB';
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs p-6 mb-8">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="h-7 w-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-xs">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider m-0">
              Preloaded Sample Documents
            </h3>
            <p className="text-xs text-slate-500 m-0">
              Test the AI forensic pipeline instantly with built-in benchmark files
            </p>
          </div>
        </div>

        <span className="text-[11px] font-semibold text-slate-500 font-mono">
          {samples.length} Demo Documents Available
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {samples.map((s) => {
          const Icon = getCategoryIcon(s.category);
          return (
            <div
              key={s.filename}
              className="p-3.5 rounded-xl bg-slate-50/70 hover:bg-white border border-slate-200/80 hover:border-blue-300 hover:shadow-xs transition group flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="p-2 rounded-lg bg-white border border-slate-200 text-blue-600 group-hover:text-blue-700 group-hover:border-blue-200 transition shrink-0">
                    <Icon className="h-4 w-4" />
                  </div>
                  <span className="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider bg-amber-50 text-amber-800 border border-amber-200">
                    Demo Document
                  </span>
                </div>

                <h4 className="text-xs font-bold text-slate-900 group-hover:text-blue-700 transition truncate m-0">
                  {s.label}
                </h4>
                <div className="flex items-center gap-2 mt-1 text-[11px] text-slate-500 font-mono">
                  <span>{s.category}</span>
                  {s.size_bytes && (
                    <>
                      <span>•</span>
                      <span>{formatFileSize(s.size_bytes)}</span>
                    </>
                  )}
                </div>
              </div>

              <button
                onClick={() => onSelectSample(s.filename)}
                disabled={isAnalyzing}
                className="mt-3 w-full flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg bg-white hover:bg-blue-50 text-blue-600 text-xs font-semibold border border-slate-200 hover:border-blue-200 transition cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span>Try Sample</span>
                <ArrowRight className="h-3 w-3 group-hover:translate-x-0.5 transition-transform" />
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
