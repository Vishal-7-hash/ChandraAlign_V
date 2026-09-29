import React, { useRef } from 'react';
import { UploadCloud, CheckCircle2, FileCode, FileImage, X } from 'lucide-react';

export const FileUploaderTile = ({ label, accept, file, onFileSelect, onFileRemove, fileType }) => {
  const inputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      if (validateFileType(droppedFile)) {
        onFileSelect(droppedFile);
      }
    }
  };

  const validateFileType = (f) => {
    if (fileType === 'png' && !f.name.endsWith('.png')) {
      alert('Please upload a .png image file');
      return false;
    }
    if (fileType === 'xml' && !f.name.endsWith('.xml')) {
      alert('Please upload an .xml metadata file');
      return false;
    }
    return true;
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      if (validateFileType(selected)) {
        onFileSelect(selected);
      }
    }
  };

  return (
    <div className="flex flex-col">
      <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
        {fileType === 'png' ? <FileImage className="w-3.5 h-3.5 text-cyan-400" /> : <FileCode className="w-3.5 h-3.5 text-amber-400" />}
        {label}
      </span>

      {!file ? (
        <div
          onClick={() => inputRef.current?.click()}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          className="border-2 border-dashed border-slate-700/80 hover:border-cyan-500/80 bg-slate-900/50 hover:bg-slate-850/80 rounded-xl p-4 transition-all duration-200 cursor-pointer flex flex-col items-center justify-center text-center group min-h-27.5"
        >
          <UploadCloud className="w-6 h-6 text-slate-500 group-hover:text-cyan-400 transition-colors mb-1.5" />
          <span className="text-xs font-medium text-slate-300 group-hover:text-cyan-300">
            Click or drag & drop file
          </span>
          <span className="text-[10px] text-slate-500 mt-0.5">Supports {accept}</span>
          <input
            type="file"
            ref={inputRef}
            onChange={handleChange}
            accept={accept}
            className="hidden"
          />
        </div>
      ) : (
        <div className="bg-slate-900 border border-cyan-500/30 rounded-xl p-3 flex items-center justify-between shadow-md">
          <div className="flex items-center space-x-2.5 truncate">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <div className="truncate">
              <p className="text-xs font-medium text-slate-200 truncate">{file.name}</p>
              <p className="text-[10px] text-slate-500">{(file.size / 1024).toFixed(1)} KB</p>
            </div>
          </div>
          <button
            onClick={onFileRemove}
            className="p-1 hover:bg-slate-800 rounded-md text-slate-400 hover:text-red-400 transition shrink-0"
            title="Remove File"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUploaderTile;