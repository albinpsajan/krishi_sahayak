/** Top header: brand, language toggle, logout. */
export default function Header({ lang, onToggleLang, onLogout }) {
  return (
    <header className="app-header">
      <div className="brand-wrapper">
        <div className="brand-icon">🌱</div>
        <div>
          <div className="brand-title">KrishiSahayak AI</div>
          <div className="brand-subtitle">AI-Assisted, Officer-Verified Agricultural Administration Platform</div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <button
          onClick={onToggleLang}
          className="ks-btn ks-btn-outline"
          style={{ color: '#fff', borderColor: 'rgba(255,255,255,0.3)', fontSize: '0.82rem' }}
        >
          🌐 Language: {lang === 'en' ? 'English' : 'മലയാളം (Malayalam)'}
        </button>

        <button onClick={onLogout} className="ks-btn ks-btn-gold" style={{ fontSize: '0.82rem' }}>
          🚪 Logout
        </button>
      </div>
    </header>
  );
}
