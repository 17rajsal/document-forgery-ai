import React, { useState, useEffect, useRef } from 'react';
import { Volume2, VolumeX, Play, Pause, RotateCcw, Sparkles } from 'lucide-react';

export default function VoicePlayer({ textEn, textHi, language = 'en' }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const utteranceRef = useRef(null);

  useEffect(() => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      setIsSupported(true);
    }
  }, []);

  const stopSpeaking = () => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
    }
  };

  const handlePlayToggle = () => {
    if (!isSupported) return;

    if (isPlaying) {
      stopSpeaking();
      return;
    }

    window.speechSynthesis.cancel();

    const textToSpeak = language === 'hi' ? (textHi || textEn) : (textEn || textHi);
    if (!textToSpeak) return;

    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utteranceRef.current = utterance;

    // Attempt to select language voice
    const voices = window.speechSynthesis.getVoices();
    if (language === 'hi') {
      const hiVoice = voices.find(v => v.lang.startsWith('hi') || v.name.toLowerCase().includes('hindi') || v.name.toLowerCase().includes('india'));
      if (hiVoice) utterance.voice = hiVoice;
      utterance.lang = 'hi-IN';
      utterance.rate = 0.95; // Slightly calmer pace
    } else {
      const enVoice = voices.find(v => v.lang.startsWith('en-IN') || v.lang.startsWith('en-GB') || v.lang.startsWith('en-US'));
      if (enVoice) utterance.voice = enVoice;
      utterance.lang = 'en-US';
      utterance.rate = 1.0;
    }

    utterance.onend = () => setIsPlaying(false);
    utterance.onerror = () => setIsPlaying(false);

    window.speechSynthesis.speak(utterance);
    setIsPlaying(true);
  };

  // Stop audio if component unmounts
  useEffect(() => {
    return () => {
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  if (!isSupported) return null;

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={handlePlayToggle}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer shadow-xs ${
          isPlaying
            ? 'bg-rose-100 text-rose-800 border border-rose-200 hover:bg-rose-200'
            : 'bg-indigo-50 text-indigo-700 border border-indigo-200 hover:bg-indigo-100'
        }`}
        title={isPlaying ? 'Pause spoken explanation' : 'Listen to explanation in voice audio'}
      >
        {isPlaying ? (
          <>
            <Pause className="h-3.5 w-3.5 text-rose-600 animate-pulse" />
            <span>{language === 'hi' ? 'Rokein' : 'Pause'}</span>
          </>
        ) : (
          <>
            <Volume2 className="h-3.5 w-3.5 text-indigo-600" />
            <span>{language === 'hi' ? 'Sunein (Audio)' : 'Listen to Findings'}</span>
          </>
        )}
      </button>

      {isPlaying && (
        <span className="flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-indigo-50 text-[10px] text-indigo-600 font-mono">
          <span className="h-1.5 w-1 bg-indigo-600 rounded-full animate-bounce" />
          <span className="h-2.5 w-1 bg-indigo-600 rounded-full animate-bounce [animation-delay:0.15s]" />
          <span className="h-1.5 w-1 bg-indigo-600 rounded-full animate-bounce [animation-delay:0.3s]" />
        </span>
      )}
    </div>
  );
}
