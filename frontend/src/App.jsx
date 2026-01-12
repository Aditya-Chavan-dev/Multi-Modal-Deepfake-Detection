import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileImage, FileAudio, FileVideo, ShieldCheck, AlertTriangle, Scan, CheckCircle2 } from 'lucide-react';
import { simulateAnalysis } from './lib/simulation';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Helper for conditional classes
function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export default function App() {
  return (
    <div className="min-h-screen bg-background text-primary selection:bg-white/20 overflow-x-hidden relative">
      {/* Background Grid */}
      <div className="fixed inset-0 z-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
      <div className="fixed inset-0 z-0 bg-gradient-to-tr from-background via-transparent to-background/80 pointer-events-none"></div>

      <main className="relative z-10 max-w-6xl mx-auto px-6 py-20 flex flex-col items-center">

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16 space-y-4"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium tracking-wider text-secondary uppercase mb-4">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            System Operational v2.4
          </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-b from-white to-white/60">
            DeepFake Guard
          </h1>
          <p className="text-secondary text-lg max-w-xl mx-auto leading-relaxed">
            Advanced forensic analysis for digital media authentication.
            Detect AI-generated anomalies in real-time.
          </p>
        </motion.div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
          <AnalysisCard
            type="image"
            title="Image Forensics"
            desc="Gabor filter texture analysis"
            icon={FileImage}
            accept="image/*"
          />
          <AnalysisCard
            type="audio"
            title="Voice Biometrics"
            desc="MFCC spectral signature matching"
            icon={FileAudio}
            accept="audio/*"
          />
          <AnalysisCard
            type="video"
            title="Video Integrity"
            desc="Temporal frame-by-frame forensics"
            icon={FileVideo}
            accept="video/*"
          />
        </div>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-24 text-center text-sm text-white/20 font-mono"
        >
          SECURE CONNECTION // ENCRYPTED
        </motion.footer>
      </main>
    </div>
  );
}

function AnalysisCard({ type, title, desc, icon: Icon, accept }) {
  const [file, setFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);

  const handleFile = async (e) => {
    const selected = e.target.files?.[0];
    if (!selected) return;

    setFile(selected);
    setResult(null);
  };

  const startAnalysis = async () => {
    if (!file) return;
    setIsAnalyzing(true);
    const res = await simulateAnalysis(file);
    setResult(res);
    setIsAnalyzing(false);
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ y: -5 }}
      className="group relative bg-surface border border-border rounded-xl p-6 h-[420px] flex flex-col transition-all hover:border-white/20 hover:bg-surface/80 hover:shadow-2xl hover:shadow-black/50"
    >
      {/* Glow Effect */}
      <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-xl pointer-events-none" />

      {/* Header */}
      <div className="relative z-10 flex-1 flex flex-col items-center text-center pt-8">
        <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-6 text-white group-hover:scale-110 transition-transform duration-500">
          <Icon size={32} strokeWidth={1.5} />
        </div>
        <h3 className="text-xl font-semibold mb-2">{title}</h3>
        <p className="text-sm text-secondary px-4">{desc}</p>
      </div>

      {/* Analyzer Interface */}
      <div className="relative z-10 mt-auto space-y-4">
        <AnimatePresence mode="wait">
          {!result ? (
            <motion.div
              key="input"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-3"
            >
              {/* File Input */}
              <div className="relative">
                <input
                  type="file"
                  id={`file-${type}`}
                  accept={accept}
                  onChange={handleFile}
                  disabled={isAnalyzing}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
                />
                <label
                  htmlFor={`file-${type}`}
                  className={cn(
                    "block w-full py-3 px-4 rounded-lg border border-dashed text-sm text-center transition-all truncate",
                    file
                      ? "border-white/40 text-white bg-white/5"
                      : "border-border text-secondary hover:border-white/40 hover:text-white"
                  )}
                >
                  {file ? file.name : `Select ${title.split(' ')[0]} File`}
                </label>
              </div>

              {/* Action Button */}
              <button
                onClick={startAnalysis}
                disabled={!file || isAnalyzing}
                className={cn(
                  "w-full py-3 rounded-lg font-medium text-sm transition-all flex items-center justify-center gap-2",
                  !file
                    ? "bg-white/5 text-white/20 cursor-not-allowed"
                    : isAnalyzing
                      ? "bg-white/10 text-white cursor-wait"
                      : "bg-white text-black hover:bg-gray-200"
                )}
              >
                {isAnalyzing ? (
                  <>
                    <Scan className="animate-spin" size={16} />
                    SCANNING...
                  </>
                ) : (
                  "ANALYZE"
                )}
              </button>
            </motion.div>
          ) : (
            <motion.div
              key="result"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={cn(
                "p-4 rounded-lg border backdrop-blur-md",
                result.status === 'FAKE'
                  ? "bg-red-500/10 border-red-500/30 text-red-200"
                  : "bg-green-500/10 border-green-500/30 text-green-200"
              )}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2 font-bold tracking-wider">
                  {result.status === 'FAKE' ? <AlertTriangle size={18} /> : <ShieldCheck size={18} />}
                  {result.status}
                </div>
                <div className="text-xs font-mono opacity-80">{result.confidence}% CONFIDENCE</div>
              </div>
              <div className="h-1 w-full bg-black/20 rounded-full overflow-hidden">
                <div
                  className={cn("h-full w-full", result.status === 'FAKE' ? "bg-red-500" : "bg-green-500")}
                ></div>
              </div>
              <p className="text-xs mt-3 opacity-90 leading-tight">
                {result.details}
              </p>

              <button
                onClick={() => { setFile(null); setResult(null); }}
                className="mt-4 w-full py-2 text-xs border border-white/10 rounded hover:bg-white/5 transition-colors"
              >
                NEW SCAN
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
