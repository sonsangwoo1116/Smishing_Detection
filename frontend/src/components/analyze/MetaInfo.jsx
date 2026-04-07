export default function MetaInfo({ meta, analyzedAt }) {
  if (!meta && !analyzedAt) return null;

  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500 pt-3 border-t border-gray-700">
      {analyzedAt && (
        <span>
          분석 시각: {new Date(analyzedAt).toLocaleString('ko-KR')}
        </span>
      )}
      {meta?.processing_time_ms != null && (
        <span>처리 시간: {meta.processing_time_ms}ms</span>
      )}
      {meta?.model && (
        <span>모델: {meta.model}</span>
      )}
      {meta?.cache_hit != null && (
        <span>캐시: {meta.cache_hit ? '적중' : '미적중'}</span>
      )}
    </div>
  );
}
