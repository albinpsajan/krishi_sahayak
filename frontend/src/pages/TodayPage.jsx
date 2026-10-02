import React, { useCallback, useEffect, useState } from 'react';
import { ArrowRight, ArrowUpRight, Sprout, Camera, Tractor, Users, CalendarDays, ShieldCheck, ChevronRight, Map } from 'lucide-react';
import { PageHeading, SectionHeading, Empty } from '../components/ui/Primitives';
import { firstName, prettyDate } from '../utils/format';
import { liveDataAPI } from '../services/liveDataApi';
import useAutoRefresh from '../hooks/useAutoRefresh';
import WeatherCard from '../components/weather/WeatherCard';
import MarketPriceCard from '../components/market/MarketPriceCard';
import useMarketPrices from '../hooks/useMarketPrices';
import FarmImage from '../components/media/FarmImage';
import { useLanguage } from '../i18n/languageContext';
import '../dashboardImages.css';

const imageCopy = {
  en: {
    eyebrow: 'ROOTED IN THE EVERYDAY', title: 'Your land.', subtitle: 'A season of possibility.',
    description: 'From the first seed to the next harvest, keep your next step in sight.',
    farm: 'Walk through your farm', planner: 'Plan your field', plannerDetail: 'Map crops & irrigation',
    guard: 'Check an input', guardDetail: 'Make an informed purchase', shortcuts: 'Farm shortcuts',
    reference: 'Crop reference',
  },
  ml: {
    eyebrow: 'ഓരോ ദിവസവും കൃഷിക്കൊപ്പം', title: 'നിങ്ങളുടെ ഭൂമി.', subtitle: 'സാധ്യതകളുടെ ഒരു കാലം.',
    description: 'വിത്തിടൽ മുതൽ വിളവെടുപ്പ് വരെ, അടുത്ത ചുവട് ആസൂത്രണം ചെയ്യാം.',
    farm: 'എന്റെ കൃഷിയിടം കാണുക', planner: 'കൃഷിയിടം ആസൂത്രണം ചെയ്യാം', plannerDetail: 'വിളകളും ജലസേചനവും',
    guard: 'ഉൽപ്പന്നം പരിശോധിക്കാം', guardDetail: 'വാങ്ങുന്നതിന് മുമ്പ് അറിയാം', shortcuts: 'കൃഷി സഹായങ്ങൾ',
    reference: 'വിളയുടെ മാതൃകാചിത്രം',
  },
  hi: {
    eyebrow: 'हर दिन, खेती के साथ', title: 'आपकी ज़मीन।', subtitle: 'संभावनाओं का मौसम।',
    description: 'बीज बोने से अगली फसल तक, अपना अगला कदम तय करें।',
    farm: 'अपना खेत देखें', planner: 'खेत की योजना बनाएँ', plannerDetail: 'फसल और सिंचाई का नक्शा',
    guard: 'कृषि उत्पाद जाँचें', guardDetail: 'खरीदने से पहले जानकारी लें', shortcuts: 'खेती के विकल्प',
    reference: 'फसल का संदर्भ चित्र',
  },
  ta: {
    eyebrow: 'ஒவ்வொரு நாளும் விவசாயத்துடன்', title: 'உங்கள் நிலம்.', subtitle: 'வாய்ப்புகள் நிறைந்த பருவம்.',
    description: 'விதைப்பு முதல் அறுவடை வரை, அடுத்த படியைத் திட்டமிடுங்கள்.',
    farm: 'உங்கள் பண்ணையைப் பார்க்கவும்', planner: 'வயலைத் திட்டமிடுங்கள்', plannerDetail: 'பயிர் மற்றும் பாசன வரைபடம்',
    guard: 'இடுபொருளைச் சரிபார்க்கவும்', guardDetail: 'வாங்கும் முன் அறிந்துகொள்ளுங்கள்', shortcuts: 'விவசாய உதவிகள்',
    reference: 'பயிரின் மாதிரிப் படம்',
  },
};

export default function TodayPage({ user, data, navigate, onReport, onCase }) {
  const { language } = useLanguage();
  const copy = imageCopy[language] || imageCopy.en;
  const marketProps = useMarketPrices();
  const [weather, setWeather] = useState(null), [liveLoading, setLiveLoading] = useState(true);
  const loadLive = useCallback(async (initial = false) => {
    if (initial) setLiveLoading(true);
    try { setWeather(await liveDataAPI.farmerWeather(user.id)); }
    catch { /* Weather failures are independent of market prices. */ }
    finally { setLiveLoading(false); }
  }, [user.id]);
  useEffect(() => { loadLive(true); }, [loadLive]);
  useAutoRefresh(() => loadLive(false), 60000);
  const verified = data.cases.find(c => c.officer_review && c.status !== 'Closed');
  const pending = data.cases.filter(c => c.status === 'Awaiting Officer Review');
  const date = new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' });
  const tasks = [
    verified && { type:'EXPERT ADVICE', title:`Your ${verified.crop_type.toLowerCase()} report has a response`, text: 'Read the reviewed guidance and plan your next step.', icon: ShieldCheck, action: 'Read advice', click: () => onCase(verified), tone:'green' },
    { type: 'FARM RECORD', title: data.plots.length ? 'A little observation goes a long way' : 'Let’s get to know your first plot', text: data.plots.length ? 'Keep your crop stage and field notes close at hand.' : 'Add your crop, planting date and irrigation source.', icon: Sprout, action: 'Open my farm', click: () => navigate('farm'), tone:'olive' },
    { type:'PLAN AHEAD', title: 'Need a hand for the next farm job?', text: 'Request equipment or coordinate a shared service.', icon: Tractor, action: 'Find a service', click: () => navigate('resources'), tone:'sand' },
  ].filter(Boolean);
  return <>
    <PageHeading eyebrow={date} title={<>A good day starts here, <em>{firstName(user.full_name)}.</em></>} description="A little clarity for your farm. One useful step at a time." action={<button className="button secondary compact" onClick={() => navigate('farm')}><Sprout size={17}/> My farm <ArrowUpRight size={16}/></button>}/>
    <div className="today-layout"><div className="today-main">
      <section className="season-banner photo-season-banner">
        <FarmImage asset="farmHero" className="season-photo" priority sizes="(max-width: 760px) 100vw, (max-width: 1000px) 75vw, 65vw"/>
        <div className="season-copy">
          <div className="eyebrow">{copy.eyebrow}</div>
          <h2>{copy.title}<br/>{copy.subtitle}</h2>
          <p>{copy.description}</p>
          <button className="banner-link" onClick={() => navigate('farm')}>{copy.farm} <ArrowRight size={18}/></button>
        </div>
        <nav className="season-shortcuts" aria-label={copy.shortcuts}>
          <button className="season-shortcut" onClick={() => navigate('planner')}>
            <Map size={23} aria-hidden="true"/><span><strong>{copy.planner}</strong><small>{copy.plannerDetail}</small></span><ArrowUpRight size={18} aria-hidden="true"/>
          </button>
          <button className="season-shortcut" onClick={() => navigate('input-guard')}>
            <ShieldCheck size={23} aria-hidden="true"/><span><strong>{copy.guard}</strong><small>{copy.guardDetail}</small></span><ArrowUpRight size={18} aria-hidden="true"/>
          </button>
        </nav>
      </section>
      <section className="daily-section"><SectionHeading title="Your next steps" action="View farm" onClick={() => navigate('farm')}/><p className="section-subtitle">The things that deserve your attention.</p><div className="action-list">{tasks.map((task, i) => <article className="action-row" key={task.type}><span className="step-number">0{i+1}</span><span className={`action-icon ${task.tone}`}><task.icon size={22}/></span><div className="action-copy"><div className="eyebrow">{task.type}</div><h3>{task.title}</h3><p>{task.text}</p></div><button className="action-button" onClick={task.click} aria-label={task.action}><ArrowUpRight size={21}/></button></article>)}</div></section>
      <section><SectionHeading title="Growing on your farm" action="All plots" onClick={() => navigate('farm')}/><div className="plot-strip">{data.plots.slice(0,3).map((plot, i) => <button className={`mini-plot photo-mini-plot crop-${i}`} key={plot.id} onClick={() => navigate('farm')}><div className="mini-plot-photo"><FarmImage crop={plot.crop} sizes="(max-width: 420px) 100vw, (max-width: 1000px) 30vw, 20vw"/><span className="crop-reference-label">{copy.reference}</span><span className="mini-plot-arrow"><ArrowUpRight size={17}/></span></div><h3>{plot.crop}</h3><p>{plot.name} · {plot.area} acres</p><div className="plot-stage"><span/> {plot.growth_stage}</div></button>)}{!data.plots.length && <Empty title="Your story starts with a plot">Add your first plot to personalise this space.</Empty>}</div></section>
      <section className="community-banner"><span className="community-icon"><Users size={30}/></span><div><div className="eyebrow">BETTER, TOGETHER</div><h3>Small farms. Shared possibilities.</h3><p>Share a tractor, a market trip, or the work ahead.</p></div><button className="round-button" onClick={() => navigate('groups')} aria-label="Explore cooperation"><ArrowUpRight/></button></section>
    </div><aside className="today-rail">
      <WeatherCard data={weather} loading={liveLoading} onRefresh={() => loadLive(false)}/><MarketPriceCard {...marketProps}/>
      <section className="help-panel photo-help-panel"><FarmImage asset="officerSupport" className="help-field-photo" sizes="(max-width: 760px) 100vw, 350px"/><div className="help-panel-copy"><span className="outlined-icon"><Camera size={24}/></span><h3>Something doesn’t<br/>look right?</h3><p>Share a photo of your crop.<br/>An expert can help you find<br/>the next step.</p><button className="button primary" onClick={onReport}>Report a crop problem <ArrowUpRight size={16}/></button><small><ShieldCheck size={13}/> Guidance reviewed by a person</small></div></section>
      <section className="rail-requests"><SectionHeading title="In progress"/>{pending.length ? pending.slice(0,2).map(c => <button key={c.id} className="request-peek" onClick={() => onCase(c)}><span className="status-dot"/><div><strong>{c.crop_type} crop report</strong><small>Waiting for expert review</small></div><ChevronRight size={16}/></button>) : <p className="muted">No crop reports waiting for review.</p>}{data.bookings.filter(b => !['Cancelled','Completed'].includes(b.status)).slice(0,2).map(b => <button className="request-peek" key={b.id} onClick={() => navigate('resources')}><CalendarDays size={16}/><div><strong>{b.resource_name}</strong><small>{prettyDate(b.date)} · {b.status}</small></div></button>)}</section>
    </aside></div>
  </>;
}
