import { useState } from 'react';
import { getApiKey, setApiKey } from '../../api/client';

export default function ApiKeyModal({ onClose, onSave }) {
  const [key, setKey] = useState(getApiKey());
  const [showKey, setShowKey] = useState(false);

  const handleSave = () => {
    setApiKey(key.trim());
    onSave();
  };

  const handleRemove = () => {
    setApiKey('');
    setKey('');
    onSave();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      role="dialog"
      aria-modal="true"
      aria-label="API Key 설정"
    >
      <div className="card w-full max-w-md mx-4 animate-slide-up">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-100">API Key 설정</h2>
          <button
            onClick={onClose}
            className="btn-ghost p-1"
            aria-label="닫기"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <p className="text-sm text-gray-400 mb-4">
          스미싱 분석 API를 사용하려면 API Key가 필요합니다.
          키는 이 브라우저 탭에서만 유지됩니다 (sessionStorage).
        </p>

        <div className="mb-4">
          <label htmlFor="api-key-input" className="block text-sm font-medium text-gray-300 mb-2">
            API Key
          </label>
          <div className="relative">
            <input
              id="api-key-input"
              type={showKey ? 'text' : 'password'}
              value={key}
              onChange={(e) => setKey(e.target.value)}
              placeholder="API Key를 입력하세요"
              className="input-field pr-10"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter' && key.trim()) handleSave();
              }}
            />
            <button
              type="button"
              onClick={() => setShowKey(!showKey)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
              aria-label={showKey ? '키 숨기기' : '키 보기'}
            >
              {showKey ? (
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              )}
            </button>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleSave}
            disabled={!key.trim()}
            className="btn-primary flex-1"
          >
            저장
          </button>
          {getApiKey() && (
            <button
              onClick={handleRemove}
              className="px-4 py-2.5 rounded-lg text-red-400 hover:bg-red-500/10 transition-colors text-sm"
            >
              삭제
            </button>
          )}
          <button
            onClick={onClose}
            className="px-4 py-2.5 rounded-lg text-gray-400 hover:bg-gray-800 transition-colors text-sm"
          >
            취소
          </button>
        </div>
      </div>
    </div>
  );
}
