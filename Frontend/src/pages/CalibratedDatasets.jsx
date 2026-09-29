import React from 'react';
import { Database, Image as ImageIcon, Folder } from 'lucide-react';

export const CalibratedDatasets = () => {
  const datasets = [
    { title: 'Mare Tranquillitatis High-Res Orbit', resolution: '0.5m/px', pairs: 14, size: '2.4 GB' },
    { title: 'Shackleton Crater Polar Survey', resolution: '1.2m/px', pairs: 8, size: '1.1 GB' },
    { title: 'Tycho Crater Impact Ejecta', resolution: '0.8m/px', pairs: 22, size: '4.8 GB' },
  ];

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-800 pb-5">
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <Database className="w-5 h-5 text-cyan-400" /> Calibrated Lunar Datasets
        </h2>
        <p className="text-xs text-slate-400 mt-1">Pre-registered reference missions and orbital image libraries.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {datasets.map((item, idx) => (
          <div key={idx} className="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl p-4 space-y-3 transition">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-cyan-950 border border-cyan-800/50 rounded-lg">
                <Folder className="w-5 h-5 text-cyan-400" />
              </div>
              <div>
                <h3 className="text-xs font-semibold text-slate-200">{item.title}</h3>
                <span className="text-[10px] text-slate-500 font-mono">Spatial Resolution: {item.resolution}</span>
              </div>
            </div>

            <div className="flex justify-between items-center text-[11px] text-slate-400 pt-2 border-t border-slate-800 font-mono">
              <span>{item.pairs} Image Pairs</span>
              <span>{item.size}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CalibratedDatasets;