import { useState, useEffect } from 'react';
import { useUiStore } from '@/store/uiStore';
import { apiGet } from '@/api/client';

interface HeaderProps {
  trayOpen: boolean;
  onToggleTray: () => void;
}

export function Header({ trayOpen, onToggleTray }: HeaderProps) {
  const activeView = useUiStore((s) => s.activeView);
  const setActiveView = useUiStore((s) => s.setActiveView);
  const [version, setVersion] = useState('');

  useEffect(() => {
    apiGet<{ config: { version?: string } }>('/api/config')
      .then((data) => setVersion(data.config?.version ?? ''))
      .catch(() => {});
  }, []);

  const tabs = [
    { key: 'workspace', label: 'Research' },
    { key: 'skills', label: 'Skills' },
    { key: 'docs', label: 'Docs' },
  ] as const;

  return (
    <header className="app-header">
      <div className="header-left">
        <button
          className={`header-tray-toggle${trayOpen ? ' is-open' : ''}`}
          onClick={onToggleTray}
          title={trayOpen ? 'Hide sessions' : 'Show sessions'}
          aria-label={trayOpen ? 'Hide session tray' : 'Show session tray'}
        >
          {/* Sidebar panel icon — cleaner than hamburger/X */}
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <line x1="9" y1="3" x2="9" y2="21" />
          </svg>
        </button>
        <div className="header-brand">
          <img src="/logo-claw.png" alt="" className="header-logo" />
          <span className="header-title">EurekaLab</span>
          {version && <span className="version-pill">v{version}</span>}
        </div>
      </div>

      <nav className="header-tabs" role="tablist" aria-label="Main navigation">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            className={`header-tab${activeView === tab.key ? ' is-active' : ''}`}
            role="tab"
            aria-selected={activeView === tab.key}
            onClick={() => setActiveView(tab.key as typeof activeView)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <div className="header-right">
        <button
          className={`header-icon-btn${activeView === 'systems' ? ' is-active' : ''}`}
          onClick={() => setActiveView('systems')}
          title="Settings"
          aria-label="Settings"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
        </button>
      </div>
    </header>
  );
}
