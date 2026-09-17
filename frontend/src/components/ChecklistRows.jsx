import React from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  Cpu,
  Layers,
  Search,
  Fingerprint,
  FileCheck2,
  FileText
} from 'lucide-react';

export default function ChecklistRows({ analysisResult }) {
  if (!analysisResult) return null;

  const fa = analysisResult.forgery_analysis || {};
  const ela = fa.ela_analysis || {};
  const noise = fa.noise_analysis || {};
  const meta = fa.metadata_forensics || {};
  const copyMove = fa.copy_move_analysis || {};
  const layout = fa.text_layout_analysis || {};
  const validations = analysisResult.extracted_fields?.validations || [];

  // 1. Image Consistency (Noise & Spatial compression)
  const isImageConsistent = !noise.anomaly_detected && (ela.is_uniform_compression || ela.average_difference < 12);
  const imageConsistencyRow = {
    category: 'Image Consistency',
    icon: Layers,
    status: isImageConsistent ? 'PASSED' : 'FLAGGED',
    desc: isImageConsistent
      ? 'Uniform background noise and consistent compression levels detected across grid tiles.'
      : noise.anomaly_detected
      ? `Anomalous noise variance detected in ${noise.outlier_blocks || 0} image blocks. Potential digital splicing.`
      : 'Localized compression variance detected between foreground elements and background.'
  };

  // 2. Text Integrity & Layout
  const isLayoutConsistent = !layout.inconsistency_detected;
  const textIntegrityRow = {
    category: 'Text Integrity',
    icon: FileText,
    status: isLayoutConsistent ? 'PASSED' : 'FLAGGED',
    desc: isLayoutConsistent
      ? 'Text line baselines and character bounding heights conform to typical typesetting alignment.'
      : layout.description || 'Abnormal baseline jitter or mismatched font heights detected in text lines.'
  };

  // 3. Metadata Analysis
  const hasEditor = meta.editing_software_detected;
  const metadataRow = {
    category: 'Metadata Analysis',
    icon: Search,
    status: hasEditor ? 'FLAGGED' : 'PASSED',
    desc: hasEditor
      ? `Container tags contain signatures of digital photo editing software: ${meta.detected_software_name || 'Tool detected'}.`
      : meta.has_exif
      ? `Valid camera/scanner hardware metadata found (${meta.camera_model || 'Hardware'}). No editor tags.`
      : 'Clean container stream. No known image manipulation software tags identified.'
  };

  // 4. ELA (Error Level Analysis)
  const isElaPassed = ela.status === 'LOW_ANOMALY' || ela.is_uniform_compression;
  const elaRow = {
    category: 'ELA Analysis',
    icon: Cpu,
    status: isElaPassed ? 'PASSED' : ela.status === 'HIGH_ANOMALY' ? 'FLAGGED' : 'REVIEW',
    desc: isElaPassed
      ? `Error level compression delta is low (avg diff: ${ela.average_difference ?? '0'}) with uniform spatial distribution.`
      : `High error-level compression variance (${ela.anomaly_ratio_pct ?? 0}% anomalous region) indicates localized resaving.`
  };

  // 5. Copy-Move Splicing Detection
  const hasCopyMove = copyMove.detected;
  const copyMoveRow = {
    category: 'Copy-Move Detection',
    icon: Fingerprint,
    status: hasCopyMove ? 'FLAGGED' : 'PASSED',
    desc: hasCopyMove
      ? copyMove.description || 'Identical visual feature clusters detected in disparate document coordinates.'
      : 'No duplicated stamp, signature, or graphic keypoint clusters identified.'
  };

  // 6. Document Structure & Algorithmic Validation
  const hasCritValidation = validations.some(v => v.severity === 'CRITICAL');
  const hasPassValidation = validations.some(v => v.severity === 'VERIFIED');
  const structureRow = {
    category: 'Document Structure',
    icon: FileCheck2,
    status: hasCritValidation ? 'FLAGGED' : hasPassValidation ? 'PASSED' : 'INCONCLUSIVE',
    desc: hasCritValidation
      ? 'Mathematical validation checks (e.g. Verhoeff dihedral D5 checksum or GSTIN structure) failed.'
      : hasPassValidation
      ? 'Document formatting and mathematical checksums verified successfully.'
      : 'Standard structure parsed. No mandatory mathematical checksum required for this category.'
  };

  const rows = [
    imageConsistencyRow,
    textIntegrityRow,
    metadataRow,
    elaRow,
    copyMoveRow,
    structureRow
  ];

  return (
    <div className="space-y-2.5">
      {rows.map((r, idx) => {
        const Icon = r.icon;
        const isPassed = r.status === 'PASSED';
        const isFlagged = r.status === 'FLAGGED';
        const isReview = r.status === 'REVIEW' || r.status === 'INCONCLUSIVE';

        return (
          <div
            key={idx}
            className={`p-3.5 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs transition ${
              isFlagged
                ? 'bg-rose-50/50 border-rose-200'
                : isPassed
                ? 'bg-slate-50/70 border-slate-200'
                : 'bg-amber-50/50 border-amber-200'
            }`}
          >
            <div className="flex items-start sm:items-center gap-3">
              <div
                className={`p-2 rounded-lg shrink-0 ${
                  isFlagged
                    ? 'bg-rose-100 text-rose-700'
                    : isPassed
                    ? 'bg-emerald-100 text-emerald-700'
                    : 'bg-amber-100 text-amber-700'
                }`}
              >
                <Icon className="h-4 w-4" />
              </div>
              <div>
                <span className="font-bold text-slate-900 block sm:inline mr-2">
                  {r.category}:
                </span>
                <span className="text-slate-600 leading-relaxed">
                  {r.desc}
                </span>
              </div>
            </div>

            <div className="shrink-0 self-end sm:self-center">
              <span
                className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider font-mono ${
                  isFlagged
                    ? 'bg-rose-100 text-rose-800 border border-rose-200'
                    : isPassed
                    ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                    : 'bg-amber-100 text-amber-800 border border-amber-200'
                }`}
              >
                {isFlagged ? (
                  <>
                    <XCircle className="h-3 w-3" />
                    <span>Flagged</span>
                  </>
                ) : isPassed ? (
                  <>
                    <CheckCircle2 className="h-3 w-3" />
                    <span>Passed</span>
                  </>
                ) : (
                  <>
                    <AlertTriangle className="h-3 w-3" />
                    <span>Review</span>
                  </>
                )}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
