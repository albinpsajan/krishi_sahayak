import React, { useEffect, useState } from 'react';
import { Camera, Save, Send } from 'lucide-react';
import { Modal, Field, Button } from './ui/Primitives';
import { casesAPI, uploadAPI } from '../services/api';

export default function CropReportForm({ userId, onClose, mutate }) {
  const key = `krishi-report-draft-${userId}`;
  const [draft, setDraft] = useState(() => { try { return JSON.parse(localStorage.getItem(key)) || {crop_type:'Paddy', field_location:'', symptoms_description:''}; } catch {return {crop_type:'Paddy', field_location:'', symptoms_description:''};} });
  const [photo, setPhoto] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  useEffect(() => { localStorage.setItem(key, JSON.stringify(draft)); }, [draft, key]);
  const change = e => setDraft({...draft, [e.target.name]: e.target.value});
  async function submit(e) {
    e.preventDefault(); setError('');
    if (!navigator.onLine) { setError('Your text is saved. Reconnect to upload and send this report.'); return; }
    if (photo && (photo.size > 5*1024*1024 || !['image/jpeg','image/png'].includes(photo.type))) {setError('Choose a JPEG or PNG photo under 5 MB.'); return;}
    setBusy(true);
    const ok = await mutate(async () => { const uploaded = photo ? await uploadAPI.uploadFile(photo) : null; await casesAPI.createCase({...draft, image_base64_or_url: uploaded?.file_url}); }, 'Report sent for expert review.');
    setBusy(false); if (ok) {localStorage.removeItem(key); onClose();}
  }
  return <Modal title="Let’s take a closer look." subtitle="Describe what you see. An expert will review your report before advising treatment." onClose={onClose}><form onSubmit={submit}><div className="draft-note"><Save size={15}/> Text saved on this device as you type</div><div className="form-grid"><Field label="Which crop?"><select name="crop_type" value={draft.crop_type} onChange={change}>{['Paddy','Banana','Coconut','Pepper','Vegetables','Other'].map(v=><option key={v}>{v}</option>)}</select></Field><Field label="Plot or village"><input name="field_location" value={draft.field_location} onChange={change} required minLength={2} maxLength={200} placeholder="e.g. Canal-side field"/></Field></div><Field label="What have you noticed?" hint="Include when it started, which parts are affected, and how much of the crop is affected."><textarea name="symptoms_description" value={draft.symptoms_description} onChange={change} minLength={10} maxLength={3000} rows={5} required placeholder="The lower leaves started turning yellow three days ago…"/></Field><label className="upload-zone"><Camera size={28}/><strong>{photo ? photo.name : 'Add a clear crop photo'}</strong><span>JPEG or PNG · up to 5 MB · optional</span><input type="file" accept="image/jpeg,image/png" onChange={e => setPhoto(e.target.files[0] || null)}/></label><p className="muted small">Only report text is saved offline. Select your photo again if you close this form.</p>{error && <p className="form-error" role="alert">{error}</p>}<Button disabled={busy}><Send size={16}/>{busy ? 'Sending your report…' : 'Send for expert review'}</Button></form></Modal>;
}
