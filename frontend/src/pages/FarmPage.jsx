import React, { useState } from 'react';
import { Plus, Droplets, CalendarDays, ArrowUpRight } from 'lucide-react';
import { PageHeading, Button, Modal, Field, Badge, Empty } from '../components/ui/Primitives';
import FarmImage from '../components/media/FarmImage';
import { workspaceAPI } from '../services/workspace';
import { prettyDate, today } from '../utils/format';
import { useLanguage } from '../i18n/languageContext';
import '../dashboardImages.css';

const cropOptions = ['Paddy', 'Banana', 'Coconut', 'Pepper', 'Ginger', 'Turmeric', 'Vegetables', 'Other'];
const referenceLabels = {
  en: 'Crop reference photo', ml: 'വിളയുടെ മാതൃകാചിത്രം',
  hi: 'फसल का संदर्भ चित्र', ta: 'பயிரின் மாதிரிப் படம்',
};

export default function FarmPage({ plots, mutate, onReport }) {
  const { language } = useLanguage();
  const referenceLabel = referenceLabels[language] || referenceLabels.en;
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [selectedCrop, setSelectedCrop] = useState('Paddy');
  async function save(e) {
    e.preventDefault();
    const fields = Object.fromEntries(new FormData(e.currentTarget));
    setBusy(true);
    const ok = await mutate(() => workspaceAPI.create('plots', { ...fields, area: Number(fields.area) }), 'Your plot is ready.');
    setBusy(false);
    if (ok) setOpen(false);
  }
  return <>
    <PageHeading
      eyebrow="YOUR LAND, AT A GLANCE"
      title={<>Every plot has <em>a story.</em></>}
      description="Keep each crop, season and growing stage in one place."
      action={<Button onClick={() => setOpen(true)}><Plus size={17}/> Add a plot</Button>}
    />
    <div className="summary-line farm-photo-summary">
      <span><strong>{plots.length}</strong> plots</span>
      <span><strong>{plots.reduce((a, p) => a + p.area, 0).toFixed(1)}</strong> acres recorded</span>
      <span><strong>{new Set(plots.map(p => p.crop)).size}</strong> crops growing</span>
    </div>
    <div className="card-grid">
      {plots.map(p => <article className="plot-card photo-plot-card" key={p.id}>
        <div className="plot-art">
          <FarmImage crop={p.crop} sizes="(max-width: 420px) 100vw, (max-width: 1200px) 45vw, 30vw"/>
          <span className="crop-reference-label">{referenceLabel}</span>
          <Badge>{p.area} acres</Badge>
        </div>
        <div className="card-body">
          <div className="eyebrow">{p.name}</div>
          <h2>{p.crop}</h2>
          <Badge tone="green">{p.growth_stage}</Badge>
          <div className="detail-lines">
            <span><Droplets size={17}/>{p.water_source}</span>
            <span><CalendarDays size={17}/>Planted {prettyDate(p.planting_date)}</span>
          </div>
          <button className="text-link" onClick={onReport}>Ask about this crop <ArrowUpRight size={16}/></button>
        </div>
      </article>)}
    </div>
    {!plots.length && <Empty title="Let’s start with your first plot">Add a name you recognise, your crop and its planting date.</Empty>}
    {open && <Modal title="Add a farm plot" subtitle="A few details make your farm records more useful." onClose={() => setOpen(false)}>
      <form onSubmit={save}>
        <Field label="Plot name"><input name="name" placeholder="e.g. Canal-side field" required minLength={2} maxLength={100}/></Field>
        <div className="form-grid">
          <Field label="Crop">
            <select name="crop" value={selectedCrop} onChange={e => setSelectedCrop(e.target.value)}>
              {cropOptions.map(crop => <option key={crop}>{crop}</option>)}
            </select>
          </Field>
          <Field label="Area in acres"><input name="area" type="number" min="0.01" step="0.01" required/></Field>
        </div>
        <div className="farm-crop-preview">
          <FarmImage crop={selectedCrop} sizes="66px"/>
          <div><strong>{selectedCrop}</strong><small>{referenceLabel}</small></div>
        </div>
        <Field label="Planting date"><input name="planting_date" type="date" max={today()} required/></Field>
        <div className="form-grid">
          <Field label="Irrigation source"><select name="water_source">{['Canal', 'Well', 'Borewell', 'Rain-fed', 'Pond'].map(value => <option key={value}>{value}</option>)}</select></Field>
          <Field label="Crop stage"><select name="growth_stage">{['initial', 'vegetative', 'flowering', 'fruiting', 'maturity'].map(value => <option key={value}>{value}</option>)}</select></Field>
        </div>
        <Button disabled={busy}>{busy ? 'Saving…' : 'Save plot'}</Button>
      </form>
    </Modal>}
  </>;
}
