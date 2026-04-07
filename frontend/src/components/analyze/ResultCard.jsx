import RiskBadge from './RiskBadge';
import RiskGauge from './RiskGauge';
import DegradedBanner from './DegradedBanner';
import UrlAnalysis from './UrlAnalysis';
import KeywordTags from './KeywordTags';
import ExplanationSection from './ExplanationSection';
import MetaInfo from './MetaInfo';

export default function ResultCard({ result, meta }) {
  if (!result) return null;

  const {
    risk_level,
    risk_score,
    summary,
    explanation,
    urls,
    text_analysis,
    patterns_detected,
    degraded,
    degraded_services,
    degraded_reason,
    analyzed_at,
  } = result;

  return (
    <div className="card space-y-5 animate-slide-up">
      {degraded && (
        <DegradedBanner
          degradedServices={degraded_services}
          degradedReason={degraded_reason}
        />
      )}

      <div className="flex flex-col sm:flex-row items-center gap-5">
        <RiskGauge score={risk_score} />
        <div className="flex-1 text-center sm:text-left space-y-2">
          <RiskBadge level={risk_level} />
          <p className="text-gray-200 leading-relaxed">{summary}</p>
        </div>
      </div>

      {text_analysis && (
        <div className="space-y-2">
          {text_analysis.urgency_score != null && (
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-500">긴급성 점수</span>
                <span className="text-xs text-gray-400">{text_analysis.urgency_score}/100</span>
              </div>
              <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${
                    text_analysis.urgency_score > 70
                      ? 'bg-red-500'
                      : text_analysis.urgency_score > 40
                      ? 'bg-amber-500'
                      : 'bg-green-500'
                  }`}
                  style={{ width: `${text_analysis.urgency_score}%` }}
                />
              </div>
            </div>
          )}

          <KeywordTags
            keywords={text_analysis.detected_keywords}
            patterns={patterns_detected}
            categories={text_analysis.pattern_categories}
          />
        </div>
      )}

      <UrlAnalysis urls={urls} />

      <ExplanationSection explanation={explanation} />

      <MetaInfo meta={meta} analyzedAt={analyzed_at} />
    </div>
  );
}
