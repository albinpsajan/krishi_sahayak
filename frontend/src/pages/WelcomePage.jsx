import React, { useState } from 'react';
import { Sprout, ArrowUpRight, ArrowRight, ShieldCheck, Users, Leaf } from 'lucide-react';
import { authAPI } from '../services/api';
import { Button, Field } from '../components/ui/Primitives';

export default function WelcomePage({ onLogin }) {
  const [mode, setMode] = useState('welcome');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const finish = async (operation) => {
    setBusy(true); setError('');
    try { const result = await operation(); localStorage.setItem('krishi_token', result.access_token); onLogin(result.user); }
    catch (e) { setError(e.message); } finally { setBusy(false); }
  };
  const submit = (e) => {
    e.preventDefault(); const form = Object.fromEntries(new FormData(e.currentTarget));
    finish(async () => {
      if (mode !== 'register') return authAPI.login(form.identifier, form.password);
      const res = await authAPI.register({ ...form, role: 'FARMER' });
      localStorage.setItem('krishi_token', res.access_token);
      return authAPI.updateDetails({ full_name: form.full_name, age: Number(form.age), role: 'FARMER', language:'en' });
    });
  };
  return <div className="welcome"><header className="welcome-header"><a className="brand" href="#"><span className="brand-mark"><Sprout size={26}/></span><span>krishi<span className="brand-second">sahayak.</span></span></a><span>FOR THE PEOPLE WHO GROW.</span><button className="text-link" onClick={() => setMode('login')}>Sign in <ArrowUpRight size={18}/></button></header><main className="welcome-grid"><section className="welcome-story"><div className="eyebrow"><span className="status-dot"/> YOUR EVERYDAY FARMING COMPANION</div><h1>Good things<br/>grow from<br/><em>the next step.</em></h1><p>Your land, your questions, your community.<br/>Find a little clarity for everything that grows.</p><div className="welcome-values"><span><Leaf size={19}/> Farm with confidence</span><span><Users size={19}/> Grow together</span></div><div className="welcome-landscape"><svg viewBox="0 0 700 180" aria-hidden="true"><path fill="#D5D8AF" d="M0 110Q180 -60 400 70T700 60V180H0Z"/><path fill="#6F8D61" d="M0 140Q270 40 700 110V180H0Z"/><path fill="#294E3C" d="M0 170Q300 180 700 65V180H0Z"/>{[0,1,2,3].map(i=><path key={i} d={`M${i*70} 180Q380 120 700 ${85+i*23}`} stroke="#F2EAD7" fill="none" opacity=".4"/>)}</svg></div></section><section className="welcome-entry"><div className="eyebrow">WELCOME TO KRISHI SAHAYAK</div><h2>{mode === 'register' ? 'Make room for your farm.' : mode === 'login' ? 'Good to see you again.' : 'Your farm. All together.'}</h2><p>{mode === 'welcome' ? 'A practical place to plan, get help, and move forward.' : 'Keep your next step within reach.'}</p>{error && <div className="form-error" role="alert">{error}</div>}
      {mode === 'welcome' ? <><Button disabled={busy} onClick={() => finish(() => authAPI.login('farmer','farmer123'))}>Explore the farmer workspace <ArrowRight size={18}/></Button><Button variant="secondary" disabled={busy} onClick={() => finish(() => authAPI.login('officer','officer123'))}>Open the expert desk <ArrowUpRight size={18}/></Button><div className="demo-explanation"><ShieldCheck size={18}/><span>This is a local pilot with sample accounts and services. Changes are saved to the local database.</span></div><div className="entry-divider"><span>OR START YOUR OWN</span></div><button className="text-link" onClick={() => setMode('register')}>Create a farmer account <ArrowUpRight size={17}/></button></> : <form onSubmit={submit}>{mode === 'register' ? <><Field label="Your name"><input name="full_name" autoComplete="name" minLength={2} required/></Field><div className="form-grid"><Field label="Username"><input name="username" minLength={3} pattern="[a-zA-Z0-9_.-]+" required autoComplete="username"/></Field><Field label="Age"><input name="age" type="number" min={10} max={120} required/></Field></div><Field label="Email"><input name="email" type="email" required autoComplete="email"/></Field></> : <Field label="Username or email"><input name="identifier" required autoComplete="username"/></Field>}<Field label="Password"><input type="password" name="password" minLength={8} required autoComplete={mode === 'register' ? 'new-password' : 'current-password'}/></Field><Button disabled={busy} type="submit">{busy ? 'Opening your workspace…' : mode === 'register' ? 'Create account' : 'Sign in'}<ArrowRight size={18}/></Button><button className="text-link back-link" type="button" onClick={() => {setMode('welcome'); setError('');}}>Back to explore</button></form>}</section></main><footer className="welcome-footer"><span>Rooted in your everyday.</span><span>Made for farmers. Built around people.</span></footer></div>;
}
