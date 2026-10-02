// Local files only. Provenance and regeneration live in scripts/images/ and
// public/assets/images/*-sources.json; UI labels belong here, not in page markup.
const photo = (file, width, height, en, ml, hi, ta) => ({
  file: `/assets/images/${file}`, width, height, alt: { en, ml, hi, ta },
  widths: width > 800 ? [400, 800, width] : [400, 800],
});

export const imageAssets = {
  farmHero: photo('hero/farm-hero', 1600, 900,
    'A water channel through the Kole paddy fields at dusk in Thrissur, Kerala',
    'തൃശ്ശൂരിലെ കോൾ പാടങ്ങൾക്കിടയിലെ ജലപാത, സന്ധ്യാസമയത്ത്',
    'केरल के त्रिशूर में शाम के समय कोल धान के खेतों के बीच जलधारा',
    'கேரளாவின் திருச்சூரில் மாலையில் கோல் நெல் வயல்களுக்கு இடையிலான நீர்வழி'),
  paddyField: photo('backgrounds/paddy-field-bg', 1200, 675,
    'Kole paddy fields and palm trees at dusk in Kerala',
    'സന്ധ്യയിലെ കേരളത്തിലെ കോൾ പാടങ്ങളും തെങ്ങുകളും',
    'केरल में शाम के समय कोल धान के खेत और नारियल के पेड़',
    'கேரளாவில் மாலையில் கோல் நெல் வயல்களும் தென்னை மரங்களும்'),
  coconutFarm: photo('backgrounds/coconut-farm-bg', 1200, 675,
    'Coconut palms at Bekal Beach Park in Kasaragod, Kerala',
    'കാസർഗോഡ് ബേക്കൽ ബീച്ച് പാർക്കിലെ തെങ്ങുകൾ',
    'केरल के कासरगोड में बेकल बीच पार्क के नारियल के पेड़',
    'கேரளாவின் காசர்கோட்டில் பேக்கல் கடற்கரைப் பூங்காவில் தென்னை மரங்கள்'),
  smartPlanner: photo('features/smart-planner', 1200, 800,
    'Coconut grove in Bekal, Kerala, illustrating plantation planning',
    'തോട്ടം ആസൂത്രണം ചെയ്യുന്നതിനുള്ള ഉദാഹരണമായി ബേക്കലിലെ തെങ്ങിൻതോപ്പ്',
    'बागान योजना के उदाहरण के लिए केरल के बेकल में नारियल का उपवन',
    'தோட்டத் திட்டமிடலுக்கான எடுத்துக்காட்டாக கேரளாவின் பேக்கலில் தென்னந்தோப்பு'),
  inputGuard: photo('features/input-guard', 1200, 800,
    'Garden fork and spade resting in cultivated soil',
    'കൃഷിയിടത്തിലെ മണ്ണിൽ വച്ചിരിക്കുന്ന കൃഷി ഉപകരണങ്ങൾ',
    'खेती की मिट्टी में रखे बागवानी के औजार',
    'பண்படுத்தப்பட்ட மண்ணில் வைக்கப்பட்ட தோட்டக் கருவிகள்'),
  soilCloseup: photo('hero/soil-closeup', 1200, 800,
    'Cultivated soil and garden tools seen close up',
    'കൃഷിയിടത്തിലെ മണ്ണും ഉപകരണങ്ങളും അടുത്ത കാഴ്ചയിൽ',
    'खेती की मिट्टी और औजारों का नज़दीकी दृश्य',
    'பண்படுத்தப்பட்ட மண் மற்றும் தோட்டக் கருவிகளின் நெருக்கமான காட்சி'),
  soilTexture: photo('backgrounds/soil-texture-bg', 1200, 675,
    'Soil and leaf litter around garden tools',
    'കൃഷി ഉപകരണങ്ങൾക്ക് ചുറ്റുമുള്ള മണ്ണും കരിയിലകളും',
    'बागवानी के औजारों के आसपास मिट्टी और सूखी पत्तियाँ',
    'தோட்டக் கருவிகளைச் சுற்றியுள்ள மண் மற்றும் உலர்ந்த இலைகள்'),
  marketPrice: photo('features/market-price', 1200, 800,
    'Fresh beans, guavas and aubergines in a basket in Dang, Gujarat',
    'ഗുജറാത്തിലെ ഡാങ്ങിൽ കുട്ടയിൽ വച്ചിരിക്കുന്ന പച്ചക്കറികളും പേരയ്ക്കയും',
    'गुजरात के डांग में टोकरी में ताज़ी फलियाँ, अमरूद और बैंगन',
    'குஜராத்தின் டாங்கில் கூடையில் புதிய பயறு, கொய்யா மற்றும் கத்தரிக்காய்'),
  irrigation: photo('features/irrigation-system', 1200, 800,
    'A drip irrigation pipe beside a melon plant in Catalonia',
    'കാറ്റലോണിയയിൽ തണ്ണിമത്തൻ ചെടിക്കരികിലെ തുള്ളിനന പൈപ്പ്',
    'कैटालोनिया में खरबूजे के पौधे के पास टपक सिंचाई पाइप',
    'கத்தலோனியாவில் முலாம்பழச் செடிக்கு அருகில் சொட்டு நீர்ப்பாசனக் குழாய்'),
  weather: photo('features/weather-field', 1200, 800,
    'Rice paddy fields and sky in Kerala; an illustrative field photograph',
    'കേരളത്തിലെ നെൽപ്പാടങ്ങളും ആകാശവും; ഉദാഹരണ ചിത്രം',
    'केरल में धान के खेत और आकाश; उदाहरण के लिए खेत की तस्वीर',
    'கேரளாவில் நெல் வயல்களும் வானமும்; எடுத்துக்காட்டு வயல் புகைப்படம்'),
  officerSupport: photo('features/officer-support', 1200, 800,
    'Rice fields in Kerala, illustrating the field context for crop advice',
    'വിള പരിപാലനത്തിന് ഉദാഹരണമായി കേരളത്തിലെ നെൽപ്പാടങ്ങൾ',
    'फसल सलाह के संदर्भ के लिए केरल के धान के खेत',
    'பயிர் ஆலோசனைக்கான சூழலைக் காட்டும் கேரள நெல் வயல்கள்'),
};

export const cropImages = {
  banana: photo('crops/banana', 800, 600, 'Bananas growing on a plant in Kerala', 'കേരളത്തിലെ വാഴയിൽ വളരുന്ന കായകൾ', 'केरल में केले के पौधे पर लगे फल', 'கேரளாவில் வாழை மரத்தில் வளரும் காய்கள்'),
  coconut: photo('crops/coconut', 800, 600, 'Coconut palm in Kavvayi, Kerala', 'കേരളത്തിലെ കവ്വായിയിലെ തെങ്ങ്', 'केरल के कव्वायी में नारियल का पेड़', 'கேரளாவின் கவ்வாயியில் தென்னை மரம்'),
  paddy: photo('crops/paddy', 800, 600, 'Rice paddy fields in Kerala', 'കേരളത്തിലെ നെൽപ്പാടങ്ങൾ', 'केरल के धान के खेत', 'கேரளாவில் நெல் வயல்கள்'),
  pepper: photo('crops/pepper', 800, 600, 'Black pepper growing in Kozhikode, Kerala', 'കോഴിക്കോട്ട് വളരുന്ന കുരുമുളക്', 'केरल के कोझिकोड में उगती काली मिर्च', 'கேரளாவின் கோழிக்கோட்டில் வளரும் மிளகு'),
  ginger: photo('crops/ginger', 800, 600, 'Freshly harvested ginger rhizomes', 'വിളവെടുത്ത ഇഞ്ചി', 'ताज़ी अदरक की गाँठें', 'அறுவடை செய்யப்பட்ட இஞ்சி'),
  turmeric: photo('crops/turmeric', 800, 600, 'Turmeric rhizomes with a cut orange centre', 'മുറിച്ച ഭാഗത്ത് ഓറഞ്ച് നിറമുള്ള മഞ്ഞൾ', 'नारंगी रंग के कटे हिस्से वाली हल्दी की गाँठें', 'வெட்டப்பட்ட ஆரஞ்சு நிற உட்பகுதியுடன் மஞ்சள் கிழங்குகள்'),
};

export const imageLabels = {
  en: { missing: 'Photo unavailable', cropMissing: 'Crop photograph not yet available', credits: 'Photo credits' },
  ml: { missing: 'ചിത്രം ലഭ്യമല്ല', cropMissing: 'വിളയുടെ ചിത്രം ഇതുവരെ ലഭ്യമല്ല', credits: 'ചിത്രങ്ങൾക്ക് കടപ്പാട്' },
  hi: { missing: 'तस्वीर उपलब्ध नहीं है', cropMissing: 'फसल की तस्वीर अभी उपलब्ध नहीं है', credits: 'तस्वीरों का श्रेय' },
  ta: { missing: 'புகைப்படம் கிடைக்கவில்லை', cropMissing: 'பயிர் புகைப்படம் இன்னும் கிடைக்கவில்லை', credits: 'புகைப்பட நன்றிகள்' },
};

export function getCropImage(crop) {
  const key = String(crop || '').trim().toLowerCase();
  return cropImages[{ rice: 'paddy', 'black pepper': 'pepper' }[key] || key];
}
