import React, { useRef, useState, useEffect } from 'react';
import { Camera, RotateCcw, ArrowRight, X, AlertTriangle, ShieldCheck, Upload } from 'lucide-react';

export default function CameraCapture({
  onPhotoCaptured,
  onCancel,
  isAnalyzing = false
}) {
  const [stream, setStream] = useState(null);
  const [capturedImageUrl, setCapturedImageUrl] = useState(null);
  const [capturedBlob, setCapturedBlob] = useState(null);
  const [error, setError] = useState(null);
  const [qualityWarning, setQualityWarning] = useState(null);
  const [isStarting, setIsStarting] = useState(true);

  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const fallbackInputRef = useRef(null);

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
      setStream(null);
    }
  };

  const startCamera = async () => {
    setError(null);
    setQualityWarning(null);
    setIsStarting(true);

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Camera access is unavailable. You can upload a photo instead.');
      }

      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: { ideal: 'environment' },
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        },
        audio: false
      });

      streamRef.current = mediaStream;
      setStream(mediaStream);

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.play().catch(() => {});
      }
    } catch (err) {
      setError('Camera access is unavailable. You can upload a photo instead.');
    } finally {
      setIsStarting(false);
    }
  };

  useEffect(() => {
    startCamera();
    return () => {
      stopCamera();
      if (capturedImageUrl) {
        URL.revokeObjectURL(capturedImageUrl);
      }
    };
  }, []);

  const handleCapture = () => {
    const video = videoRef.current;
    if (!video) return;

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 1280;
    canvas.height = video.videoHeight || 720;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Lightweight quality checks: check average brightness and resolution
    try {
      const sampleCanvas = document.createElement('canvas');
      sampleCanvas.width = 100;
      sampleCanvas.height = 100;
      const sCtx = sampleCanvas.getContext('2d');
      sCtx.drawImage(canvas, 0, 0, 100, 100);
      const imgData = sCtx.getImageData(0, 0, 100, 100);
      let totalBrightness = 0;
      for (let i = 0; i < imgData.data.length; i += 4) {
        totalBrightness += (imgData.data[i] + imgData.data[i + 1] + imgData.data[i + 2]) / 3;
      }
      const avgBrightness = totalBrightness / (100 * 100);
      if (avgBrightness < 35) {
        setQualityWarning('The photo appears dark. For best results, ensure the document is well lit.');
      } else if (canvas.width < 500 || canvas.height < 500) {
        setQualityWarning('Low resolution photo detected. Text details may be difficult to read.');
      } else {
        setQualityWarning(null);
      }
    } catch (e) {
      // Ignore quality check errors
    }

    canvas.toBlob((blob) => {
      if (blob) {
        setCapturedBlob(blob);
        setCapturedImageUrl(URL.createObjectURL(blob));
        stopCamera();
      }
    }, 'image/jpeg', 0.92);
  };

  const handleRetake = () => {
    if (capturedImageUrl) {
      URL.revokeObjectURL(capturedImageUrl);
      setCapturedImageUrl(null);
      setCapturedBlob(null);
    }
    setQualityWarning(null);
    startCamera();
  };

  const handleAnalyzePhoto = () => {
    if (!capturedBlob) return;
    const file = new File([capturedBlob], `camera_doc_${Date.now()}.jpg`, { type: 'image/jpeg' });
    stopCamera();
    onPhotoCaptured(file);
  };

  const handleFallbackFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      stopCamera();
      onPhotoCaptured(file);
    }
  };

  return (
    <div className="space-y-4">
      {/* Hidden fallback file input with capture="environment" */}
      <input
        ref={fallbackInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={handleFallbackFileChange}
      />

      {error ? (
        <div className="p-6 rounded-2xl bg-amber-50 border border-amber-200 text-center space-y-3">
          <div className="h-10 w-10 mx-auto rounded-full bg-amber-100 text-amber-700 flex items-center justify-center">
            <AlertTriangle className="h-5 w-5" />
          </div>
          <div>
            <p className="text-xs font-semibold text-amber-900 m-0">{error}</p>
            <p className="text-[11px] text-amber-700 mt-1 m-0">
              Please grant camera permission or use your device photo picker.
            </p>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-2 pt-2">
            <button
              onClick={() => fallbackInputRef.current?.click()}
              className="px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold transition flex items-center gap-1.5 cursor-pointer"
            >
              <Camera className="h-4 w-4" />
              <span>Take Photo via Device Camera</span>
            </button>
            <button
              onClick={onCancel}
              className="px-4 py-2 rounded-xl bg-white border border-slate-300 text-slate-700 text-xs font-semibold hover:bg-slate-50 transition cursor-pointer"
            >
              Upload File Instead
            </button>
          </div>
        </div>
      ) : capturedImageUrl ? (
        /* CAPTURED PREVIEW MODE */
        <div className="space-y-3">
          <div className="relative rounded-2xl overflow-hidden bg-slate-900 border border-slate-300 shadow-inner">
            <img
              src={capturedImageUrl}
              alt="Captured document"
              className="w-full max-h-[380px] object-contain mx-auto"
            />
          </div>

          {qualityWarning && (
            <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0" />
              <span>{qualityWarning}</span>
            </div>
          )}

          <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
            <button
              onClick={handleRetake}
              disabled={isAnalyzing}
              className="px-4 py-2.5 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-50 text-xs font-bold transition flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
            >
              <RotateCcw className="h-4 w-4" />
              <span>Retake</span>
            </button>

            <div className="flex items-center gap-2">
              <button
                onClick={onCancel}
                disabled={isAnalyzing}
                className="px-3.5 py-2.5 rounded-xl text-slate-500 hover:text-slate-800 text-xs font-semibold transition cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleAnalyzePhoto}
                disabled={isAnalyzing}
                className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white text-xs font-bold shadow-md shadow-blue-600/25 transition flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
              >
                <span>Analyze Photo</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      ) : (
        /* LIVE CAMERA PREVIEW MODE */
        <div className="space-y-3">
          <div className="relative rounded-2xl overflow-hidden bg-black border border-slate-300 aspect-[4/3] max-h-[380px] flex items-center justify-center">
            {isStarting && (
              <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-900 text-white z-10 text-xs gap-2">
                <Camera className="h-6 w-6 animate-pulse text-blue-400" />
                <span>Starting camera...</span>
              </div>
            )}
            <video
              ref={videoRef}
              playsInline
              autoPlay
              muted
              className="w-full h-full object-cover"
            />
            {/* Guide overlay box */}
            <div className="absolute inset-4 sm:inset-8 border-2 border-dashed border-white/60 rounded-xl pointer-events-none flex items-start justify-center pt-2">
              <span className="text-[10px] bg-black/60 backdrop-blur-xs text-white px-2 py-0.5 rounded-md font-mono">
                Align document inside frame
              </span>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center justify-between gap-3 pt-1">
            <button
              onClick={onCancel}
              className="px-4 py-2.5 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-50 text-xs font-semibold transition cursor-pointer"
            >
              Cancel
            </button>

            {/* Large mobile-friendly capture button */}
            <button
              onClick={handleCapture}
              disabled={isStarting}
              className="px-6 py-3 rounded-full bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white text-sm font-bold shadow-lg shadow-blue-600/30 transition flex items-center gap-2 cursor-pointer disabled:opacity-50"
            >
              <Camera className="h-5 w-5" />
              <span>Capture</span>
            </button>

            {/* Mobile device camera fallback link */}
            <button
              onClick={() => fallbackInputRef.current?.click()}
              className="text-[11px] text-blue-600 hover:underline font-medium"
              title="Use system camera app"
            >
              System Camera
            </button>
          </div>
        </div>
      )}

      {/* Privacy disclosure note */}
      <div className="flex items-center gap-1.5 text-[11px] text-slate-500 pt-1">
        <ShieldCheck className="h-3.5 w-3.5 text-blue-600 shrink-0" />
        <span>Your camera is used only to capture the document you choose to analyze.</span>
      </div>
    </div>
  );
}
