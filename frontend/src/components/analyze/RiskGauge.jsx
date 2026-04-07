import { useEffect, useState } from 'react';

function getColor(score) {
  if (score <= 40) return '#22c55e';
  if (score <= 70) return '#f59e0b';
  return '#ef4444';
}

export default function RiskGauge({ score = 0 }) {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    const timeout = setTimeout(() => setAnimatedScore(score), 50);
    return () => clearTimeout(timeout);
  }, [score]);

  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const progress = (animatedScore / 100) * circumference;
  const offset = circumference - progress;
  const color = getColor(score);

  return (
    <div className="flex flex-col items-center">
      <div className="relative">
        <svg width="120" height="120" viewBox="0 0 120 120">
          <circle
            cx="60"
            cy="60"
            r={radius}
            fill="none"
            stroke="#374151"
            strokeWidth="8"
          />
          <circle
            cx="60"
            cy="60"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            style={{
              strokeDashoffset: offset,
              transition: 'stroke-dashoffset 1s ease-out, stroke 0.5s ease',
              transform: 'rotate(-90deg)',
              transformOrigin: '60px 60px',
            }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className="text-2xl font-bold"
            style={{ color }}
          >
            {score}
          </span>
          <span className="text-xs text-gray-400">점</span>
        </div>
      </div>
      <span className="text-xs text-gray-500 mt-1">위험도 점수</span>
    </div>
  );
}
