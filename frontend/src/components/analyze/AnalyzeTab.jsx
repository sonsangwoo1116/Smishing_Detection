import { useState, useRef, useEffect } from 'react';
import MessageInput from './MessageInput';
import ResultCard from './ResultCard';
import { analyzeMessage } from '../../api/client';

export default function AnalyzeTab({ apiKeySet, onOpenSettings }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [meta, setMeta] = useState(null);
  const [error, setError] = useState(null);
  const abortRef = useRef(null);

  useEffect(() => {
    return () => {
      if (abortRef.current) {
        abortRef.current.abort();
      }
    };
  }, []);

  const handleAnalyze = async (message, sender) => {
    if (!apiKeySet) {
      onOpenSettings();
      return;
    }

    if (abortRef.current) {
      abortRef.current.abort();
    }

    const controller = new AbortController();
    abortRef.current = controller;

    setLoading(true);
    setError(null);
    setResult(null);
    setMeta(null);

    try {
      const response = await analyzeMessage(message, sender, controller.signal);
      if (response.success !== false) {
        setResult(response.data);
        setMeta(response.meta || null);
      } else {
        setError(response.message || '분석에 실패했습니다.');
      }
    } catch (err) {
      if (err.aborted) return;
      setError(err.message || '분석 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
      abortRef.current = null;
    }
  };

  return (
    <div className="space-y-6">
      {!apiKeySet && (
        <div className="card bg-amber-500/5 border-amber-500/30">
          <div className="flex items-center gap-3">
            <svg className="w-5 h-5 text-amber-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1121.75 8.25z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-amber-400">API Key가 설정되지 않았습니다</p>
              <p className="text-xs text-gray-400 mt-0.5">분석을 시작하려면 먼저 API Key를 설정해주세요.</p>
            </div>
            <button onClick={onOpenSettings} className="btn-primary text-sm ml-auto shrink-0">
              설정하기
            </button>
          </div>
        </div>
      )}

      <MessageInput onAnalyze={handleAnalyze} loading={loading} />

      {error && (
        <div className="card bg-red-500/5 border-red-500/30 animate-fade-in">
          <div className="flex items-start gap-3">
            <svg className="w-5 h-5 text-red-400 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-red-400">분석 오류</p>
              <p className="text-sm text-gray-400 mt-0.5">{error}</p>
            </div>
          </div>
        </div>
      )}

      {loading && (
        <div className="card animate-fade-in">
          <div className="flex flex-col items-center gap-3 py-8">
            <div className="w-10 h-10 border-2 border-gray-600 border-t-cyan-400 rounded-full animate-spin-slow" />
            <div className="text-center">
              <p className="text-sm text-gray-300">메시지 분석 중...</p>
              <p className="text-xs text-gray-500 mt-1">URL 추적, 키워드 분석, AI 판단을 수행합니다</p>
            </div>
          </div>
        </div>
      )}

      <ResultCard result={result} meta={meta} />
    </div>
  );
}
