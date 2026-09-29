import React from 'react';
import { FileText, Code2, Copy } from 'lucide-react';

export const ApiReference = () => {
  const curlExample = `curl -X 'POST' \\
  'http://127.0.0.1:8000/image/match' \\
  -H 'accept: application/json' \\
  -H 'Content-Type: multipart/form-data' \\
  -F 'source_img=@source.png;type=image/png' \\
  -F 'source_xml=@source.xml;type=text/xml' \\
  -F 'ref_img=@ref.png;type=image/png' \\
  -F 'ref_xml=@ref.xml;type=text/xml'`;

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-800 pb-5">
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <FileText className="w-5 h-5 text-cyan-400" /> OpenAPI Documentation
        </h2>
        <p className="text-xs text-slate-400 mt-1">REST API schema details for integration into mission pipelines.</p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex items-center space-x-3 font-mono text-xs">
          <span className="px-2 py-1 bg-cyan-950 text-cyan-400 border border-cyan-800/50 font-bold rounded">POST</span>
          <span className="text-slate-200 font-semibold">/image/match</span>
        </div>

        <p className="text-xs text-slate-400">Accepts four payload components and returns registered base64 outputs alongside alignment quality statistics.</p>

        <div className="relative bg-slate-950 p-4 rounded-lg border border-slate-800 font-mono text-xs text-slate-300 overflow-x-auto">
          <button
            onClick={() => navigator.clipboard.writeText(curlExample)}
            className="absolute top-3 right-3 p-1.5 bg-slate-800 hover:bg-slate-700 rounded text-slate-400 hover:text-slate-200 transition"
            title="Copy cURL Command"
          >
            <Copy className="w-3.5 h-3.5" />
          </button>
          <pre>{curlExample}</pre>
        </div>
      </div>
    </div>
  );
};

export default ApiReference;