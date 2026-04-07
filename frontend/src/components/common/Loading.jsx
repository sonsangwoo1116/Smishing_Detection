export default function Loading({ text = '로딩 중...', size = 'md' }) {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-2',
    lg: 'w-12 h-12 border-3',
  };

  return (
    <div className="flex flex-col items-center justify-center gap-3 py-8">
      <div
        className={`${sizeClasses[size]} border-gray-600 border-t-cyan-400 rounded-full animate-spin-slow`}
        role="status"
        aria-label={text}
      />
      <span className="text-sm text-gray-400">{text}</span>
    </div>
  );
}
