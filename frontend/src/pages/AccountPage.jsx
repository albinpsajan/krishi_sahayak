import React, { useState } from 'react';
import { Bell, Check, User } from 'lucide-react';
import { PageHeading, Field, Button, Empty, ReadAloud, Badge } from '../components/ui/Primitives';
import { workspaceAPI } from '../services/workspace';
import { notificationsAPI } from '../services/api';
import { prettyDate } from '../utils/format';

export function AccountPage({ profile, mutate, staff }) {
  const [busy,setBusy]=useState(false);
  async function submit(e){e.preventDefault();const fields=Object.fromEntries(new FormData(e.currentTarget));setBusy(true);await mutate(()=>workspaceAPI.profile(fields),'Your profile has been updated.');setBusy(false);}
  if(!profile)return null;
  return <><PageHeading eyebrow="THE PERSON BEHIND THE FARM" title={<>Make yourself <em>at home.</em></>} description="Your profile helps keep your records in context."/><section className="profile-panel"><div className="profile-summary"><span className="large-avatar"><User size={32}/></span><div><h2>{profile.full_name}</h2><p>{profile.email}</p><Badge tone="green">{profile.role.toLowerCase()}</Badge></div></div>{staff?<div className="info-box"><p>Staff credentials are managed by the administrator. Your expert role cannot be edited from this account screen.</p></div>:<form onSubmit={submit}><Field label="Full name"><input name="full_name" defaultValue={profile.full_name} minLength={2} maxLength={100} required/></Field><Field label="Phone"><input name="phone" type="tel" defaultValue={profile.phone || ''} maxLength={25}/></Field><div className="form-grid"><Field label="District"><input name="district" defaultValue={profile.farmer_profile?.district || ''} required minLength={2}/></Field><Field label="Irrigation source"><input name="water_source" defaultValue={profile.farmer_profile?.water_source || ''} required minLength={2}/></Field></div><Button disabled={busy}>{busy?'Saving…':'Save profile'}</Button></form>}<p className="muted small">The pilot interface is in English. Local-language translation and voice reporting need field validation before rollout.</p></section></>;
}

export function AlertsPage({ notifications, mutate }) {
  return <><PageHeading eyebrow="KEEPING YOU IN THE LOOP" title={<>A word <em>from your workspace.</em></>} description="Crop reviews and account updates, all in one place."/><div className="notification-list">{notifications.map(n=><article key={n.id} className={n.is_read?'read':''}><span className="notification-icon"><Bell size={20}/></span><div><div className="eyebrow">{prettyDate(n.created_at)} · {n.is_read?'READ':'NEW'}</div><h3>{n.title.replace(/[🤖✓]/gu,'')}</h3><p>{n.message}</p><ReadAloud text={n.message}/></div>{!n.is_read && <button className="icon-button" aria-label={`Mark ${n.title} as read`} onClick={()=>mutate(()=>notificationsAPI.markAsRead(n.id),'Marked as read.')}><Check size={20}/></button>}</article>)}</div>{!notifications.length && <Empty title="You’re all caught up">New updates will appear here.</Empty>}</>;
}
