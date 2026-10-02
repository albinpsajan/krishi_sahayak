"""Localized voice summaries of a farmer's own latest product check."""

MESSAGES = {
    "en": {
        "none": "There is no product check yet. Open Input Guard and enter the package details first.",
        "open": "Opening Input Guard. Enter the product, crop, and field area to begin. I cannot confirm whether a product is genuine.",
        "no_note": "There is no officer note on the latest product check yet.",
        "note": "The officer's note says: {note}",
        "weather": "Weather note for {product}: {note}",
        "wx_unavailable": "Live weather is unavailable; check local conditions before weather-sensitive work.",
        "wx_clear": "No major weather restriction was shown. Check your field conditions and product label.",
        "wx_rain": "Rain is likely; avoid applying before rain.", "wx_wind": "Wind is strong; avoid spraying because of drift risk.", "wx_heat": "It is hot; avoid spraying during peak heat.",
        "result": "Latest check for {product}: {status}. Crop suitability: {suitability}. Price check: {price}. {weather} Follow the package label and officer guidance.",
        "status": {"Submitted": "sent for officer review", "Under review": "under review", "Approved": "reviewed by an officer", "Not recommended": "not recommended by an officer", "More details needed": "returned for more details", "Field visit required": "a field visit was requested"},
        "suitability": {"needs_verification": "needs officer verification", "not_recommended": "does not match entered label details", "insufficient_information": "needs more information"},
        "price": {"above_mrp": "quote is above the entered MRP", "at_or_below_mrp": "quote is at or below the entered MRP", "missing": "price could not be compared"},
    },
    "ml": {
        "none": "ഇതുവരെ ഉൽപ്പന്ന പരിശോധനയില്ല. ആദ്യം ഇൻപുട്ട് ഗാർഡിൽ പാക്കറ്റിന്റെ വിവരങ്ങൾ നൽകുക.",
        "open": "ഇൻപുട്ട് ഗാർഡ് തുറക്കുന്നു. ഉൽപ്പന്നം, വിള, കൃഷിയിട വിസ്തൃതി എന്നിവ നൽകി തുടങ്ങുക. യഥാർത്ഥത ഉറപ്പാക്കാൻ എനിക്ക് കഴിയില്ല.",
        "no_note": "ഏറ്റവും പുതിയ പരിശോധനയിൽ ഉദ്യോഗസ്ഥന്റെ കുറിപ്പില്ല.", "note": "ഉദ്യോഗസ്ഥന്റെ കുറിപ്പ്: {note}",
        "weather": "{product} ഉൽപ്പന്നത്തിനുള്ള കാലാവസ്ഥാ കുറിപ്പ്: {note}",
        "wx_unavailable": "തത്സമയ കാലാവസ്ഥ ലഭ്യമല്ല; പ്രാദേശിക സാഹചര്യം പരിശോധിക്കുക.", "wx_clear": "പ്രധാന കാലാവസ്ഥാ തടസ്സം കണ്ടില്ല. കൃഷിയിടത്തിലെ സാഹചര്യം, ഉൽപ്പന്ന ലേബൽ എന്നിവ പരിശോധിക്കുക.",
        "wx_rain": "മഴയ്ക്ക് സാധ്യതയുണ്ട്; മഴയ്ക്ക് മുമ്പ് പ്രയോഗിക്കരുത്.", "wx_wind": "കാറ്റ് ശക്തമാണ്; പടരാനുള്ള അപകടം ഒഴിവാക്കാൻ തളിക്കരുത്.", "wx_heat": "ചൂട് കൂടുതലാണ്; കടുത്ത ചൂടിൽ തളിക്കുന്നത് ഒഴിവാക്കുക.",
        "result": "ഏറ്റവും പുതിയ {product} പരിശോധന: {status}. വിളയ്ക്കുള്ള അനുയോജ്യത: {suitability}. വില പരിശോധന: {price}. {weather} പാക്കറ്റിലെ നിർദ്ദേശങ്ങളും ഉദ്യോഗസ്ഥന്റെ ഉപദേശവും പാലിക്കുക.",
        "status": {"Submitted": "ഉദ്യോഗസ്ഥന്റെ പരിശോധനയ്ക്ക് അയച്ചു", "Under review": "പരിശോധനയിലാണ്", "Approved": "ഉദ്യോഗസ്ഥൻ പരിശോധിച്ചു", "Not recommended": "ഉദ്യോഗസ്ഥൻ ശുപാർശ ചെയ്തില്ല", "More details needed": "കൂടുതൽ വിവരങ്ങൾ ആവശ്യപ്പെട്ടു", "Field visit required": "കൃഷിയിട സന്ദർശനം ആവശ്യപ്പെട്ടു"},
        "suitability": {"needs_verification": "ഉദ്യോഗസ്ഥന്റെ പരിശോധന വേണം", "not_recommended": "നൽകിയ ലേബൽ വിവരങ്ങൾ പൊരുത്തപ്പെടുന്നില്ല", "insufficient_information": "കൂടുതൽ വിവരങ്ങൾ വേണം"},
        "price": {"above_mrp": "നൽകിയ എം.ആർ.പി.യേക്കാൾ കൂടുതലാണ്", "at_or_below_mrp": "നൽകിയ എം.ആർ.പി.യുടെ പരിധിയിലാണ്", "missing": "വില താരതമ്യം ചെയ്യാനായില്ല"},
    },
    "hi": {
        "none": "अभी कोई उत्पाद जाँच नहीं है। पहले इनपुट गार्ड में पैकेट की जानकारी भरें।",
        "open": "इनपुट गार्ड खोल रहा हूँ। शुरू करने के लिए उत्पाद, फसल और जमीन की जानकारी भरें। मैं उत्पाद के असली होने की पुष्टि नहीं कर सकता।",
        "no_note": "पिछली उत्पाद जाँच पर अधिकारी का कोई नोट नहीं है।", "note": "अधिकारी का नोट: {note}",
        "weather": "{product} के लिए मौसम की जानकारी: {note}",
        "wx_unavailable": "लाइव मौसम उपलब्ध नहीं है; मौसम पर निर्भर काम से पहले स्थानीय स्थिति जाँचें।", "wx_clear": "कोई बड़ी मौसम रोक नहीं दिखी। अपने खेत की स्थिति और उत्पाद का लेबल जाँचें।",
        "wx_rain": "बारिश की संभावना है; बारिश से पहले उत्पाद न डालें।", "wx_wind": "हवा तेज़ है; बहाव के जोखिम से बचने के लिए छिड़काव न करें।", "wx_heat": "गर्मी है; तेज़ धूप में छिड़काव न करें।",
        "result": "पिछली {product} जाँच: {status}. फसल उपयुक्तता: {suitability}. कीमत: {price}. {weather} पैकेट का लेबल और अधिकारी की सलाह मानें।",
        "status": {"Submitted": "अधिकारी को भेजी गई", "Under review": "जाँच में है", "Approved": "अधिकारी ने जाँची", "Not recommended": "अधिकारी ने मना किया", "More details needed": "और जानकारी माँगी गई", "Field visit required": "खेत का दौरा माँगा गया"},
        "suitability": {"needs_verification": "अधिकारी की पुष्टि ज़रूरी", "not_recommended": "भरी लेबल जानकारी मेल नहीं खाती", "insufficient_information": "और जानकारी चाहिए"},
        "price": {"above_mrp": "दर्ज MRP से अधिक", "at_or_below_mrp": "दर्ज MRP के भीतर", "missing": "कीमत की तुलना नहीं हुई"},
    },
    "ta": {
        "none": "இன்னும் பொருள் சரிபார்ப்பு இல்லை. முதலில் உள்ளீடு சரிபார்ப்பில் பொட்டல விவரங்களை உள்ளிடவும்.",
        "open": "உள்ளீடு சரிபார்ப்பைத் திறக்கிறேன். பொருள், பயிர், நிலப்பரப்பு விவரங்களை உள்ளிடவும். உண்மைத்தன்மையை உறுதிப்படுத்த என்னால் முடியாது.",
        "no_note": "சமீபத்திய பொருள் சரிபார்ப்பில் அலுவலர் குறிப்பு இல்லை.", "note": "அலுவலர் குறிப்பு: {note}",
        "weather": "{product} பொருளுக்கான வானிலை குறிப்பு: {note}",
        "wx_unavailable": "நேரடி வானிலை கிடைக்கவில்லை; வானிலை சார்ந்த வேலைக்கு முன் உள்ளூர் நிலையைப் பாருங்கள்.", "wx_clear": "பெரிய வானிலைத் தடை தெரியவில்லை. நிலத்தின் நிலையும் பொருள் லேபிளையும் பாருங்கள்.",
        "wx_rain": "மழை பெய்ய வாய்ப்பு உள்ளது; மழைக்கு முன் இடுவதைத் தவிர்க்கவும்.", "wx_wind": "காற்று பலமாக உள்ளது; தெளிப்பதைத் தவிர்க்கவும்.", "wx_heat": "வெப்பம் அதிகம்; உச்ச வெப்ப நேரத்தில் தெளிக்க வேண்டாம்.",
        "result": "சமீபத்திய {product} சரிபார்ப்பு: {status}. பயிர் பொருத்தம்: {suitability}. விலை: {price}. {weather} பொட்டல லேபிளையும் அலுவலர் ஆலோசனையையும் பின்பற்றவும்.",
        "status": {"Submitted": "அலுவலர் மதிப்பாய்வுக்கு அனுப்பப்பட்டது", "Under review": "மதிப்பாய்வில் உள்ளது", "Approved": "அலுவலர் மதிப்பாய்வு செய்தார்", "Not recommended": "அலுவலர் பரிந்துரைக்கவில்லை", "More details needed": "கூடுதல் விவரம் கேட்கப்பட்டது", "Field visit required": "நிலப் பார்வை கோரப்பட்டது"},
        "suitability": {"needs_verification": "அலுவலர் சரிபார்ப்பு தேவை", "not_recommended": "உள்ளிட்ட லேபிள் விவரங்கள் பொருந்தவில்லை", "insufficient_information": "மேலும் தகவல் தேவை"},
        "price": {"above_mrp": "உள்ளிட்ட MRP-ஐ விட அதிகம்", "at_or_below_mrp": "உள்ளிட்ட MRP-க்குள் உள்ளது", "missing": "விலையை ஒப்பிட முடியவில்லை"},
    },
}


def reply_for_check(action, check, language="en"):
    strings = MESSAGES.get(language, MESSAGES["en"])
    if check is None:
        return strings["none"]
    if action == "input_guard_note":
        return strings["note"].format(note=check.officer_note) if check.officer_note else strings["no_note"]
    weather = local_weather_note(check, strings)
    if action == "input_guard_weather":
        return weather
    return strings["result"].format(
        product=check.product_name,
        status=strings["status"].get(check.status, check.status),
        suitability=strings["suitability"].get(check.suitability_status, strings["suitability"]["needs_verification"]),
        price=strings["price"].get(check.price_status, strings["price"]["missing"]),
        weather=weather,
    )


def reply_for_open(language="en"):
    return MESSAGES.get(language, MESSAGES["en"])["open"]


def local_weather_note(check, strings):
    if check.weather_status == "unavailable":
        return strings["wx_unavailable"]
    risks = []
    if check.rain_chance is not None and check.rain_chance >= 70 and check.product_type in ("Fertilizer", "Pesticide"):
        risks.append(strings["wx_rain"])
    if check.wind_kmh is not None and check.wind_kmh >= 25 and check.product_type == "Pesticide":
        risks.append(strings["wx_wind"])
    if check.temperature_c is not None and check.temperature_c >= 35 and check.product_type == "Pesticide":
        risks.append(strings["wx_heat"])
    return " ".join(risks) if risks else strings["wx_clear"]
