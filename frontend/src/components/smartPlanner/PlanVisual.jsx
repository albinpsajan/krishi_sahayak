import React from 'react';
export default function PlanVisual({ svg, title = 'Rough field layout' }) { return <div className="plan-visual"><div className="plan-visual-title"><span>{title}</span><small>Planning diagram</small></div><div dangerouslySetInnerHTML={{ __html: svg }} /></div>; }
