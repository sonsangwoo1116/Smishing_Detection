import { useState, useEffect, useCallback } from 'react';
import { getHealth } from '../../api/client';
import Loading from '../common/Loading';

const DEP_CONFIG = {
  database: { label: '데이터베이스', connectedLabel: 'connected' },
  redis: { label: 'Redis 캐시', connectedLabel: 'connected' },
  openai_api: { label: 'OpenAI API', connectedLabel: 'configured' },
  web_risk_api: { label: 'Web Risk API', connectedLabel: 'configured' },
};

function formatUptime(seconds) {
  if (!seconds && seconds !== 0) return '-';
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  const parts = [];
  if (d > 0) parts.push(`${d}일`);
  if (h > 0) parts.push(`${h}시간`);
  if (m > 0) parts.push(`${m}분`);
  parts.push(`${s}초`);
  return parts.join(' ');
}

function StatusIcon({ ok }) {
  if (ok) {
    return (
      <div className="w-8 h-8 rounded-lg bg-green-500/10 flex items-center justify-center">
        <svg className="w-4 h-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
        </svg>
      </div>
    );
  }
  return (
    <div className="w-8 h-8 rounded-lg bg-red-500/10 flex items-center justify-center">
      <svg className="w-4 h-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </div>
  );
}

export default function StatusTab() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchHealth = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getHealth();
      setHealth(response);
    } catch (err) {
      setError(err.message || '서버 상태를 확인할 수 없습니다.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
  }, [fetchHealth]);

  if (loading) return <Loading text="서버 상태 확인 중..." />;

  if (error) {
    return (
      <div className="card">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center shrink-0">
            <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
          </div>
          <div>
            <p className="text-sm font-medium text-red-400">서버 연결 실패</p>
            <p className="text-sm text-gray-400 mt-1">{error}</p>
            <button onClick={fetchHealth} className="btn-primary text-sm mt-3">
              다시 시도
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!health) return null;

  const isHealthy = health.status === 'healthy';
  const deps = health.dependencies || {};

  return (
    <div className="space-y-4">
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-100">서버 상태</h2>
          <button onClick={fetchHealth} className="btn-ghost text-xs flex items-center gap-1.5">
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182" />
            </svg>
            새로고침
          </button>
        </div>

        <div className="card-inner flex items-center gap-4 mb-4">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
            isHealthy ? 'bg-green-500/10' : 'bg-amber-500/10'
          }`}>
            {isHealthy ? (
              <svg className="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            ) : (
              <svg className="w-6 h-6 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
              </svg>
            )}
          </div>
          <div>
            <p className={`text-lg font-bold ${isHealthy ? 'text-green-400' : 'text-amber-400'}`}>
              {isHealthy ? '정상 운영 중' : '제한된 운영 중'}
            </p>
            <p className="text-xs text-gray-500">
              {health.version && `v${health.version}`}
              {health.uptime_seconds != null && ` | 업타임: ${formatUptime(health.uptime_seconds)}`}
            </p>
          </div>
        </div>

        <h3 className="text-sm font-medium text-gray-400 mb-3">의존성 상태</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {Object.entries(DEP_CONFIG).map(([key, config]) => {
            const value = deps[key];
            const isOk = value === config.connectedLabel;
            return (
              <div key={key} className="card-inner flex items-center gap-3">
                <StatusIcon ok={isOk} />
                <div>
                  <p className="text-sm text-gray-300">{config.label}</p>
                  <p className={`text-xs ${isOk ? 'text-green-400' : 'text-red-400'}`}>
                    {value || '알 수 없음'}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {health.cache_stats && (
          <div className="mt-4 pt-4 border-t border-gray-700">
            <h3 className="text-sm font-medium text-gray-400 mb-2">캐시 통계</h3>
            <div className="card-inner">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">URL 캐시 크기</span>
                <span className="text-sm text-cyan-400 font-mono">
                  {health.cache_stats.url_cache_size ?? '-'}
                </span>
              </div>
            </div>
          </div>
        )}

        {health.timestamp && (
          <p className="text-xs text-gray-600 mt-4">
            확인 시각: {new Date(health.timestamp).toLocaleString('ko-KR')}
          </p>
        )}
      </div>
    </div>
  );
}
