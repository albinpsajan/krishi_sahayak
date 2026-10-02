export const money = (value) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value || 0);
export const today = () => { const d=new Date(); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`; };
export const prettyDate = (value) => value ? new Date(value.length === 10 ? `${value}T12:00:00` : value).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : 'Not set';
export const firstName = (name) => (name || 'Farmer').split(' ')[0];
export function listen(text) {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const speech = new SpeechSynthesisUtterance(text);
    speech.lang = 'en-IN';
    speech.rate = 0.9;
    window.speechSynthesis.speak(speech);
  }
}
