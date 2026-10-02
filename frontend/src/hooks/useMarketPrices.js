import { useCallback, useEffect, useRef, useState } from 'react';
import { liveDataAPI } from '../services/liveDataApi';
import useAutoRefresh from './useAutoRefresh';

// Ignore late responses after a crop switch. Never retain another crop's quote.
export default function useMarketPrices() {
  const [crop, setCrop] = useState(() => localStorage.getItem('preferredMarketCrop') || 'banana');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const requestId = useRef(0);
  const refresh = useCallback(async () => {
    const id = ++requestId.current;
    setLoading(true);
    setData(null);
    try {
      const next = await liveDataAPI.market({ commodity: crop, state: 'Kerala', district: 'Thrissur' });
      if (id === requestId.current) setData(next);
    } catch {
      if (id === requestId.current) setData({ requested_commodity: crop, available: false,
        warning: 'Market prices could not be loaded. Please retry.' });
    } finally {
      if (id === requestId.current) setLoading(false);
    }
  }, [crop]);
  useEffect(() => { refresh(); return () => { requestId.current++; }; }, [refresh]);
  useAutoRefresh(refresh, 60000);
  const selectCrop = value => {
    requestId.current++;
    setData(null);
    setLoading(true);
    localStorage.setItem('preferredMarketCrop', value);
    setCrop(value);
  };
  return { data, crop, loading, onCropChange: selectCrop, onRefresh: refresh };
}
