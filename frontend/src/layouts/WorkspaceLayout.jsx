import React from 'react';
import { Sprout, LayoutDashboard, Map, Stethoscope, Tractor, Users, TrendingUp, Wallet, Files, Landmark, Bell, ArrowUpRight, LogOut, ChevronDown, PanelLeftClose, Menu, WifiOff, Compass } from 'lucide-react';
import { firstName } from '../utils/format';
import { useLanguage } from '../i18n/languageContext';

const items = [
  ['today', 'Today', LayoutDashboard], ['farm', 'My farm', Sprout], ['help', 'Crop care', Stethoscope],
  ['resources', 'Farm services', Tractor], ['groups', 'Together', Users], ['market', 'Market watch', TrendingUp],
  ['planner', 'Smart planner', Compass], ['cashbook', 'Cashbook', Wallet], ['schemes', 'Schemes & support', Landmark], ['documents', 'My documents', Files], ['community', 'Community', Users],
];
export default function WorkspaceLayout({ user, tab, navigate, notifications, onLogout, online, children }) {
  const [expanded, setExpanded] = React.useState(false);
  const { language, setLanguage, t } = useLanguage();
  const staff = user.role !== 'FARMER';
  return <div className="workspace"><a className="skip-link" href="#main">Skip to content</a>
    <aside className={`sidebar ${expanded ? 'expanded' : ''}`}>
      <a href="#today" className="brand" onClick={() => navigate('today')}><span className="brand-mark"><Sprout size={26}/></span><span>krishi<span className="brand-second">sahayak<span className="brand-dot">.</span></span></span></a>
      <div className="workspace-switch"><span className="workspace-avatar"><Map size={17}/></span><div><strong>{staff ? 'Expert workspace' : 'My farm workspace'}</strong><small>Palakkad · Kerala</small></div><ChevronDown size={14}/></div>
      <div className="nav-caption">YOUR EVERYDAY COMPANION</div>
      <nav aria-label="Main navigation">{items.map(([key, label, Icon], i) => <React.Fragment key={key}>{i === 6 && <div className="nav-divider"/>}<button onClick={() => { navigate(key); setExpanded(false); }} className={`nav-item ${tab === key ? 'active' : ''}`} aria-current={tab === key ? 'page' : undefined}><Icon size={19}/><span>{staff && key === 'today' ? 'Review desk' : t(`nav_${key}`) || label}</span>{key === 'help' && <span className="nav-dot"/>}</button></React.Fragment>)}</nav>
      <div className="sidebar-note"><span className="little-sun">✳</span><strong>Good farming grows<br/>with good company.</strong><p>Your farm. Your community.<br/>One step at a time.</p><button onClick={() => navigate('groups')}>Find your people <ArrowUpRight size={16}/></button></div>
      <button className="user-block" onClick={() => navigate('profile')}><span className="avatar">{firstName(user.full_name).slice(0, 1)}</span><span><strong>{firstName(user.full_name)}</strong><small>{staff ? 'Agricultural expert' : 'Farmer account'}</small></span><ChevronDown size={14}/></button>
    </aside>
    <div className="workspace-body"><header className="topbar"><div className="topbar-left"><button className="icon-button mobile-menu" onClick={() => setExpanded(!expanded)} aria-label="Toggle navigation">{expanded ? <PanelLeftClose/> : <Menu/>}</button><span className="breadcrumb">Your workspace <span>/</span> <strong>{items.find(i => i[0] === tab)?.[1] || 'Account'}</strong></span></div><div className="topbar-actions"><label className="language-select"><span>{t('language')}</span><select value={language} onChange={e => setLanguage(e.target.value)} aria-label={t('language')}><option value="en">English</option><option value="ml">മലയാളം</option><option value="hi">हिन्दी</option><option value="ta">தமிழ்</option></select></label><span className="pilot-label"><i/> Local pilot · sample services</span><button className="icon-button notification-button" onClick={() => navigate('notifications')} aria-label="Open notifications"><Bell size={20}/>{notifications.some(n => !n.is_read) && <i/>}</button><button className="icon-button" onClick={onLogout} aria-label="Sign out" title="Sign out"><LogOut size={18}/></button></div></header>
      {!online && <div className="offline-banner"><WifiOff size={17}/> You’re offline. Crop report text is saved on this device. Reconnect before submitting.</div>}
      <main id="main" className="page-content">{children}</main><footer className="workspace-footer"><span><Sprout size={14}/> Rooted in your everyday.</span><span>Krishi Sahayak · Local pilot</span></footer>
    </div><nav className="bottom-nav" aria-label="Mobile navigation">{items.slice(0, 5).map(([key, label, Icon]) => <button key={key} className={tab === key ? 'active' : ''} onClick={() => navigate(key)}><Icon size={20}/><span>{label === 'Farm services' ? 'Services' : label}</span></button>)}</nav>
  </div>;
}
