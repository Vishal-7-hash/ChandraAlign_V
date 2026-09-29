import React from 'react';
import { Play, Loader2 } from 'lucide-react';

export const ExecuteButton = ({ onExecute, isDisabled, isLoading }) => {
  return (
    <button
      onClick={onExecute}
      disabled={isDisabled || isLoading}
      className={`
        w-full py-3.5 px-6 rounded-xl font-semibold text-sm transition-all duration-200 flex items-center justify-center space-x-2 shadow-lg
        ${
          isDisabled || isLoading
            ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700/50'
            : 'bg-linear-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-cyan-500/20 active:scale-[0.99]'
        }
      `}
    >
      {isLoading ? (
        <>
          <Loader2 className="w-4 h-4 animate-spin text-white" />
          <span>Executing Registration Pipeline...</span>
        </>
      ) : (
        <>
          <Play className="w-4 h-4 fill-current text-white" />
          <span>Align Surface Images</span>
        </>
      )}
    </button>
  );
};

export default ExecuteButton;