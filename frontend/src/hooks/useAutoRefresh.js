import { useEffect, useRef } from 'react';
export default function useAutoRefresh(callback, intervalMs = 60000) {
  const callbackRef = useRef(callback); callbackRef.current = callback;
  useEffect(() => { const id = setInterval(() => callbackRef.current(), intervalMs); return () => clearInterval(id); }, [intervalMs]);
}
