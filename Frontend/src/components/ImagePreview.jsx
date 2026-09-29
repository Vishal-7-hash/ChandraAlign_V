import React, { useState } from 'react';
import { Maximize2, Download, Eye } from 'lucide-react';

export const ImagePreview = ({ title, base64String, badge, filename = "image.png" }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Normalize Base64 source string format
  const imageSrc = base64String?.startsWith('data:image') 
    ? base64String 
    : `data:image/png;base64,${base64String}`;

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = imageSrc;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <>
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg flex flex-col group hover:border-slate-700 transition-all">
        {/* Header */}
        <div className="px-4 py-3 bg-slate-850/80 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <h3 className="text-sm font-semibold text-slate-200">{title}</h3>
            {badge && (
              <span className="text-[10px] uppercase tracking-wider font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/50">
                {badge}
              </span>
            )}
          </div>
          <div className="flex items-center space-x-1 opacity-80 group-hover:opacity-100 transition-opacity">
            <button
              onClick={() => setIsModalOpen(true)}
              className="p-1.5 hover:bg-slate-700/60 rounded-md text-slate-400 hover:text-slate-200 transition"
              title="Expand Image"
            >
              <Maximize2 className="w-4 h-4" />
            </button>
            <button
              onClick={handleDownload}
              className="p-1.5 hover:bg-slate-700/60 rounded-md text-slate-400 hover:text-cyan-400 transition"
              title="Download Image"
            >
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Image Display */}
        <div className="relative flex-1 bg-slate-950/80 min-h-65 flex items-center justify-center p-2 overflow-hidden">
          {base64String ? (
            <img
              src={imageSrc}
              alt={title}
              className="max-h-95 w-auto object-contain rounded border border-slate-800/50"
            />
          ) : (
            <div className="text-center text-slate-600 text-xs flex flex-col items-center gap-2">
              <Eye className="w-6 h-6 opacity-40" />
              <span>No image output loaded</span>
            </div>
          )}
        </div>
      </div>

      {/* Fullscreen Lightbox Modal */}
      {isModalOpen && (
        <div 
          className="fixed inset-0 z-50 bg-black/90 backdrop-blur-md flex items-center justify-center p-6"
          onClick={() => setIsModalOpen(false)}
        >
          <div className="relative max-w-5xl max-h-[90vh] flex flex-col items-center">
            <img
              src={imageSrc}
              alt={title}
              className="max-h-[85vh] max-w-full object-contain rounded-lg shadow-2xl border border-slate-800"
            />
            <div className="mt-4 flex items-center gap-4">
              <span className="text-slate-300 font-medium text-sm">{title}</span>
              <button
                onClick={(e) => { e.stopPropagation(); handleDownload(); }}
                className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold rounded-md flex items-center gap-1.5 transition"
              >
                <Download className="w-3.5 h-3.5" /> Download
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ImagePreview;