
import React, { useState } from 'react';
import { analyzeVideoSentiment } from './services/apiService';
import { SentimentData, AnalysisStatus } from './types';
import { Gauge } from './components/Gauge';
import { MetricsGrid } from './components/MetricsGrid';

const App: React.FC = () => {
  const [url, setUrl] = useState('');
  const [status, setStatus] = useState<AnalysisStatus>(AnalysisStatus.IDLE);
  const [data, setData] = useState<SentimentData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setStatus(AnalysisStatus.LOADING);
    setError(null);
    setData(null);

    try {
      const result = await analyzeVideoSentiment(url);
      setData(result);
      setStatus(AnalysisStatus.SUCCESS);
    } catch (err) {
      console.error(err);
      setError('Failed to process video. Please check the URL and try again.');
      setStatus(AnalysisStatus.ERROR);
    }
  };

  return (
    <div className="min-h-screen p-4 md:p-8 flex flex-col items-center max-w-5xl mx-auto">
      {/* Header */}
      <header className="w-full text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-extrabold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent mb-4">
          Sentiview ML
        </h1>
        <p className="text-slate-400 text-lg">
          Deep learning sentiment inference for video content
        </p>
      </header>

      {/* Input Section */}
      <div className="w-full max-w-2xl bg-slate-800/80 backdrop-blur-md rounded-2xl p-6 shadow-2xl border border-slate-700 mb-8">
        <form onSubmit={handleSubmit} className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter YouTube URL or Video ID (e.g., BU9gKr1miS8)"
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50 placeholder:text-slate-600 transition-all"
            />
          </div>
          <button
            type="submit"
            disabled={status === AnalysisStatus.LOADING}
            className="bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 text-white font-bold py-3 px-8 rounded-xl transition-all shadow-lg shadow-blue-900/20 active:scale-95 flex items-center justify-center gap-2"
          >
            {status === AnalysisStatus.LOADING ? (
              <>
                <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                Inferring...
              </>
            ) : 'Analyze'}
          </button>
        </form>
      </div>

      {/* Results Section */}
      {status === AnalysisStatus.ERROR && (
        <div className="w-full max-w-2xl bg-red-900/20 border border-red-500/50 rounded-xl p-4 text-red-400 text-center animate-pulse">
          {error}
        </div>
      )}

      {status === AnalysisStatus.SUCCESS && data && (
        <div className="w-full space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Primary Analysis Card */}
            <div className="lg:col-span-1 bg-slate-800/80 backdrop-blur-md rounded-2xl p-8 border border-slate-700 shadow-xl flex flex-col items-center">
              <h2 className="text-xl font-semibold mb-6 text-slate-300">Overall Score</h2>
              <Gauge value={data.score} label={data.label} />
              
              <div className="mt-8 pt-8 border-t border-slate-700 w-full">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-slate-400 text-sm">Model Accuracy</span>
                  <span className="text-emerald-400 font-mono text-sm">{data.model_accuracy.toFixed(2)}%</span>
                </div>
                <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
                  <div 
                    className="bg-emerald-500 h-full transition-all duration-1000"
                    style={{ width: `${data.model_accuracy}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Video & Detailed Metrics */}
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-slate-800/80 backdrop-blur-md rounded-2xl p-6 border border-slate-700 shadow-xl">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center border border-blue-500/20">
                    <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-xl font-bold">Analysis Results</h2>
                    <p className="text-slate-400 font-mono text-sm">ID: {data.video_id}</p>
                  </div>
                </div>

                <MetricsGrid components={data.components} />
                
                <div className="mt-8 bg-slate-900/50 rounded-xl p-4 font-mono text-xs text-slate-400 border border-slate-800 overflow-x-auto">
                  <pre>{`{
  "video_id": "${data.video_id}",
  "score": ${data.score.toFixed(1)},
  "label": "${data.label}",
  "components": {
    "transcript_mean": ${data.components.transcript_mean.toFixed(3)},
    "comments_mean": ${data.components.comments_mean.toFixed(3)},
    "engagement": ${data.components.engagement.toFixed(3)}
  },
  "model_accuracy": ${data.model_accuracy.toFixed(2)}
}`}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {status === AnalysisStatus.IDLE && (
        <div className="flex flex-col items-center justify-center py-20 opacity-50">
          <div className="w-24 h-24 bg-slate-800 rounded-full flex items-center justify-center mb-6">
             <svg className="w-12 h-12 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <p className="text-slate-500 text-center max-w-xs">
            Enter a YouTube video URL above to start the sentiment analysis inference process.
          </p>
        </div>
      )}

      {/* Footer */}
      <footer className="mt-auto py-8 text-slate-600 text-sm">
        Viewer ML &copy; {new Date().getFullYear()} &bull; Powered by FastAPI backend
      </footer>
    </div>
  );
};

export default App;
