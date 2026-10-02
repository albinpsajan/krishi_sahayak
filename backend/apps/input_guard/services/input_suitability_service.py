"""Conservative suitability rules based only on farmer-entered label details."""
from datetime import date

CROP_ALIASES = {
    "paddy": ("paddy", "rice", "നെല്ല്", "धान", "நெல்"),
    "banana": ("banana", "വാഴ", "केला", "வாழை"),
    "coconut": ("coconut", "തെങ്ങ്", "नारियल", "தென்னை"),
    "pepper": ("pepper", "കുരുമുളക്", "काली मिर्च", "மிளகு"),
    "tomato": ("tomato", "തക്കാളി", "टमाटर", "தக்காளி"),
    "onion": ("onion", "ഉള്ളി", "प्याज", "வெங்காயம்"),
    "potato": ("potato", "ഉരുളക്കിഴങ്ങ്", "आलू", "உருளைக்கிழங்கு"),
    "arecanut": ("arecanut", "അടയ്ക്ക", "सुपारी", "பாக்கு"),
    "rubber": ("rubber", "റബ്ബർ", "रबर", "ரப்பர்"),
    "ginger": ("ginger", "ഇഞ്ചി", "अदरक", "இஞ்சி"),
    "turmeric": ("turmeric", "മഞ്ഞൾ", "हल्दी", "மஞ்சள்"),
    "vegetables": ("vegetables", "പച്ചക്കറികൾ", "सब्ज़ियाँ", "காய்கறிகள்"),
}


def crop_key(value):
    normalized = value.strip().casefold()
    for key, aliases in CROP_ALIASES.items():
        if normalized in {alias.casefold() for alias in aliases}:
            return key
    return normalized


def assess_suitability(payload):
    if payload.expiry_date and payload.expiry_date < date.today():
        return "not_recommended", "The expiry date you entered has passed. Do not buy or use this product; ask an agricultural officer."

    label_crops = [crop_key(item) for item in payload.label_crops.split(",") if item.strip()]
    if label_crops and crop_key(payload.crop) not in label_crops:
        return "not_recommended", "The crop entered from the label does not include your selected crop. Recheck the package and ask an officer before use."

    if not payload.product_name.strip() or not payload.crop.strip() or payload.land_area <= 0:
        return "insufficient_information", "Add the product name, crop, and land area before an officer can review this check."

    if payload.expiry_date and (payload.expiry_date - date.today()).days <= 90:
        return "needs_verification", "The entered expiry date is within 90 days. Check the printed date and ask an officer before purchase or use."

    return "needs_verification", "Crop and stage suitability cannot be confirmed from the details entered. Check the full product label and get officer guidance before use."
