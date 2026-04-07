export default function DegradedBanner({ degradedServices = [], degradedReason }) {
  return (
    <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg px-4 py-3 flex items-start gap-3">
      <svg
        className="w-5 h-5 text-amber-500 mt-0.5 shrink-0"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={2}
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
        />
      </svg>
      <div>
        <p className="text-sm font-medium text-amber-400">
          일부 분석 서비스가 제한된 상태입니다
        </p>
        <p className="text-xs text-amber-500/80 mt-0.5">
          {degradedReason || '규칙 기반 fallback이 적용되었습니다.'}
        </p>
        {degradedServices.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2">
            {degradedServices.map((service) => (
              <span
                key={service}
                className="text-xs bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded"
              >
                {service}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
