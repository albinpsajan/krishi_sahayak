import React, { useEffect, useMemo, useState } from 'react';
import { AlertTriangle, ArrowUpRight, BadgeCheck, Check, ClipboardCheck, CloudRain, FileImage, ImagePlus, Info, Leaf, Loader2, ShieldAlert, ShieldCheck, X } from 'lucide-react';
import { useLanguage } from '../i18n/languageContext';
import { inputGuardCopy } from '../i18n/inputGuardTranslations';
import { inputGuardAPI } from '../services/api';
import { Empty, PageHeading } from '../components/ui/Primitives';
import FarmImage from '../components/media/FarmImage';
import '../featureImages.css';

const decisionOptions = ['Approved', 'Not recommended', 'More details needed', 'Field visit required'];
const defaultForm = { product_name: '', product_type: 'Fertilizer', brand: '', batch_number: '', expiry_date: '', mrp: '', dealer_price: '', quantity: '', quantity_unit: 'kg', dealer_name: '', crop: 'Paddy', crop_stage: 'vegetative', land_area: '', label_crops: '', label_rate_per_acre: '', label_rate_unit: 'kg', notes: '' };

function asNumber(value) { return value === '' || value == null ? null : Number(value); }
function cropKey(value) {
  const aliases = [
    ['paddy', 'rice', 'നെല്ല്', 'धान', 'நெல்'], ['banana', 'വാഴ', 'केला', 'வாழை'], ['coconut', 'തെങ്ങ്', 'नारियल', 'தென்னை'],
    ['pepper', 'കുരുമുളക്', 'काली मिर्च', 'மிளகு'], ['tomato', 'തക്കാളി', 'टमाटर', 'தக்காளி'], ['onion', 'ഉള്ളി', 'प्याज', 'வெங்காயம்'],
    ['potato', 'ഉരുളക്കിഴങ്ങ്', 'आलू', 'உருளைக்கிழங்கு'], ['arecanut', 'അടയ്ക്ക', 'सुपारी', 'பாக்கு'], ['rubber', 'റബ്ബർ', 'रबर', 'ரப்பர்'],
    ['ginger', 'ഇഞ്ചി', 'अदरक', 'இஞ்சி'], ['turmeric', 'മഞ്ഞൾ', 'हल्दी', 'மஞ்சள்'], ['vegetables', 'പച്ചക്കറികൾ', 'सब्ज़ियाँ', 'காய்கறிகள்'],
  ];
  return aliases.find(group => group.some(alias => alias.toLowerCase() === value.trim().toLowerCase()))?.[0] || value.trim().toLowerCase();
}

function AuthPhoto({ imageUrl, token, label }) {
  const [src, setSrc] = useState('');
  useEffect(() => {
    if (!imageUrl) return undefined;
    let currentUrl;
    let active = true;
    fetch(imageUrl, { headers: { Authorization: `Bearer ${token}` } }).then(response => {
      if (!response.ok) throw new Error('Photo unavailable');
      return response.blob();
    }).then(blob => {
      currentUrl = URL.createObjectURL(blob);
      if (active) setSrc(currentUrl);
    }).catch(() => {});
    return () => { active = false; if (currentUrl) URL.revokeObjectURL(currentUrl); };
  }, [imageUrl, token]);
  return imageUrl && src ? <img className="ig-saved-photo" src={src} alt={label}/> : null;
}

function Field({ label, hint, children }) {
  return <label className="ig-field"><span>{label}</span>{children}{hint && <small>{hint}</small>}</label>;
}

function AlertLine({ icon: Icon = Info, title, children, tone = '' }) {
  return <div className={`ig-alert ${tone}`}><Icon size={18}/><div><strong>{title}</strong><p>{children}</p></div></div>;
}

function translatedSuitability(check, t) {
  if (check.suitability_status === 'not_recommended') {
    if (check.expiry_date && new Date(`${check.expiry_date}T00:00:00`) < new Date()) return t.suitabilityExpired;
    const labels = check.label_crops.split(',').map(cropKey).filter(Boolean);
    if (labels.length && !labels.includes(cropKey(check.crop))) return t.suitabilityMismatch;
  }
  if (check.expiry_date) {
    const days = Math.ceil((new Date(`${check.expiry_date}T00:00:00`) - new Date()) / 86400000);
    if (days >= 0 && days <= 90) return t.suitabilityNearExpiry;
  }
  return t.suitabilityNeeds;
}

function translatedWeather(check, t) {
  if (check.weather_status === 'unavailable') return t.weatherUnavailable;
  const messages = [];
  if (check.rain_chance != null && check.rain_chance >= 70 && ['Fertilizer', 'Pesticide'].includes(check.product_type)) messages.push(t.weatherRain);
  if (check.wind_kmh != null && check.wind_kmh >= 25 && check.product_type === 'Pesticide') messages.push(t.weatherWind);
  if (check.temperature_c != null && check.temperature_c >= 35 && check.product_type === 'Pesticide') messages.push(t.weatherHeat);
  return messages.length ? `${messages.join(' ')} ${t.reviewHint}` : t.weatherClear;
}

function translatedPrice(check, t) {
  if (check.price_status === 'above_mrp') return t.priceHigh;
  if (check.price_status === 'at_or_below_mrp') return t.priceOkay;
  return t.priceMissing;
}

function translatedQuantity(check, t) {
  if (check.estimated_quantity == null) return t.noEstimate;
  if ((check.quantity_unit || check.estimated_unit).toLowerCase() !== check.estimated_unit.toLowerCase() && check.quantity != null) return t.unitMismatch;
  if (check.quantity != null && check.quantity > check.estimated_quantity * 1.25) return t.amountHigh;
  return t.amountEstimate;
}

function CheckAssessment({ check, t }) {
  const weatherStatus = check.weather_status || 'unavailable';
  const suitabilityStatus = check.suitability_status || 'needs_verification';
  const priceStatus = check.price_status || 'missing';
  const amount = check.estimated_quantity == null ? t.unknown : `${check.estimated_quantity} ${check.estimated_unit} ${t.quantityFor} ${check.land_area} ${t.areaLabel} · ${t.total}`;
  return <div className="ig-assessment">
    <section className="ig-assessment-main">
      <div className="ig-section-label"><ShieldCheck size={16}/>{t.result}</div>
      <h3>{t.suitabilityLabels[suitabilityStatus]}</h3>
      <p>{translatedSuitability(check, t)}</p>
      <small>{t.detailsManual} · {t.noOcr}</small>
    </section>
    <div className="ig-assessment-grid">
      <section className={`ig-assessment-item ${weatherStatus === 'caution' || weatherStatus === 'unavailable' ? 'warn' : ''}`}>
        <div className="ig-section-label"><CloudRain size={16}/>{t.weather} · {check.weather_location || t.unknown}</div>
        <strong>{t.weatherLabels[weatherStatus]}</strong><p>{translatedWeather(check, t)}</p>
        <small>{t.rain}: {check.rain_chance == null ? t.unknown : `${check.rain_chance}%`} · {t.wind}: {check.wind_kmh == null ? t.unknown : `${check.wind_kmh} km/h`}</small>
      </section>
      <section className="ig-assessment-item">
        <div className="ig-section-label"><ClipboardCheck size={16}/>{t.quantityEstimate}</div>
        <strong>{amount}</strong><p>{translatedQuantity(check, t)}</p>
      </section>
      <section className={`ig-assessment-item ${priceStatus === 'above_mrp' ? 'warn' : ''}`}>
        <div className="ig-section-label"><ShieldAlert size={16}/>{t.priceCheck}</div>
        <strong>{t.priceLabels[priceStatus]}</strong><p>{translatedPrice(check, t)}</p>
        <small>{t.localPrice}</small>
      </section>
    </div>
  </div>;
}

function CheckCard({ check, t, token, officer = false, note = '', setNote, decision = 'Approved', setDecision, saveReview, savingId, onEdit }) {
  const productTypeIndex = inputGuardCopy.en.productTypes.indexOf(check.product_type);
  const cropIndex = inputGuardCopy.en.crops.findIndex(crop => crop.toLowerCase() === check.crop.toLowerCase());
  const stageIndex = ['initial', 'vegetative', 'flowering', 'fruiting', 'maturity'].indexOf((check.crop_stage || '').toLowerCase());
  const typeName = productTypeIndex < 0 ? check.product_type : t.productTypes[productTypeIndex];
  const cropName = cropIndex < 0 ? check.crop : t.crops[cropIndex];
  const stageName = stageIndex < 0 ? check.crop_stage : t.stages[stageIndex];
  const title = `${check.product_name}${check.brand ? ` · ${check.brand}` : ''}`;
  return <article className="ig-check-row">
    <div className="ig-check-top"><div>{officer && check.farmer_name && <span className="ig-kicker">{t.farmer}: {check.farmer_name}</span>}<span className="ig-kicker">{typeName} · {cropName} · {check.land_area} {t.areaLabel}</span><h3>{title}</h3></div><span className={`ig-status status-${check.status.toLowerCase().replaceAll(' ', '-')}`}>{t.statusLabels[check.status] || check.status}</span></div>
    <div className="ig-check-details">
      {check.image_url && <AuthPhoto imageUrl={check.image_url} token={token} label={t.previewAlt}/>}
      <dl>
        <div><dt>{t.cropStage}</dt><dd>{stageName || t.unknown}</dd></div>
        <div><dt>{t.batch}</dt><dd>{check.batch_number || t.unknown}</dd></div>
        <div><dt>{t.expiry}</dt><dd>{check.expiry_date || t.unknown}</dd></div>
        <div><dt>{t.dealer}</dt><dd>{check.dealer_name || t.unknown}</dd></div>
        <div><dt>{t.mrp}</dt><dd>{check.mrp == null ? t.unknown : `₹${check.mrp}`}</dd></div>
        <div><dt>{t.dealerPrice}</dt><dd>{check.dealer_price == null ? t.unknown : `₹${check.dealer_price}`}</dd></div>
      </dl>
    </div>
    {!officer && check.status === 'More details needed' && onEdit && <button className="ig-edit-check" type="button" onClick={() => onEdit(check)}><ClipboardCheck size={15}/>{t.editResubmit}<ArrowUpRight size={14}/></button>}
    {check.notes && <p className="ig-farmer-note"><strong>{t.notes}:</strong> {check.notes}</p>}
    <CheckAssessment check={check} t={t}/>
    {check.officer_note && <AlertLine icon={BadgeCheck} title={t.officerNote}>{check.officer_note}</AlertLine>}
    {officer && <div className="ig-review-box">
      <Field label={t.officerNote}><textarea value={note} onChange={e => setNote(check.id, e.target.value)} maxLength={2000} rows="2" placeholder={t.notePlaceholder}/></Field>
      <div className="ig-review-controls"><select value={decision} onChange={e => setDecision(check.id, e.target.value)} aria-label={t.checkStatus}>{decisionOptions.map((value, index) => <option key={value} value={value}>{[t.approve, t.reject, t.requestDetails, t.fieldVisit][index]}</option>)}</select><button type="button" className="ig-button primary" onClick={() => saveReview(check.id)} disabled={savingId === check.id}>{savingId === check.id ? <Loader2 size={16} className="ig-spin"/> : <Check size={16}/>} {t.saveDecision}</button></div>
    </div>}
  </article>;
}

export default function InputGuardPage({ isOfficer = false, plots = [] }) {
  const { language } = useLanguage();
  const t = inputGuardCopy[language] || inputGuardCopy.en;
  const [checks, setChecks] = useState([]), [loading, setLoading] = useState(true), [busy, setBusy] = useState(false), [error, setError] = useState(''), [notice, setNotice] = useState('');
  const [form, setForm] = useState(defaultForm), [photo, setPhoto] = useState(null), [preview, setPreview] = useState('');
  const [editingId, setEditingId] = useState(null), [existingImageUrl, setExistingImageUrl] = useState('');
  const [notes, setNotes] = useState({}), [decisions, setDecisions] = useState({}), [savingId, setSavingId] = useState(null);
  const token = localStorage.getItem('krishi_token') || '';
  const cropOptions = useMemo(() => {
    const farmCrops = plots.map(plot => plot.crop).filter(Boolean);
    return [...new Set([...farmCrops, ...inputGuardCopy.en.crops])];
  }, [plots, t.crops]);

  async function load() {
    setLoading(true); setError('');
    try { setChecks(isOfficer ? await inputGuardAPI.pending() : await inputGuardAPI.list()); }
    catch (e) { setError(e.message); }
    finally { setLoading(false); }
  }
  useEffect(() => { load(); }, [isOfficer]);
  useEffect(() => {
    if (!plots.length) return;
    const first = plots[0];
    setForm(value => ({ ...value, crop: first.crop || value.crop, land_area: value.land_area || String(first.area || '') }));
  }, [plots]);
  useEffect(() => () => { if (preview) URL.revokeObjectURL(preview); }, [preview]);

  function field(name, value) { setForm(current => ({ ...current, [name]: value })); }
  function choosePhoto(file) {
    if (preview) URL.revokeObjectURL(preview);
    setPhoto(file || null);
    setPreview(file ? URL.createObjectURL(file) : '');
  }

  function editCheck(check) {
    setEditingId(check.id); setExistingImageUrl(check.image_url || ''); setPhoto(null); setPreview(''); setError(''); setNotice('');
    setForm({
      product_name: check.product_name, product_type: check.product_type, brand: check.brand || '',
      batch_number: check.batch_number || '', expiry_date: check.expiry_date || '', mrp: check.mrp ?? '',
      dealer_price: check.dealer_price ?? '', quantity: check.quantity ?? '', quantity_unit: check.quantity_unit || 'kg',
      dealer_name: check.dealer_name || '', crop: check.crop, crop_stage: check.crop_stage || 'vegetative',
      land_area: check.land_area, label_crops: check.label_crops || '', label_rate_per_acre: check.label_rate_per_acre ?? '',
      label_rate_unit: check.label_rate_unit || 'kg', notes: check.notes || '',
    });
    window.setTimeout(() => document.getElementById('ig-form-top')?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 80);
  }

  function cancelEdit() {
    setEditingId(null); setExistingImageUrl(''); setForm({ ...defaultForm, crop: plots[0]?.crop || 'Paddy', land_area: plots[0]?.area || '' });
    choosePhoto(null);
  }

  async function submit(event) {
    event.preventDefault(); setBusy(true); setError(''); setNotice('');
    try {
      let image_url = existingImageUrl;
      if (photo) image_url = (await inputGuardAPI.upload(photo)).image_url;
      const payload = {
        ...form, image_url, mrp: asNumber(form.mrp), dealer_price: asNumber(form.dealer_price),
        quantity: asNumber(form.quantity), label_rate_per_acre: asNumber(form.label_rate_per_acre),
        land_area: Number(form.land_area), expiry_date: form.expiry_date || null,
      };
      const saved = editingId ? await inputGuardAPI.update(editingId, payload) : await inputGuardAPI.submit(payload);
      const wasEditing = Boolean(editingId);
      setChecks(current => wasEditing ? current.map(check => check.id === saved.id ? saved : check) : [saved, ...current]);
      setEditingId(null); setExistingImageUrl(''); setForm({ ...defaultForm, crop: form.crop, land_area: form.land_area });
      choosePhoto(null); setNotice(wasEditing ? t.resubmitted : t.checkSaved); window.setTimeout(() => document.getElementById('ig-recent')?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 80);
    } catch (e) { setError(e.message || t.photoFailed); }
    finally { setBusy(false); }
  }

  async function saveReview(id) {
    setSavingId(id); setError(''); setNotice('');
    try {
      await inputGuardAPI.review(id, decisions[id] || 'Approved', notes[id] || '');
      await load(); setNotice(t.decisionSaved);
    } catch (e) { setError(e.message); }
    finally { setSavingId(null); }
  }

  return <div className="input-guard-page">
    <PageHeading eyebrow={t.eyebrow} title={<>{isOfficer ? t.officerTitle : t.farmerTitle}</>} description={isOfficer ? t.officerIntro : t.farmerIntro}/>
    {error && <div className="ig-feedback error" role="alert"><AlertTriangle size={17}/>{error}</div>}
    {notice && <div className="ig-feedback success" role="status"><Check size={17}/>{notice}</div>}
    {isOfficer ? <section className="ig-queue" aria-labelledby="ig-queue-heading">
      <div className="ig-section-head"><div><span className="ig-kicker">{t.pendingChecks}</span><h2 id="ig-queue-heading">{checks.length ? `${checks.length} ${t.pendingChecks.toLowerCase()}` : t.emptyPending}</h2></div><span className="ig-counter">{checks.length.toString().padStart(2, '0')}</span></div>
      {loading ? <div className="ig-loading"><Loader2 className="ig-spin"/> {t.loading}</div> : checks.length ? <div className="ig-check-list">{checks.map(check => <CheckCard key={check.id} check={check} t={t} token={token} officer note={notes[check.id] || ''} setNote={(id, value) => setNotes(prev => ({ ...prev, [id]: value }))} decision={decisions[check.id] || 'Approved'} setDecision={(id, value) => setDecisions(prev => ({ ...prev, [id]: value }))} saveReview={saveReview} savingId={savingId}/>)}</div> : <Empty title={t.emptyPending}>{t.emptyPendingHint}</Empty>}
    </section> : <>
      <div className="ig-intro-strip"><span className="ig-seal"><ShieldCheck size={22}/></span><div><strong>{t.buyBefore}</strong><p>{t.authenticity}</p></div><span className="ig-intro-mark">01—04</span></div>
      <div className="ig-farmer-grid">
        <form className="ig-form" onSubmit={submit}>
          <section className="ig-form-section" id="ig-form-top">
            <div className="ig-section-head"><div><span className="ig-kicker">01 / {t.productDetails}</span><h2>{t.productDetails}</h2></div><Leaf size={19}/></div>
            <Field label={t.productName}><input value={form.product_name} onChange={e => field('product_name', e.target.value)} required minLength="2" maxLength="160" placeholder={t.productName}/></Field>
            <div className="ig-form-grid"><Field label={t.productType}><select value={form.product_type} onChange={e => field('product_type', e.target.value)}>{t.productTypes.map((v, i) => <option value={inputGuardCopy.en.productTypes[i]} key={v}>{v}</option>)}</select></Field><Field label={t.brand}><input value={form.brand} onChange={e => field('brand', e.target.value)} maxLength="120"/></Field></div>
            <div className="ig-form-grid"><Field label={t.batch}><input value={form.batch_number} onChange={e => field('batch_number', e.target.value)} maxLength="100"/></Field><Field label={t.expiry}><input type="date" value={form.expiry_date} onChange={e => field('expiry_date', e.target.value)}/></Field></div>
            <Field label={t.notes}><textarea value={form.notes} onChange={e => field('notes', e.target.value)} maxLength="1500" rows="2" placeholder={t.notePlaceholder}/></Field>
          </section>
          <section className="ig-form-section">
            <div className="ig-section-head"><div><span className="ig-kicker">02 / {t.farmContext}</span><h2>{t.farmContext}</h2></div><Leaf size={19}/></div>
            <div className="ig-form-grid"><Field label={t.crop}><select value={form.crop} onChange={e => field('crop', e.target.value)}>{cropOptions.map(crop => { const cropIndex = inputGuardCopy.en.crops.findIndex(name => name.toLowerCase() === crop.toLowerCase()); return <option key={crop} value={crop}>{cropIndex < 0 ? crop : t.crops[cropIndex]}</option>; })}</select></Field><Field label={t.cropStage}><select value={form.crop_stage} onChange={e => field('crop_stage', e.target.value)}>{t.stages.map((stage, i) => <option key={stage} value={['initial', 'vegetative', 'flowering', 'fruiting', 'maturity'][i]}>{stage}</option>)}</select></Field></div>
            <div className="ig-form-grid"><Field label={t.area}><input type="number" inputMode="decimal" min="0.01" max="100000" step="0.01" value={form.land_area} onChange={e => field('land_area', e.target.value)} required/></Field><Field label={t.labelCrops} hint={t.labelCropsHint}><input value={form.label_crops} onChange={e => field('label_crops', e.target.value)} maxLength="240" placeholder="Paddy, Banana"/></Field></div>
          </section>
          <section className="ig-form-section">
            <div className="ig-section-head"><div><span className="ig-kicker">03 / {t.priceWeather}</span><h2>{t.priceWeather}</h2></div><ClipboardCheck size={19}/></div>
            <div className="ig-form-grid"><Field label={t.mrp}><input type="number" inputMode="decimal" min="0" step="0.01" value={form.mrp} onChange={e => field('mrp', e.target.value)}/></Field><Field label={t.dealerPrice}><input type="number" inputMode="decimal" min="0" step="0.01" value={form.dealer_price} onChange={e => field('dealer_price', e.target.value)}/></Field></div>
            <div className="ig-form-grid"><Field label={t.dealer}><input value={form.dealer_name} onChange={e => field('dealer_name', e.target.value)} maxLength="120"/></Field><div className="ig-form-grid compact-grid"><Field label={t.quantity}><input type="number" inputMode="decimal" min="0.01" step="0.01" value={form.quantity} onChange={e => field('quantity', e.target.value)}/></Field><Field label={t.unit}><select value={form.quantity_unit} onChange={e => field('quantity_unit', e.target.value)}>{t.units.map((unit, i) => <option key={unit} value={inputGuardCopy.en.units[i]}>{unit}</option>)}</select></Field></div></div>
            <div className="ig-form-grid"><Field label={t.rate} hint={t.rateHint}><input type="number" inputMode="decimal" min="0.001" step="0.001" value={form.label_rate_per_acre} onChange={e => field('label_rate_per_acre', e.target.value)}/></Field><Field label={`${t.unit} (${t.rate})`}><select value={form.label_rate_unit} onChange={e => field('label_rate_unit', e.target.value)}>{t.units.slice(0, 4).map((unit, i) => <option key={unit} value={inputGuardCopy.en.units[i]}>{unit}</option>)}</select></Field></div>
          </section>
          <section className="ig-form-section ig-upload-section">
            <div className="ig-section-head"><div><span className="ig-kicker">04 / {t.optional}</span><h2>{t.photoTitle}</h2></div><FileImage size={19}/></div>
            <label className={`ig-upload ${preview ? 'has-image' : ''}`}>
              {preview ? <><img src={preview} alt={t.previewAlt}/><span><Check size={15}/>{photo?.name}</span></> : <><span className="ig-upload-icon"><ImagePlus size={22}/></span><strong>{t.choosePhoto}</strong><small>{existingImageUrl ? t.existingPhoto : t.photoHint}</small></>}
              <input type="file" accept="image/jpeg,image/png,image/webp" onChange={e => choosePhoto(e.target.files?.[0] || null)}/>
            </label>
            {preview && <button type="button" className="ig-remove-photo" onClick={() => choosePhoto(null)}><X size={14}/> {t.removePhoto}</button>}
          </section>
          <div className="ig-submit-row"><span><ShieldCheck size={17}/>{t.sendOfficer}</span><div className="ig-submit-buttons">{editingId && <button type="button" className="ig-button secondary" onClick={cancelEdit}>{t.cancelEdit}</button>}<button className="ig-button primary" disabled={busy}>{busy ? <Loader2 size={17} className="ig-spin"/> : <ArrowUpRight size={17}/>} {busy ? t.submitting : t.submit}</button></div></div>
        </form>
        <aside className="ig-side-rail">
          <div className="ig-side-note ig-photo-note"><FarmImage asset="inputGuard" className="ig-inspection-photo" sizes="(max-width: 520px) 100vw, 360px"/><span className="ig-kicker">{t.safetyFirst}</span><h2>{t.sideTitle}</h2><p>{t.reviewHint}</p><span className="ig-side-illustration"><ShieldAlert size={43} strokeWidth={1}/><i/></span></div>
          <div className="ig-records" id="ig-recent"><div className="ig-section-head"><div><span className="ig-kicker">{t.checkHistory}</span><h2>{t.recentChecks}</h2></div><span className="ig-counter">{checks.length.toString().padStart(2, '0')}</span></div>
            {loading ? <div className="ig-loading"><Loader2 className="ig-spin"/> {t.loading}</div> : checks.length ? <div className="ig-check-list">{checks.slice(0, 8).map(check => <CheckCard key={check.id} check={check} t={t} token={token} onEdit={editCheck}/>)}</div> : <div className="ig-empty"><Info size={20}/><strong>{t.emptyChecks}</strong><p>{t.emptyChecksHint}</p></div>}
          </div>
        </aside>
      </div>
    </>}
  </div>;
}
