import { useState, useEffect, useCallback } from 'react';
import { getHistory } from '../../api/client';
import RiskBadge from '../analyze/RiskBadge';
import HistoryDetail from './HistoryDetail';
import Loading from '../common/Loading';

const FILTER_OPTIONS = [
  { value: 'ALL', label: '전체' },
  { value: 'HIGH', label: '고위험' },
  { value: 'WARNING', label: '주의' },
  { value: 'NORMAL', label: '정상' },
];

export default function HistoryTab() {
  const [items, setItems] = useState([]);
  const [pagination, setPagination] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [selectedId, setSelectedId] = useState(null);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getHistory({
        page,
        size: 20,
        riskLevel: riskFilter,
        startDate: startDate || undefined,
        endDate: endDate || undefined,
      });
      setItems(response.data?.items || []);
      setPagination(response.data?.pagination || null);
    } catch (err) {
      setError(err.message || '이력을 불러올 수 없습니다.');
    } finally {
      setLoading(false);
    }
  }, [page, riskFilter, startDate, endDate]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const handleFilterChange = (value) => {
    setRiskFilter(value);
    setPage(1);
  };

  const totalPages = pagination?.total_pages || 1;

  return (
    <div className="space-y-4">
      <div className="card">
        <div className="flex flex-col sm:flex-row sm:items-center gap-3 mb-4">
          <h2 className="text-lg font-bold text-gray-100">분석 이력</h2>
          <div className="flex flex-wrap gap-2 sm:ml-auto">
            {FILTER_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                onClick={() => handleFilterChange(opt.value)}
                className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
                  riskFilter === opt.value
                    ? 'border-cyan-500 text-cyan-400 bg-cyan-500/10'
                    : 'border-gray-700 text-gray-400 hover:border-gray-500'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 mb-4">
          <div className="flex items-center gap-2">
            <label htmlFor="start-date" className="text-xs text-gray-500 shrink-0">시작일</label>
            <input
              id="start-date"
              type="date"
              value={startDate}
              onChange={(e) => { setStartDate(e.target.value); setPage(1); }}
              className="input-field text-xs py-1.5 px-2"
            />
          </div>
          <div className="flex items-center gap-2">
            <label htmlFor="end-date" className="text-xs text-gray-500 shrink-0">종료일</label>
            <input
              id="end-date"
              type="date"
              value={endDate}
              onChange={(e) => { setEndDate(e.target.value); setPage(1); }}
              className="input-field text-xs py-1.5 px-2"
            />
          </div>
          {(startDate || endDate) && (
            <button
              onClick={() => { setStartDate(''); setEndDate(''); setPage(1); }}
              className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
            >
              초기화
            </button>
          )}
        </div>

        {loading && <Loading text="이력 로딩 중..." />}

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 text-sm text-red-400">
            {error}
          </div>
        )}

        {!loading && !error && items.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <svg className="w-12 h-12 mx-auto mb-3 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
            <p className="text-sm">분석 이력이 없습니다</p>
          </div>
        )}

        {!loading && !error && items.length > 0 && (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-700 text-gray-500">
                    <th className="text-left py-2 px-3 font-medium">위험도</th>
                    <th className="text-left py-2 px-3 font-medium">점수</th>
                    <th className="text-left py-2 px-3 font-medium hidden sm:table-cell">메시지</th>
                    <th className="text-left py-2 px-3 font-medium hidden md:table-cell">URL</th>
                    <th className="text-left py-2 px-3 font-medium">시각</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((item) => (
                    <tr
                      key={item.id}
                      onClick={() => setSelectedId(item.id)}
                      className="border-b border-gray-800 hover:bg-gray-800/50 cursor-pointer transition-colors"
                    >
                      <td className="py-3 px-3">
                        <RiskBadge level={item.risk_level} size="sm" />
                      </td>
                      <td className="py-3 px-3">
                        <span className={`font-mono font-medium ${
                          item.risk_score > 70 ? 'text-red-400' :
                          item.risk_score > 40 ? 'text-amber-400' : 'text-green-400'
                        }`}>
                          {item.risk_score}
                        </span>
                      </td>
                      <td className="py-3 px-3 hidden sm:table-cell">
                        <p className="text-gray-300 truncate max-w-xs">
                          {item.message_preview || item.summary}
                        </p>
                      </td>
                      <td className="py-3 px-3 hidden md:table-cell text-gray-500">
                        {item.urls_count || 0}건
                      </td>
                      <td className="py-3 px-3 text-xs text-gray-500 whitespace-nowrap">
                        {new Date(item.analyzed_at).toLocaleString('ko-KR', {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 pt-4">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page <= 1}
                  className="btn-ghost text-sm disabled:opacity-30"
                >
                  이전
                </button>
                {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                  let pageNum;
                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (page <= 3) {
                    pageNum = i + 1;
                  } else if (page >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = page - 2 + i;
                  }
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setPage(pageNum)}
                      className={`w-8 h-8 rounded-lg text-sm transition-colors ${
                        page === pageNum
                          ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                          : 'text-gray-400 hover:bg-gray-800'
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                  className="btn-ghost text-sm disabled:opacity-30"
                >
                  다음
                </button>
              </div>
            )}

            {pagination && (
              <p className="text-center text-xs text-gray-600 mt-2">
                전체 {pagination.total_items}건 중 {(page - 1) * 20 + 1}-{Math.min(page * 20, pagination.total_items)}건
              </p>
            )}
          </>
        )}
      </div>

      {selectedId && (
        <HistoryDetail
          id={selectedId}
          onClose={() => setSelectedId(null)}
        />
      )}
    </div>
  );
}
