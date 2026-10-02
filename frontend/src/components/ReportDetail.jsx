import React, { useEffect, useState } from 'react';
import { ShieldCheck, Clock, Image } from 'lucide-react';
import { Modal, Badge, Field, Button, ReadAloud } from './ui/Primitives';
import { casesAPI, apiCall } from '../services/api';
import { prettyDate } from '../utils/format';

function PrivatePhoto({ url }) {
  const [src, setSrc] = useState('');
  useEffect(() => {
    let active = true, objectUrl;
    if (!url.startsWith('/api/uploads/')) return;
    fetch(url, {headers:{Authorization:`Bearer ${localStorage.getItem('krishi_token')}`}}).then(r => {if (!r.ok) throw Error(); return r.blob();}).then(blob => {objectUrl=URL.createObjectURL(blob); if(active) setSrc(objectUrl);}).catch(()=>{});
    return () => {active=false; if(objectUrl) URL.revokeObjectURL(objectUrl);};
  }, [url]);
  return src ? <img className="crop-photo" src={src} alt="Farmer’s crop report photograph"/> : null;
}
export default function ReportDetail({ report, staff, mutate, onClose }) {
  const [busy, setBusy] = useState(false);
  const review = report.officer_review;
  async function save(e) {
    e.preventDefault(); const data = Object.fromEntries(new FormData(e.currentTarget)); setBusy(true);
    const ok = await mutate(() => casesAPI.submitOfficerReview(report.id, {...data, is_confirmed:false, follow_up_days:Number(data.follow_up_days)}), 'Reviewed guidance sent to the farmer.');
    setBusy(false); if (ok) onClose();
  }
  const status = async (value) => {setBusy(true); const ok=await mutate(()=>apiCall(`/cases/${report.id}/status`,'PATCH',{status:value}), 'Report updated.'); setBusy(false); if(ok) onClose();};
  return <Modal title={`${report.crop_type} crop report`} subtitle={`${report.case_number} · ${prettyDate(report.created_at)} · ${report.field_location}`} onClose={onClose}><Badge tone={review ? 'green' : 'amber'}>{report.status}</Badge><div className="report-description"><h3>What the farmer noticed</h3><p>{report.symptoms_description}</p></div>{report.images.map(url=><PrivatePhoto key={url} url={url}/>)}{review && <section className="verified-advice"><div className="eyebrow"><ShieldCheck size={16}/> EXPERT-REVIEWED GUIDANCE</div><p>{review.verified_recommendation}</p>{review.precautions && <p><strong>Precautions:</strong> {review.precautions}</p>}<small>Follow up in {review.follow_up_days} days from {prettyDate(review.reviewed_at)}.</small><ReadAloud text={review.verified_recommendation}/></section>}{!review && <div className="info-box"><Clock size={20}/><p>Your report is waiting for a person to review it. This pilot does not provide an automatic disease diagnosis or treatment prescription.</p></div>}{staff ? <form onSubmit={save}><h3>Send reviewed advice</h3><Field label="Guidance for the farmer"><textarea name="verified_recommendation" required minLength={10} maxLength={5000} rows={4} defaultValue={review?.verified_recommendation}/></Field><Field label="Precautions"><textarea name="precautions" rows={2} defaultValue={review?.precautions}/></Field><Field label="Follow-up in days"><input name="follow_up_days" type="number" min={1} max={90} defaultValue={review?.follow_up_days || 7} required/></Field><Button disabled={busy}>{busy ? 'Saving…' : 'Send reviewed guidance'}</Button></form> : <div className="modal-actions">{report.status === 'Officer Verified' && <Button disabled={busy} onClick={()=>status('Closed')}>My issue is resolved</Button>}{report.status === 'Closed' && <Button disabled={busy} variant="secondary" onClick={()=>status('Awaiting Officer Review')}>Reopen this report</Button>}</div>}</Modal>;
}
