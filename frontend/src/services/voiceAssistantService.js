import { liveDataAPI } from './liveDataApi';
export const VOICE_CODES = { en: 'en-IN', ml: 'ml-IN', hi: 'hi-IN', ta: 'ta-IN' };
export function speak(text, language) { if ('speechSynthesis' in window) { window.speechSynthesis.cancel(); const utterance = new SpeechSynthesisUtterance(text); utterance.lang = VOICE_CODES[language] || VOICE_CODES.en; window.speechSynthesis.speak(utterance); } }
export function createRecognition(language, onResult, onEnd, onError) { const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition; if (!Recognition) return null; const recognition = new Recognition(); recognition.lang = VOICE_CODES[language] || VOICE_CODES.en; recognition.interimResults = false; recognition.onresult = event => onResult(event.results[0][0].transcript); recognition.onend = onEnd; recognition.onerror = onError; return recognition; }
export const askAssistant = (query, language) => liveDataAPI.assistant(query, language);
