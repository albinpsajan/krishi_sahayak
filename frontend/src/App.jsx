import React, { useEffect, useState } from 'react';
import { AlertCircle, CheckCircle2, RefreshCw, X } from 'lucide-react';
import { createPortal } from 'react-dom';
import { authAPI } from './services/api';
import useWorkspace from './hooks/useWorkspace';
import WelcomePage from './pages/WelcomePage';
import WorkspaceLayout from './layouts/WorkspaceLayout';
import TodayPage from './pages/TodayPage';
import FarmPage from './pages/FarmPage';
import CropCarePage from './pages/CropCarePage';
import ResourcesPage from './pages/ResourcesPage';
import TogetherPage from './pages/TogetherPage';
import CashbookPage from './pages/CashbookPage';
import MarketWatchPage from './pages/MarketWatchPage';
import CommunityPage from './pages/CommunityPage';
import SmartPlannerPage from './pages/SmartPlannerPage';
import { SchemesPage, DocumentsPage } from './pages/SupportPage';
import { AccountPage, AlertsPage } from './pages/AccountPage';
import CropReportForm from './components/CropReportForm';
import ReportDetail from './components/ReportDetail';
import { LanguageProvider } from './i18n/languageContext';
import VoiceAssistantPanel from './components/voice/VoiceAssistantPanel';

const validTabs = ['today','farm','help','resources','groups','market','planner','cashbook','schemes','documents','profile','notifications','community'];
const getTab = () => validTabs.includes(location.hash.slice(1)) ? location.hash.slice(1) : 'today';

function AppContent() {
  const [user,setUser] = useState(null), [ready,setReady] = useState(false);
  const [tab,setTab] = useState(getTab), [reportOpen,setReportOpen] = useState(false), [report,setReport] = useState(null);
  const [toast,setToast] = useState(null), [online,setOnline] = useState(navigator.onLine);
  const { data,loading,error,refresh } = useWorkspace(user);
  useEffect(() => {
    if (!localStorage.getItem('krishi_token')) {setReady(true);return;}
    authAPI.getMe().then(setUser).catch(()=>localStorage.removeItem('krishi_token')).finally(()=>setReady(true));
  }, []);
  useEffect(() => {const change=()=>setTab(getTab()); window.addEventListener('hashchange',change);return ()=>window.removeEventListener('hashchange',change);}, []);
  useEffect(() => {const change=()=>setOnline(navigator.onLine);window.addEventListener('online',change);window.addEventListener('offline',change);return ()=>{window.removeEventListener('online',change);window.removeEventListener('offline',change);};}, []);
  useEffect(() => {if(!toast)return; const timer=setTimeout(()=>setToast(null),7000);return ()=>clearTimeout(timer);}, [toast]);
  const navigate = value => {location.hash=value;setTab(value);window.scrollTo({top:0,behavior:'instant'});};
  async function mutate(operation,message) {try{await operation();await refresh();setToast({message,kind:'success'});return true;}catch(e){setToast({message:e.message,kind:'error'});return false;}}
  const logout=()=>{localStorage.removeItem('krishi_token');setUser(null);setReport(null);setReportOpen(false);setToast(null);navigate('today');};
  const staff=user?.role!=='FARMER';
  if(!ready) return <div className="app-loading"><span className="loading-leaf">✳</span><p>Opening your farm workspace…</p></div>;
  if(!user) return <WelcomePage onLogin={u=>{setUser(u);navigate('today');}}/>;
  return <WorkspaceLayout user={data.profile ? {...user,full_name:data.profile.full_name} : user} tab={tab} navigate={navigate} notifications={data.notifications} onLogout={logout} online={online}>
    {error && <div className="error-banner" role="alert"><AlertCircle size={19}/><span>Could not refresh your workspace: {error}</span><button onClick={refresh}><RefreshCw size={16}/> Retry</button></div>}
    {loading && !data.profile ? <div className="loading-content">Gathering your farm records…</div> : <>
      {tab==='today' && (staff ? <CropCarePage reports={data.cases} staff onCase={setReport}/> : <TodayPage user={data.profile||user} data={data} navigate={navigate} onReport={()=>setReportOpen(true)} onCase={setReport}/>)}
      {tab==='farm' && <FarmPage plots={data.plots} mutate={mutate} onReport={()=>setReportOpen(true)}/>}
      {tab==='help' && <CropCarePage reports={data.cases} staff={staff} onReport={()=>setReportOpen(true)} onCase={setReport}/>}
      {tab==='resources' && <ResourcesPage resources={data.resources} bookings={data.bookings} staff={staff} mutate={mutate}/>}
      {tab==='groups' && <TogetherPage groups={data.groups} staff={staff} mutate={mutate}/>}
      {tab==='cashbook' && <CashbookPage entries={data.cashbook} staff={staff} mutate={mutate}/>}
      {tab==='market' && <MarketWatchPage navigate={navigate}/>}
      {tab==='planner' && <SmartPlannerPage staff={staff}/>}
      {tab==='community' && <CommunityPage staff={staff}/>}
      {tab==='schemes' && <SchemesPage schemes={data.schemes} navigate={navigate}/>}
      {tab==='documents' && <DocumentsPage available={data.documents} staff={staff} mutate={mutate}/>}
      {tab==='profile' && <AccountPage key={data.profile?.id} profile={data.profile} staff={staff} mutate={mutate}/>}
      {tab==='notifications' && <AlertsPage notifications={data.notifications} mutate={mutate}/>}
    </>}
    {reportOpen && <CropReportForm userId={user.id} onClose={()=>setReportOpen(false)} mutate={mutate}/>}
    {report && <ReportDetail report={report} staff={staff} mutate={mutate} onClose={()=>setReport(null)}/>}<VoiceAssistantPanel/>
    {toast && createPortal(<div className={`toast ${toast.kind}`} role={toast.kind==='error'?'alert':'status'}>{toast.kind==='error'?<AlertCircle size={20}/>:<CheckCircle2 size={20}/>}<span>{toast.message}</span><button aria-label="Dismiss message" onClick={()=>setToast(null)}><X size={17}/></button></div>,document.querySelector('dialog[open] .modal-inner') || document.body)}
  </WorkspaceLayout>;
}
export default function App() { return <LanguageProvider><AppContent/></LanguageProvider>; }
