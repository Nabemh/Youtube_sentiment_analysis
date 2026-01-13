
import React from 'react';
import { SentimentComponents } from '../types';

interface MetricsGridProps {
  components: SentimentComponents;
}

export const MetricsGrid: React.FC<MetricsGridProps> = ({ components }) => {
  const items = [
    { label: 'Transcript Mean', value: components.transcript_mean, color: 'bg-emerald-500' },
    { label: 'Comments Mean', value: components.comments_mean, color: 'bg-indigo-500' },
    { label: 'Engagement Rate', value: components.engagement, color: 'bg-amber-500' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full">
      {items.map((item) => (
        <div key={item.label} className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
          <p className="text-slate-400 text-xs font-semibold uppercase mb-2">{item.label}</p>
          <div className="flex items-end gap-2">
            <span className="text-2xl font-bold">{item.value.toFixed(3)}</span>
          </div>
          <div className="mt-3 w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
            <div 
              className={`${item.color} h-full transition-all duration-1000 ease-out`}
              style={{ width: `${item.value * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
};
