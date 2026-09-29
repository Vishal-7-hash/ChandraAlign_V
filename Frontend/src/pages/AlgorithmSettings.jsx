import React, { useState } from 'react';
import { Save, RefreshCw, Sliders } from 'lucide-react';

export const AlgorithmSettings = () => {
  const [config, setConfig] = useState({
    detector: 'SIFT',
    maxFeatures: 5000,
    matchThreshold: 0.75,
    ransacReprojThreshold: 3.0,
    maxRansacIters: 2000,
    subpixelRefinement: true,
  });

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-800 pb-5 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Sliders className="w-5 h-5 text-cyan-400" /> Algorithm & Matching Parameters
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Configure feature detector metrics, RANSAC outlier filtering, and matrix solvers.
          </p>
        </div>
        <button
          onClick={() => alert('Settings saved successfully!')}
          className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold rounded-lg flex items-center gap-2 transition"
        >
          <Save className="w-4 h-4" /> Save Configuration
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Feature Extraction */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <h3 className="text-sm font-semibold text-slate-200 border-b border-slate-800 pb-2">
            Feature Extraction Engine
          </h3>
          <div className="space-y-3 text-xs">
            <div>
              <label className="block text-slate-400 mb-1">Feature Detector Type</label>
              <select
                value={config.detector}
                onChange={(e) => setConfig({ ...config, detector: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:border-cyan-500 outline-none"
              >
                <option value="SIFT">SIFT (Scale-Invariant Feature Transform)</option>
                <option value="ORB">ORB (Oriented FAST and Rotated BRIEF)</option>
                <option value="AKAZE">AKAZE (Accelerated-KAZE)</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Maximum Features per Image</label>
              <input
                type="number"
                value={config.maxFeatures}
                onChange={(e) => setConfig({ ...config, maxFeatures: Number(e.target.value) })}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 font-mono focus:border-cyan-500 outline-none"
              />
            </div>
          </div>
        </div>

        {/* Robust Estimation */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <h3 className="text-sm font-semibold text-slate-200 border-b border-slate-800 pb-2">
            Homography & RANSAC Pipeline
          </h3>
          <div className="space-y-3 text-xs">
            <div>
              <label className="block text-slate-400 mb-1">RANSAC Reprojection Error Threshold (px)</label>
              <input
                type="number"
                step="0.1"
                value={config.ransacReprojThreshold}
                onChange={(e) => setConfig({ ...config, ransacReprojThreshold: Number(e.target.value) })}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 font-mono focus:border-cyan-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Max Iterations</label>
              <input
                type="number"
                value={config.maxRansacIters}
                onChange={(e) => setConfig({ ...config, maxRansacIters: Number(e.target.value) })}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 font-mono focus:border-cyan-500 outline-none"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlgorithmSettings;