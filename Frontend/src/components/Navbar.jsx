import React from 'react';
import { Moon, Sparkles, Layers } from 'lucide-react';

export const Navbar = () => {
  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-40">
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-cyan-500/10 border border-cyan-500/30 rounded-lg">
          <Moon className="w-5 h-5 text-cyan-400" />
        </div>
        <div>
          <h1 className="text-base font-bold text-slate-100 tracking-tight flex items-center gap-2">
            ChandraAlign <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/60 font-mono">v1.0.0</span>
          </h1>
          <p className="text-[11px] text-slate-400">Robust Lunar Correspondence System (RLCS)</p>
        </div>
      </div>

      <div className="flex items-center space-x-4 text-xs font-mono">
        <div className="flex items-center space-x-2 text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-2.5 py-1 rounded-full">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>FastAPI Engine Online</span>
        </div>
      </div>
    </header>
  );
};

export default Navbar;