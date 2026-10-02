import React from 'react';
import { ShieldCheck } from 'lucide-react';
export default function WeatherActionSuggestion({ text }) { return <div className="weather-action"><ShieldCheck size={17}/><div><strong>Farm action</strong><p>{text}</p></div></div>; }
