import { useState } from 'react';

function WebRiskBadge({ webRiskResult }) {
  if (!webRiskResult) return null;

  const isSafe = webRiskResult.is_safe;
  return (
    <div className="flex items-center gap-2">
      <span
        className={`text-xs px-2 py-0.5 rounded-full border ${
          isSafe
            ? 'bg-green-500/10 text-green-400 border-green-500/30'
            : 'bg-red-500/10 text-red-400 border-red-500/30'
        }`}
      >
        {isSafe ? 'Safe' : 'Dangerous'}
      </span>
      {webRiskResult.threat_types && webRiskResult.threat_types.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {webRiskResult.threat_types.map((t) => (
            <span key={t} className="text-xs text-red-400 bg-red-500/10 px-1.5 py-0.5 rounded">
              {t}
            </span>
          ))}
        </div>
      )}
      {webRiskResult.source && (
        <span className="text-xs text-gray-500">({webRiskResult.source})</span>
      )}
    </div>
  );
}

function RedirectChain({ chain }) {
  if (!chain || chain.length === 0) return null;

  return (
    <div className="mt-2">
      <p className="text-xs text-gray-500 mb-1">리다이렉트 체인:</p>
      <div className="flex flex-col gap-1">
        {chain.map((url, i) => (
          <div key={i} className="flex items-center gap-1.5 text-xs">
            {i > 0 && (
              <svg className="w-3 h-3 text-gray-600 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
              </svg>
            )}
            <span className="text-gray-400 break-all font-mono">{url}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function UrlCard({ url }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="card-inner space-y-2">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <p className="text-xs text-gray-500 mb-0.5">원본 URL</p>
          <p className="text-sm text-cyan-400 break-all font-mono">{url.original_url}</p>
        </div>
        {url.is_shortened && (
          <span className="text-xs bg-amber-500/10 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded-full shrink-0">
            단축 URL
          </span>
        )}
      </div>

      {url.resolved_url && url.resolved_url !== url.original_url && (
        <div>
          <div className="flex items-center gap-1.5 text-gray-500">
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
            </svg>
            <span className="text-xs">최종 URL</span>
          </div>
          <p className="text-sm text-gray-300 break-all font-mono mt-0.5">{url.resolved_url}</p>
        </div>
      )}

      {url.resolve_status && (
        <p className="text-xs text-gray-500">
          상태: <span className="text-gray-400">{url.resolve_status}</span>
        </p>
      )}

      {url.category && (
        <p className="text-xs text-gray-500">
          카테고리: <span className="text-gray-400">{url.category}</span>
        </p>
      )}

      <WebRiskBadge webRiskResult={url.web_risk_result} />

      {url.risk_factors && url.risk_factors.length > 0 && (
        <div>
          <p className="text-xs text-gray-500 mb-1">위험 요인:</p>
          <div className="flex flex-wrap gap-1">
            {url.risk_factors.map((f, i) => (
              <span
                key={i}
                className="text-xs bg-red-500/10 text-red-400 border border-red-500/30 px-2 py-0.5 rounded"
              >
                {f}
              </span>
            ))}
          </div>
        </div>
      )}

      {url.redirect_chain && url.redirect_chain.length > 1 && (
        <>
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
          >
            {expanded ? '리다이렉트 체인 접기' : `리다이렉트 체인 보기 (${url.redirect_chain.length}단계)`}
          </button>
          {expanded && <RedirectChain chain={url.redirect_chain} />}
        </>
      )}
    </div>
  );
}

export default function UrlAnalysis({ urls = [] }) {
  if (urls.length === 0) return null;

  return (
    <div>
      <h4 className="text-sm font-medium text-gray-300 mb-2 flex items-center gap-2">
        <svg className="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
        </svg>
        URL 분석 ({urls.length}건)
      </h4>
      <div className="space-y-3">
        {urls.map((url, i) => (
          <UrlCard key={i} url={url} />
        ))}
      </div>
    </div>
  );
}
