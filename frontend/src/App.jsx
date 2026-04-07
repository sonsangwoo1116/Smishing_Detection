import { useState, useEffect, useCallback } from 'react';
import Header from './components/layout/Header';
import TabNav from './components/layout/TabNav';
import AnalyzeTab from './components/analyze/AnalyzeTab';
import HistoryTab from './components/history/HistoryTab';
import StatusTab from './components/status/StatusTab';
import ApiKeyModal from './components/settings/ApiKeyModal';
import { hasApiKey } from './api/client';

const TABS = [
  { id: 'analyze', label: '분석' },
  { id: 'history', label: '이력' },
  { id: 'status', label: '상태' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('analyze');
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);
  const [apiKeySet, setApiKeySet] = useState(hasApiKey());

  useEffect(() => {
    if (!hasApiKey()) {
      setShowApiKeyModal(true);
    }
  }, []);

  const handleApiKeySaved = useCallback(() => {
    setApiKeySet(hasApiKey());
    setShowApiKeyModal(false);
  }, []);

  const handleOpenSettings = useCallback(() => {
    setShowApiKeyModal(true);
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <Header
        onOpenSettings={handleOpenSettings}
        apiKeySet={apiKeySet}
      />

      <TabNav
        tabs={TABS}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      <main className="flex-1 max-w-5xl w-full mx-auto px-4 py-6">
        {activeTab === 'analyze' && (
          <AnalyzeTab apiKeySet={apiKeySet} onOpenSettings={handleOpenSettings} />
        )}
        {activeTab === 'history' && <HistoryTab />}
        {activeTab === 'status' && <StatusTab />}
      </main>

      <footer className="text-center text-gray-600 text-xs py-4 border-t border-gray-800">
        스미싱 탐지 AI Agent &middot; Powered by LLM + Web Risk API
      </footer>

      {showApiKeyModal && (
        <ApiKeyModal
          onClose={() => setShowApiKeyModal(false)}
          onSave={handleApiKeySaved}
        />
      )}
    </div>
  );
}
