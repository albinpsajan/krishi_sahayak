import React from 'react';
export default function PriceChangeBadge({ change, direction }) { return <span className={`price-change ${direction || ''}`}>{change > 0 ? '+' : ''}₹{Math.abs(change || 0)} {direction === 'up' ? 'from previous' : direction === 'down' ? 'from previous' : ''}</span>; }
