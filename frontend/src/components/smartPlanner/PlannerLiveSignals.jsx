import React, { useCallback, useEffect, useState } from 'react';
import WeatherCard from '../weather/WeatherCard';
import MarketPriceCard from '../market/MarketPriceCard';
import { liveDataAPI } from '../../services/liveDataApi';
import useAutoRefresh from '../../hooks/useAutoRefresh';
import useMarketPrices from '../../hooks/useMarketPrices';

export default function PlannerLiveSignals() {
  const marketProps = useMarketPrices();
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const loadWeather = useCallback(async () => {
    setLoading(true);
    try { setWeather(await liveDataAPI.weather()); }
    catch { /* Market requests continue independently of weather failures. */ }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { loadWeather(); }, [loadWeather]);
  useAutoRefresh(loadWeather, 60000);
  return <div className="planner-live-signals">
    <WeatherCard data={weather} loading={loading} onRefresh={loadWeather}/>
    <MarketPriceCard {...marketProps}/>
  </div>;
}
