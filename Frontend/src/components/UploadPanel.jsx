import React from 'react';
import FileUploaderTile from './FileUploaderTile';

export const UploadPanel = ({ files, setFiles }) => {
  const updateFile = (key, file) => {
    setFiles((prev) => ({ ...prev, [key]: file }));
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-xl space-y-5">
      <div className="border-b border-slate-800 pb-3">
        <h2 className="text-sm font-semibold text-slate-100 uppercase tracking-wide flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400 inline-block"></span>
          Input Dataset Pairing
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Upload Source and Reference image pairs along with corresponding mission XML metadata.
        </p>
      </div>

      {/* Grid for Upload Modules */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Source Section */}
        <div className="space-y-3 bg-slate-950/50 p-3.5 rounded-lg border border-slate-800/60">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider border-b border-slate-800/80 pb-1.5">
            Source Image Target
          </h3>
          <FileUploaderTile
            label="Source Image (.png)"
            accept=".png"
            fileType="png"
            file={files.sourceImg}
            onFileSelect={(file) => updateFile('sourceImg', file)}
            onFileRemove={() => updateFile('sourceImg', null)}
          />
          <FileUploaderTile
            label="Source Metadata (.xml)"
            accept=".xml"
            fileType="xml"
            file={files.sourceXml}
            onFileSelect={(file) => updateFile('sourceXml', file)}
            onFileRemove={() => updateFile('sourceXml', null)}
          />
        </div>

        {/* Reference Section */}
        <div className="space-y-3 bg-slate-950/50 p-3.5 rounded-lg border border-slate-800/60">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider border-b border-slate-800/80 pb-1.5">
            Reference Frame
          </h3>
          <FileUploaderTile
            label="Reference Image (.png)"
            accept=".png"
            fileType="png"
            file={files.refImg}
            onFileSelect={(file) => updateFile('refImg', file)}
            onFileRemove={() => updateFile('refImg', null)}
          />
          <FileUploaderTile
            label="Reference Metadata (.xml)"
            accept=".xml"
            fileType="xml"
            file={files.refXml}
            onFileSelect={(file) => updateFile('refXml', file)}
            onFileRemove={() => updateFile('refXml', null)}
          />
        </div>
      </div>
    </div>
  );
};

export default UploadPanel;