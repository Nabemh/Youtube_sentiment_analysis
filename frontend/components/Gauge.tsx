
import React from 'react';

interface GaugeProps {
  value: number;
  label: string;
}

export const Gauge: React.FC<GaugeProps> = ({ value, label }) => {
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center relative">
      <svg className="w-40 h-40 transform -rotate-90">
        {/* Background Circle */}
        <circle
          cx="80"
          cy="80"
          r={radius}
          stroke="currentColor"
          strokeWidth="10"
          fill="transparent"
          className="text-slate-800"
        />
        {/* Progress Circle */}
        <circle
          cx="80"
          cy="80"
          r={radius}
          stroke="currentColor"
          strokeWidth="10"
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="text-blue-500 transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center rotate-0">
        <span className="text-4xl font-bold">{value.toFixed(1)}</span>
        <span className="text-sm font-medium text-slate-400 uppercase tracking-wider">{label}</span>
      </div>
    </div>
  );
};
