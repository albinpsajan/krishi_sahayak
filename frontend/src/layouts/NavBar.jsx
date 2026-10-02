/** Main navigation: role-aware tab links with unread notification badge. */
export default function NavBar({ isFarmer, isOfficer, currentTab, setCurrentTab, unreadCount }) {
  const link = (tab) => `nav-link ${currentTab === tab ? 'active' : ''}`;

  return (
    <nav className="nav-bar">
      <div className="nav-links">
        {isFarmer ? (
          <>
            <button className={link('home')} onClick={() => setCurrentTab('home')}>🏠 Home Dashboard</button>
            <button className={link('cases')} onClick={() => setCurrentTab('cases')}>🌾 My Crop Cases</button>
            <button className={link('subsidies')} onClick={() => setCurrentTab('subsidies')}>📜 Subsidies & Schemes</button>
            <button className={link('notifications')} onClick={() => setCurrentTab('notifications')}>
              🔔 Notifications ({unreadCount})
            </button>
            <button className={link('profile')} onClick={() => setCurrentTab('profile')}>👤 Profile</button>
            <button className={link('audit')} onClick={() => setCurrentTab('audit')}>🔒 Audit Ledger</button>
          </>
        ) : (
          <>
            <button className={link('dashboard')} onClick={() => setCurrentTab('dashboard')}>📊 Officer Dashboard</button>
            <button className={link('cases')} onClick={() => setCurrentTab('cases')}>🔎 Case Reviews</button>
            <button className={link('subsidies')} onClick={() => setCurrentTab('subsidies')}>⚖️ Subsidy Review (SubsidyChain)</button>
            <button className={link('notifications')} onClick={() => setCurrentTab('notifications')}>
              🔔 Alerts ({unreadCount})
            </button>
            <button className={link('profile')} onClick={() => setCurrentTab('profile')}>👤 Officer Profile</button>
            <button className={link('audit')} onClick={() => setCurrentTab('audit')}>🔒 Tamper-Evident Audit</button>
          </>
        )}
      </div>

      <div className="user-badge">
        <span>{isFarmer || isOfficer ? '' : ''}</span>
      </div>
    </nav>
  );
}
