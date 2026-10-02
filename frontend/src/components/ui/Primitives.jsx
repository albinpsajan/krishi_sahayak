import React, { useEffect, useRef } from 'react';
import { ArrowUpRight, X, Leaf, Volume2 } from 'lucide-react';
import { listen } from '../../utils/format';

export function Button({ children, variant = 'primary', className = '', ...props }) {
  return <button className={`button ${variant} ${className}`} {...props}>{children}</button>;
}
export function PageHeading({ eyebrow, title, description, action }) {
  return <div className="page-heading"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1>{description && <p>{description}</p>}</div>{action}</div>;
}
export function SectionHeading({ title, action, onClick }) {
  return <div className="section-heading"><h2>{title}</h2>{action && <button className="text-link" onClick={onClick}>{action}<ArrowUpRight size={16}/></button>}</div>;
}
export function Badge({ children, tone = '' }) { return <span className={`badge ${tone}`}>{children}</span>; }
export function Empty({ title, children }) { return <div className="empty"><Leaf size={28}/><h3>{title}</h3><p>{children}</p></div>; }
export function Field({ label, children, hint }) { return <label className="field"><span>{label}</span>{children}{hint && <small>{hint}</small>}</label>; }
export function ReadAloud({ text }) { return 'speechSynthesis' in window ? <button className="read-aloud" onClick={() => listen(text)} aria-label="Listen to this message"><Volume2 size={16}/> Listen</button> : null; }
export function Modal({ title, subtitle, children, onClose }) {
  const dialog = useRef(null);
  useEffect(() => {
    const element = dialog.current;
    element.showModal();
    const before = document.activeElement;
    return () => { element.close(); before?.focus(); };
  }, []);
  return <dialog ref={dialog} className="modal" onCancel={onClose} onClick={e => { if (e.target === dialog.current) onClose(); }} aria-labelledby="dialog-title"><div className="modal-inner"><div className="modal-heading"><div><div className="eyebrow">KRISHI SAHAYAK</div><h2 id="dialog-title">{title}</h2>{subtitle && <p>{subtitle}</p>}</div><button className="icon-button" onClick={onClose} aria-label="Close dialog"><X size={22}/></button></div>{children}</div></dialog>;
}
