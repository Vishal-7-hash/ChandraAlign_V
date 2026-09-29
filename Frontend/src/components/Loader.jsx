import React from 'react';
import { Loader2 } from 'lucide-react';

export const Loader = ({ message = "Processing lunar surface registration..." }) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 bg-slate-900/60 rounded-xl border border-slate-800 backdrop-blur-sm shadow-2xl">
      <div className="relative flex items-center justify-center">
        <div className="w-16 h-16 rounded-full border-4 border-cyan-500/20 border-t-cyan-400 animate-spin" />
        <Loader2 className="w-8 h-8 text-cyan-400 animate-pulse absolute" />
      </div>
      <p className="mt-4 text-sm font-medium text-slate-300 tracking-wide">{message}</p>
      <p className="text-xs text-slate-500 mt-1">Executing feature extraction and homography matrix computation...</p>
    </div>
  );
};

export default Loader;