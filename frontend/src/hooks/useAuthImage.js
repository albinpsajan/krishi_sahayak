import { useEffect, useState } from 'react';

/**
 * Loads a private photo (e.g. /api/uploads/<user>/<file>) with the stored
 * Bearer token and exposes it as an object URL for <img src>. The object URL
 * is revoked when the URL changes or the component unmounts.
 */
export default function useAuthImage(url) {
  const [src, setSrc] = useState('');
  useEffect(() => {
    if (!url) { setSrc(''); return undefined; }
    let objectUrl;
    let active = true;
    const token = localStorage.getItem('krishi_token');
    fetch(url, { headers: token ? { Authorization: `Bearer ${token}` } : {} })
      .then(response => { if (!response.ok) throw new Error('Photo unavailable'); return response.blob(); })
      .then(blob => { objectUrl = URL.createObjectURL(blob); if (active) setSrc(objectUrl); })
      .catch(() => { if (active) setSrc(''); });
    return () => { active = false; if (objectUrl) URL.revokeObjectURL(objectUrl); };
  }, [url]);
  return src;
}
