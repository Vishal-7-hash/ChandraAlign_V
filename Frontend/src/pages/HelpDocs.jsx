import React from 'react';
import { HelpCircle, BookOpen, ExternalLink } from 'lucide-react';

export const HelpDocs = () => {
  return (
    <div className="space-y-6">
      <div className="border-b border-slate-800 pb-5">
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <HelpCircle className="w-5 h-5 text-cyan-400" /> User Guide & Technical Documentation
        </h2>
        <p className="text-xs text-slate-400 mt-1">Understanding homography estimation, XML coordinate metadata, and surface matching.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
          <h3 className="font-semibold text-slate-200 text-sm flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-cyan-400" /> XML Metadata Standards
          </h3>
          <p className="text-slate-400 leading-relaxed">
            The metadata XML files must specify orbital geometric matrices, intrinsic focal lengths, camera sensor orientation vectors, and solar illumination angles.
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
          <h3 className="font-semibold text-slate-200 text-sm flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-cyan-400" /> Interpreting RMSE & Inlier Metrics
          </h3>
          <p className="text-slate-400 leading-relaxed">
            An <b>RMSE below 0.50 px</b> indicates sub-pixel registration accuracy. An <b>Inlier Ratio above 60%</b> confirms high feature correspondence reliability without false matches.
          </p>
        </div>
      </div>
    </div>
  );
};

export default HelpDocs;