import React, { useEffect, useState } from 'react';
import { History, Download, Terminal } from 'lucide-react';
import { downloadExecutionLog, getExecutionLogs } from '../services/api';

export const ExecutionLogs = () => {
  const [logs, setLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    getExecutionLogs()
      .then((data) => {
        if (isMounted) setLogs(data);
      })
      .catch((requestError) => {
        if (isMounted) {
          setError(requestError.response?.data?.detail || 'Unable to load execution logs.');
        }
      })
      .finally(() => {
        if (isMounted) setIsLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-800 pb-5 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <History className="w-5 h-5 text-cyan-400" /> Execution History & Audit Logs
          </h2>
          <p className="text-xs text-slate-400 mt-1">Review prior lunar registration jobs, performance metrics, and computational timing.</p>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        {error && <p className="p-4 text-xs text-red-400">{error}</p>}
        {isLoading && <p className="p-4 text-xs text-slate-400">Loading execution logs...</p>}
        {!isLoading && !error && logs.length === 0 && (
          <p className="p-4 text-xs text-slate-400">No pipeline executions recorded yet.</p>
        )}
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-slate-850 border-b border-slate-800 text-slate-400 font-mono">
              <th className="p-3">Job ID</th>
              <th className="p-3">Timestamp</th>
              <th className="p-3">Status</th>
              <th className="p-3">RMSE Error</th>
              <th className="p-3">Duration</th>
              <th className="p-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono text-slate-300">
            {logs.map((log) => (
              <tr key={log.id} className="hover:bg-slate-850/50">
                <td className="p-3 text-cyan-400 font-bold">{log.id}</td>
                <td className="p-3 text-slate-400">{log.timestamp}</td>
                <td className="p-3">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                    log.status === 'SUCCESS' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/40' : 'bg-red-950 text-red-400 border border-red-800/40'
                  }`}>
                    {log.status}
                  </span>
                </td>
                <td className="p-3">{log.rmse == null ? '—' : `${log.rmse.toFixed(4)} px`}</td>
                <td className="p-3">{`${log.time.toFixed(2)}s`}</td>
                <td className="p-3 text-right">
                  <button
                    className="p-1.5 hover:bg-slate-800 rounded text-slate-400 hover:text-cyan-400 transition"
                    title="Export Log File"
                    onClick={() => downloadExecutionLog(log.id)}
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ExecutionLogs;