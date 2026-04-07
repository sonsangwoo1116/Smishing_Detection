const CATEGORY_COLORS = {
  delivery: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
  finance: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
  government: 'bg-red-500/10 text-red-400 border-red-500/30',
  family: 'bg-pink-500/10 text-pink-400 border-pink-500/30',
  urgency: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
  url: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
};

const DEFAULT_COLOR = 'bg-gray-700/50 text-gray-300 border-gray-600';

export default function KeywordTags({ keywords = [], patterns = [], categories = [] }) {
  if (keywords.length === 0 && patterns.length === 0 && categories.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      {categories.length > 0 && (
        <div>
          <h4 className="text-xs font-medium text-gray-500 mb-1.5">패턴 카테고리</h4>
          <div className="flex flex-wrap gap-1.5">
            {categories.map((cat) => (
              <span
                key={cat}
                className={`text-xs px-2.5 py-1 rounded-full border ${CATEGORY_COLORS[cat] || DEFAULT_COLOR}`}
              >
                {cat}
              </span>
            ))}
          </div>
        </div>
      )}

      {keywords.length > 0 && (
        <div>
          <h4 className="text-xs font-medium text-gray-500 mb-1.5">탐지 키워드</h4>
          <div className="flex flex-wrap gap-1.5">
            {keywords.map((kw) => (
              <span
                key={kw}
                className="text-xs px-2.5 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30"
              >
                {kw}
              </span>
            ))}
          </div>
        </div>
      )}

      {patterns.length > 0 && (
        <div>
          <h4 className="text-xs font-medium text-gray-500 mb-1.5">탐지 패턴</h4>
          <div className="flex flex-wrap gap-1.5">
            {patterns.map((p) => (
              <span
                key={p}
                className={`text-xs px-2.5 py-1 rounded-full border ${DEFAULT_COLOR}`}
              >
                {p}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
