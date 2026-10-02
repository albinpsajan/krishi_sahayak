import React, { useEffect, useState } from 'react';
import { ArrowUpRight, Info, Calculator } from 'lucide-react';
import { PageHeading, Field, Button } from '../components/ui/Primitives';
import { money } from '../utils/format';
import { liveDataAPI } from '../services/liveDataApi';
import MarketPriceCard from '../components/market/MarketPriceCard';
import useAutoRefresh from '../hooks/useAutoRefresh';

export default function MarketWatchPage({ navigate }) {
  const [qty, setQty] = useState(100), [a, setA] = useState({ price: 30, transport: 400, other: 100 }), [b, setB] = useState({ price: 34, transport: 900, other: 150 });
  const [market, setMarket] = useState(null), [loading, setLoading] = useState(true), [crop, setCrop] = useState(localStorage.getItem('preferredMarketCrop') || 'banana');
  const load = async initial => { if (initial) setLoading(true); try { setMarket(await liveDataAPI.market({ commodity: crop, state: 'Kerala', district: 'Thrissur' })); } catch { /* Keep the previous price snapshot. */ } finally { if (initial) setLoading(false); } };
  useEffect(() => { load(true); }, [crop]); useAutoRefresh(() => load(false), 60000);
  const net = v => qty * v.price - v.transport - v.other;
  return <><PageHeading eyebrow="LOOK BEYOND THE PRICE TAG" title={<>A better price. <em>A clearer picture.</em></>} description="Compare what reaches your pocket after the journey to market."/><MarketPriceCard data={market} loading={loading} onRefresh={() => load(false)}/><section className="calculator"><div className="section-heading"><h2><Calculator size={23}/> Compare two selling options</h2><span className="badge neutral">Illustrative values · editable</span></div><p>Enter actual buyer quotes and costs. All prices below are per kilogram.</p><Field label="Harvest quantity (kg)"><input type="number" min={0} value={qty} onChange={e => setQty(Math.max(0, Number(e.target.value)))}/></Field><div className="comparison-grid">{[[a, setA, 'Option A'], [b, setB, 'Option B']].map(([value, setValue, label]) => <div className="comparison-option" key={label}><h3>{label}</h3>{[['price', 'Buyer quote (₹/kg)'], ['transport', 'Transport (₹)'], ['other', 'Other deductions (₹)']].map(([key, text]) => <Field key={key} label={text}><input type="number" min={0} step="0.01" value={value[key]} onChange={e => setValue({ ...value, [key]: Math.max(0, Number(e.target.value)) })}/></Field>)}<div className="net-return"><span>Estimated net proceeds</span><strong>{money(net(value))}</strong></div></div>)}</div><div className="comparison-result"><Info size={20}/><p>{net(a) === net(b) ? 'Both options have the same estimated net proceeds.' : `${net(a) > net(b) ? 'Option A' : 'Option B'} leaves approximately ${money(Math.abs(net(a) - net(b)))} more after the entered costs.`} Consider quality deductions, payment reliability and spoilage too.</p></div><Button variant="secondary" onClick={() => navigate('groups')}>Explore a shared market trip <ArrowUpRight size={16}/></Button></section></>;
}
