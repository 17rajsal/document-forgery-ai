import React, { useState } from 'react';
import {
  ShieldAlert,
  AlertTriangle,
  QrCode,
  Landmark,
  Layers,
  Info,
  CheckCircle2,
  ExternalLink,
  ChevronRight
} from 'lucide-react';

export default function VisualEvidenceMap({
  previewImage,
  visualBoxes = [],
  imageWidth = 1240,
  imageHeight = 1754,
  language = 'en'
}) {
  const [activeFilter, setActiveFilter] = useState('all'); // 'all', 'red', 'orange', 'yellow', 'blue'
  const [selectedBoxId, setSelectedBoxId] = useState(visualBoxes[0]?.id || null);

  const filteredBoxes = visualBoxes.filter((box) => {
    if (activeFilter === 'all') return true;
    return box.color === activeFilter;
  });

  const selectedBox = visualBoxes.find((b) => b.id === selectedBoxId) || filteredBoxes[0];

  const getColorClasses = (color) => {
    switch (color) {
      case 'red':
        return {
          border: 'border-rose-500',
          bg: 'bg-rose-500/20 hover:bg-rose-500/30',
          badge: 'bg-rose-600 text-white',
          text: 'text-rose-700',
          pill: 'bg-rose-50 border-rose-200 text-rose-700'
        };
      case 'orange':
        return {
          border: 'border-amber-500',
          bg: 'bg-amber-500/20 hover:bg-amber-500/30',
          badge: 'bg-amber-600 text-white',
          text: 'text-amber-800',
          pill: 'bg-amber-50 border-amber-200 text-amber-800'
        };
      case 'yellow':
        return {
          border: 'border-yellow-500',
          bg: 'bg-yellow-400/25 hover:bg-yellow-400/35',
          badge: 'bg-yellow-600 text-white',
          text: 'text-yellow-900',
          pill: 'bg-yellow-50 border-yellow-200 text-yellow-800'
        };
      case 'blue':
      default:
        return {
          border: 'border-blue-500',
          bg: 'bg-blue-500/20 hover:bg-blue-500/30',
          badge: 'bg-blue-600 text-white',
          text: 'text-blue-700',
          pill: 'bg-blue-50 border-blue-200 text-blue-700'
        };
    }
  };

  const counts = {
    red: visualBoxes.filter((b) => b.color === 'red').length,
    orange: visualBoxes.filter((b) => b.color === 'orange').length,
    yellow: visualBoxes.filter((b) => b.color === 'yellow').length,
    blue: visualBoxes.filter((b) => b.color === 'blue').length,
  };

  return (
    <div className="space-y-6">
      {/* FILTER PILLS */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-50 p-3 rounded-xl border border-slate-200/80">
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-xs font-semibold text-slate-500 mr-1">
            {language === 'hi' ? 'Evidence Filter:' : 'Filter Layers:'}
          </span>
          <button
            onClick={() => setActiveFilter('all')}
            className={`px-3 py-1 rounded-lg text-xs font-semibold transition cursor-pointer border ${
              activeFilter === 'all'
                ? 'bg-slate-900 text-white border-slate-900 shadow-xs'
                : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-100'
            }`}
          >
            All Evidence ({visualBoxes.length})
          </button>

          {counts.red > 0 && (
            <button
              onClick={() => setActiveFilter('red')}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold transition cursor-pointer border ${
                activeFilter === 'red'
                  ? 'bg-rose-600 text-white border-rose-600 shadow-xs'
                  : 'bg-rose-50 text-rose-700 border-rose-200 hover:bg-rose-100'
              }`}
            >
              <span className="h-2 w-2 rounded-full bg-rose-500" />
              <span>{language === 'hi' ? 'Chhed-Chhad' : 'Manipulation'} ({counts.red})</span>
            </button>
          )}

          {counts.orange > 0 && (
            <button
              onClick={() => setActiveFilter('orange')}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold transition cursor-pointer border ${
                activeFilter === 'orange'
                  ? 'bg-amber-600 text-white border-amber-600 shadow-xs'
                  : 'bg-amber-50 text-amber-800 border-amber-200 hover:bg-amber-100'
              }`}
            >
              <span className="h-2 w-2 rounded-full bg-amber-500" />
              <span>{language === 'hi' ? 'Bade Daawe' : 'High-Risk Claims'} ({counts.orange})</span>
            </button>
          )}

          {counts.yellow > 0 && (
            <button
              onClick={() => setActiveFilter('yellow')}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold transition cursor-pointer border ${
                activeFilter === 'yellow'
                  ? 'bg-yellow-600 text-white border-yellow-600 shadow-xs'
                  : 'bg-yellow-50 text-yellow-800 border-yellow-200 hover:bg-yellow-100'
              }`}
            >
              <span className="h-2 w-2 rounded-full bg-yellow-500" />
              <span>{language === 'hi' ? 'Payment / QR' : 'QR / Payment'} ({counts.yellow})</span>
            </button>
          )}

          {counts.blue > 0 && (
            <button
              onClick={() => setActiveFilter('blue')}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold transition cursor-pointer border ${
                activeFilter === 'blue'
                  ? 'bg-blue-600 text-white border-blue-600 shadow-xs'
                  : 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100'
              }`}
            >
              <span className="h-2 w-2 rounded-full bg-blue-500" />
              <span>{language === 'hi' ? 'Pehchan / SEBI' : 'Regulatory'} ({counts.blue})</span>
            </button>
          )}
        </div>

        <span className="text-[11px] text-slate-400 font-mono">
          {language === 'hi' ? 'Kisi bhi box par click karein' : 'Click box to inspect findings'}
        </span>
      </div>

      {/* TWO-COLUMN WORKSPACE: DOCUMENT OVERLAY (LEFT) + INSPECTION DRAWER (RIGHT) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* DOCUMENT CANVAS WITH SVG OVERLAY */}
        <div className="lg:col-span-7 bg-slate-900/5 rounded-2xl border border-slate-200 p-3 flex items-center justify-center relative overflow-hidden">
          <div className="relative inline-block max-h-[580px] w-auto">
            {previewImage && (
              <img
                src={previewImage}
                alt="Document Evidence Preview"
                className="max-h-[560px] w-auto rounded-xl shadow-md object-contain bg-white block"
              />
            )}

            {/* INTERACTIVE BOUNDING BOXES OVERLAY */}
            <div className="absolute inset-0 pointer-events-auto">
              {filteredBoxes.map((box) => {
                const colors = getColorClasses(box.color);
                const isSelected = selectedBox?.id === box.id;

                const leftPct = (box.bbox.x / imageWidth) * 100;
                const topPct = (box.bbox.y / imageHeight) * 100;
                const widthPct = (box.bbox.w / imageWidth) * 100;
                const heightPct = (box.bbox.h / imageHeight) * 100;

                return (
                  <div
                    key={box.id}
                    onClick={() => setSelectedBoxId(box.id)}
                    className={`absolute border-2 rounded-md transition cursor-pointer group ${colors.border} ${colors.bg} ${
                      isSelected ? 'ring-3 ring-blue-500/80 shadow-lg scale-[1.02] z-20' : 'z-10'
                    }`}
                    style={{
                      left: `${Math.max(0, Math.min(96, leftPct))}%`,
                      top: `${Math.max(0, Math.min(96, topPct))}%`,
                      width: `${Math.max(4, Math.min(95, widthPct))}%`,
                      height: `${Math.max(2.5, Math.min(95, heightPct))}%`,
                    }}
                    title={`${box.label}: ${box.text_snippet}`}
                  >
                    {/* Badge tag on box */}
                    <span
                      className={`absolute -top-3 left-0 px-1.5 py-0.2 rounded text-[9px] font-bold tracking-wider uppercase shadow-xs whitespace-nowrap ${colors.badge}`}
                    >
                      {box.label}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* EVIDENCE DETAIL CARD (RIGHT) */}
        <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs space-y-4">
          {selectedBox ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <span
                  className={`px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                    getColorClasses(selectedBox.color).pill
                  }`}
                >
                  {selectedBox.badge}
                </span>

                <span className="text-[11px] font-mono text-slate-500 font-semibold">
                  Region ID: {selectedBox.id}
                </span>
              </div>

              <div>
                <h3 className="text-base font-bold text-slate-900 m-0">
                  {selectedBox.label}
                </h3>
                <p className="text-xs text-slate-500 mt-1 m-0">
                  {language === 'hi' ? 'Document mein pehchana gaya text:' : 'Detected text / target in document:'}
                </p>
                <div className="mt-1.5 p-2.5 bg-slate-50 border border-slate-200 rounded-xl font-mono text-xs font-bold text-slate-800 break-words">
                  "{selectedBox.text_snippet}"
                </div>
              </div>

              {/* WHY THIS MATTERS */}
              <div className="p-3.5 rounded-xl bg-blue-50/50 border border-blue-100 text-xs space-y-1">
                <span className="font-bold text-blue-900 flex items-center gap-1.5">
                  <Info className="h-3.5 w-3.5 text-blue-600" />
                  <span>{language === 'hi' ? 'Yeh kyon zaroori hai?' : 'Why is this flagged?'}</span>
                </span>
                <p className="text-slate-600 text-[11px] leading-relaxed m-0">
                  {selectedBox.explanation}
                </p>
              </div>

              {/* STATUTORY VERIFICATION SOURCE IF PRESENT */}
              {selectedBox.verification_source && (
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 text-[11px] text-slate-600 space-y-1">
                  <span className="font-semibold text-slate-800">
                    {language === 'hi' ? 'Official Sandarbh (Authority):' : 'Official Regulatory Reference:'}
                  </span>
                  <p className="text-slate-500 m-0 leading-relaxed font-mono text-[10px]">
                    {selectedBox.verification_source}
                  </p>
                </div>
              )}

              {/* ACTION FOOTER */}
              <div className="pt-2 text-[11px] text-slate-500 font-medium">
                {language === 'hi'
                  ? 'Bina official source se verify kiye is daawe par bharosa na karein.'
                  : 'Always verify claims independently on official exchange or regulator portals.'}
              </div>
            </div>
          ) : (
            <div className="text-center py-16 text-slate-400 text-xs">
              {language === 'hi' ? 'Kisi bhi highlight par click karein' : 'Select an evidence highlight on the document to inspect forensic findings.'}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
