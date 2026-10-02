KEYWORDS = {"weather": ["weather", "rain", "temperature", "കാലാവസ്ഥ", "മഴ", "मौसम", "बारिश", "வானிலை", "மழை"], "market_price": ["price", "market", "rate", "വില", "മാർക്കറ്റ്", "कीमत", "बाज़ार", "भाव", "விலை", "சந்தை"], "planner": ["smart planner", "irrigation", "plot", "ജലസേചനം", "പ്ലാൻ", "सिंचाई", "खेत", "பாசனம்", "திட்டம்"], "resource": ["tractor", "equipment", "service", "ട്രാക്ടർ", "ट्रैक्टर", "यंत्र", "டிராக்டர்"], "crop_report": ["crop problem", "disease", "report", "രോഗം", "समस्या", "நோய்"], "scheme": ["scheme", "subsidy", "പദ്ധതി", "योजना", "திட்டம்"], "documents": ["document", "certificate", "രേഖ", "दस्तावेज", "ஆவணம்"]}

KEYWORDS = {
    "input_guard_note": ["officer note", "read my note", "what did the officer say", "ഇൻപുട്ട് ഗാർഡ് കുറിപ്പ്", "अधिकारी नोट", "அலுவலர் குறிப்பு"],
    "input_guard_weather": ["weather warning", "read weather", "spray warning", "കാലാവസ്ഥ മുന്നറിയിപ്പ്", "मौसम चेतावनी", "வானிலை எச்சரிக்கை"],
    "input_guard_result": ["latest input result", "latest product check", "explain latest result", "input guard result", "ഇൻപുട്ട് ഫലം", "ताज़ा इनपुट जाँच", "சரிபார்ப்பை விளக்கு"],
    "input_guard": ["input guard", "check fertilizer", "check pesticide", "check a fertilizer", "check a pesticide", "is this product safe", "is this safe to use", "product safety", "വളം പരിശോധിക്കുക", "കീടനാശിനി പരിശോധിക്കുക", "खाद जाँचो", "कीटनाशक जाँचो", "உரத்தை சரிபார்க்கவும்", "பூச்சிக்கொல்லியை சரிபார்க்கவும்"],
    **KEYWORDS,
}


def detect_intent(query):
    text = (query or "").lower()
    for intent, words in KEYWORDS.items():
        if any(word in text for word in words): return intent
    return "help"

CROP_WORDS = {"banana": ["banana", "केला", "வாழை"], "coconut": ["coconut", "தேங்காய்", "नारियल"], "paddy": ["paddy", "धान", "நெல்"], "pepper": ["pepper", "மிளகு"], "tomato": ["tomato", "टमाटर"]}
def detect_crop(query, default="banana"):
    text = (query or "").lower()
    return next((crop for crop, words in CROP_WORDS.items() if any(word in text for word in words)), default)

def reply_for(intent, language="en"):
    replies = {"weather": {"en": "Open the weather card for today’s rain chance and field action.", "ml": "ഇന്നത്തെ മഴസാധ്യതയും കൃഷി നിർദ്ദേശവും കാലാവസ്ഥാ കാർഡിൽ കാണാം.", "hi": "आज की बारिश और खेत की सलाह मौसम कार्ड में देखें।", "ta": "இன்றைய மழை வாய்ப்பையும் பண்ணை ஆலோசனையையும் வானிலை அட்டையில் பார்க்கவும்."}, "market_price": {"en": "Open Market Watch to see the latest pilot price and selling suggestion.", "ml": "വിപണി വിലയും വിൽപ്പന നിർദ്ദേശവും മാർക്കറ്റ് വാച്ചിൽ കാണാം.", "hi": "बाज़ार भाव और बिक्री सलाह मार्केट वॉच में देखें।", "ta": "சந்தை விலையையும் விற்பனை ஆலோசனையையும் மார்க்கெட் வாட்சில் பார்க்கவும்."}}
    if intent == "planner": return {"en": "Smart Planner is ready to help you select a plot and plan irrigation.", "ml": "സ്മാർട്ട് പ്ലാനറിൽ പ്ലോട്ടും ജലസേചനവും ആസൂത്രണം ചെയ്യാം.", "hi": "स्मार्ट प्लानर में खेत और सिंचाई की योजना बनाएं।", "ta": "ஸ்மார்ட் பிளானரில் நிலம் மற்றும் பாசனத்தை திட்டமிடுங்கள்."}.get(language, "Smart Planner is ready to help.")
    return replies.get(intent, {}).get(language) or replies.get(intent, {}).get("en") or "I can help with weather, market prices, schemes, services or crop reports."
