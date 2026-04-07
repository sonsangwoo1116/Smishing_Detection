import { useState, useEffect } from 'react';
import { getHistoryDetail } from '../../api/client';
import ResultCard from '../analyze/ResultCard';
import Loading from '../common/Loading';

export default function HistoryDetail({ id, onClose }) {
  const [data, setData] = useState(null);
  const [meta, setMeta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchDetail() {
      setLoading(true);
      setError(null);
      try {
        const response = await getHistoryDetail(id);
        if (!cancelled) {
          setData(response.data);
          setMeta(response.meta || null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || '상세 정보를 불러올 수 없습니다.');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchDetail();
    return () => { cancelled = true; };
  }, [id]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/60 backdrop-blur-sm animate-fade-in overflow-y-auto py-8"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      role="dialog"
      aria-modal="true"
      aria-label="분석 상세 결과"
    >
      <div className="w-full max-w-3xl mx-4 animate-slide-up">
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-gray-100">분석 상세 결과</h2>
            <button onClick={onClose} className="btn-ghost p-1" aria-label="닫기">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {loading && <Loading text="상세 정보 로딩 중..." />}

          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 text-sm text-red-400">
              {error}
            </div>
          )}

          {data && <ResultCard result={data} meta={meta} />}
        </div>
      </div>
    </div>
  );
}
