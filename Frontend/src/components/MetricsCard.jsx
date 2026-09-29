import React from 'react';

export const MetricsCard = ({ title, value, unit = '', icon: Icon, description, trend }) => {
  return (
    <div className="bg-slate-900 border border-slate-800/80 rounded-xl p-4 shadow-lg hover:border-slate-700 transition-all duration-200">
      <div className="flex items-center justify-between text-slate-400 mb-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</span>
        {Icon && <Icon className="w-4 h-4 text-cyan-400" />}
      </div>
      <div className="flex items-baseline space-x-1">
        <span className="text-2xl font-bold font-mono text-slate-100">{value}</span>
        {unit && <span className="text-xs font-medium text-slate-400">{unit}</span>}
      </div>
      {description && <p className="text-xs text-slate-500 mt-1.5">{description}</p>}
    </div>
  );
};

export default MetricsCard;