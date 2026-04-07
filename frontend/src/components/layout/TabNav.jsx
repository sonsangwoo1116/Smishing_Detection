export default function TabNav({ tabs, activeTab, onTabChange }) {
  return (
    <nav className="bg-gray-900 border-b border-gray-700" role="tablist">
      <div className="max-w-5xl mx-auto px-4">
        <div className="flex gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              role="tab"
              aria-selected={activeTab === tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`
                px-5 py-3 text-sm font-medium transition-colors duration-200 border-b-2
                focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-inset
                ${
                  activeTab === tab.id
                    ? 'text-cyan-400 border-cyan-400'
                    : 'text-gray-400 border-transparent hover:text-gray-200 hover:border-gray-600'
                }
              `}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
    </nav>
  );
}
