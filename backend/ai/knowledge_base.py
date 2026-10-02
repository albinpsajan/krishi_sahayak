"""
CropDoctor disease knowledge base and Malayalam translations.

Data-only module. The provider (crop_doctor.py) consults this table; editing
diagnosis content never touches business logic.
"""

MALAYALAM_DICTIONARY = {
    "Paddy Blast (Magnaporthe oryzae)": {
        "name": "നെല്ലിലെ ബ്ലാസ്റ്റ് രോഗം (ഞെട്ടിപ്പഴുപ്പ്)",
        "guidance": "സുഡോമോണസ് ഫ്ലൂറസെൻസ് (10 ഗ്രാം/ലിറ്റർ) തളിക്കുക. നൈട്രജൻ വളങ്ങളുടെ അമിത ഉപയോഗം ഒഴിവാക്കുക. ഞാറ്റടി ഘട്ടത്തിൽ 2.5 ഗ്രാം മാങ്കോസെബ് തളിക്കുന്നത് രോഗം തടയും.",
    },
    "Tomato Early Blight (Alternaria solani)": {
        "name": "തക്കാളി അഗതി രോഗം (ഇലപ്പുള്ളി രോഗം)",
        "guidance": "വേപ്പെണ്ണ മിശ്രിതം (5 മില്ലി/ലിറ്റർ) തളിക്കുക. ബാധിതമായ താഴ്ഭാഗത്തെ ഇലകൾ നീക്കം ചെയ്യുക. തടങ്ങളിൽ വെള്ളം കെട്ടിക്കിടക്കാൻ അനുവദിക്കരുത്.",
    },
    "Yellow Rust (Puccinia striiformis)": {
        "name": "മഞ്ഞ കുങ്കുമ രോഗം (യെല്ലോ റസ്റ്റ്)",
        "guidance": "തൈര് മിശ്രിതമോ കോപ്പർ ഹൈഡ്രോക്സൈഡോ തളിക്കുക. പ്രതിരോധ ശേഷിയുള്ള വിത്തിനങ്ങൾ മാത്രം ഉപയോഗിക്കുക.",
    },
    "Cotton Leaf Curl Virus": {
        "name": "പരുത്തി ഇല ചുരുളൽ രോഗം",
        "guidance": "മഞ്ഞ ഒട്ടുന്ന കെണികൾ വെച്ച് വെള്ളീച്ചകളെ നിയന്ത്രിക്കുക. വേപ്പെണ്ണ 10000 PPM ലായനി തളിക്കുക.",
    },
    "Pepper Quick Wilt (Phytophthora capsici)": {
        "name": "കുരുമുളക് ദ്രുതവാട്ടം (പെപ്പർ വൈൽറ്റ്)",
        "guidance": "1% ബോർഡോ മിശ്രിതം അല്ലെങ്കിൽ ട്രൈക്കോഡെർമ (20 ഗ്രാം/ചുവട്) തടത്തിൽ ഒഴിച്ചുകൊടുക്കുക. നീർവാർച്ച ഉറപ്പാക്കുക.",
    },
    "Healthy Crop": {
        "name": "ആരോഗ്യമുള്ള വിള",
        "guidance": "വിളയിൽ രോഗലക്ഷണങ്ങളൊന്നുമില്ല. കൃത്യമായ നനയും ജീവാണു വളപ്രയോഗവും തുടരുക.",
    },
}

DISEASE_KNOWLEDGE_BASE = {
    "paddy": {
        "probable_disease": "Paddy Blast (Magnaporthe oryzae)",
        "confidence": 88.5,
        "observations": "Spindle-shaped diamond eye-spots detected on leaf surface with dark reddish-brown borders and grey central necrotic zones.",
        "preliminary_guidance": "Spray Pseudomonas fluorescens @ 10g/L water during early morning. Avoid excessive nitrogenous fertilizer applications during humid weather.",
    },
    "tomato": {
        "probable_disease": "Tomato Early Blight (Alternaria solani)",
        "confidence": 91.2,
        "observations": "Concentric dark brown circular rings observed on lower foliar leaves accompanied by yellow chlorotic halos around lesions.",
        "preliminary_guidance": "Prune and dispose affected lower leaves. Apply organic Neem formulation (5ml/L) or Copper Oxychloride 50% WP @ 3g/L.",
    },
    "pepper": {
        "probable_disease": "Pepper Quick Wilt (Phytophthora capsici)",
        "confidence": 86.4,
        "observations": "Water-soaked dark brown lesions at the runner shoot base with leaf drooping and vine wilting symptoms.",
        "preliminary_guidance": "Drench vine base with 1% Bordeaux Mixture or Trichoderma viride enriched organic compost (50g/vine). Improve field drainage immediately.",
    },
    "cotton": {
        "probable_disease": "Cotton Leaf Curl Virus",
        "confidence": 84.0,
        "observations": "Upward thickening and curling of leaves with minor enation on lower leaf veins indicative of Whitefly vector transmission.",
        "preliminary_guidance": "Install Yellow Sticky Traps (12-15 traps/acre) to control Whitefly vectors. Spray 10,000 PPM Neem Oil.",
    },
    "wheat": {
        "probable_disease": "Yellow Rust (Puccinia striiformis)",
        "confidence": 89.0,
        "observations": "Bright yellow powdery linear stripes formed along leaf veins containing active urediniospores.",
        "preliminary_guidance": "Foliar spray of Propiconazole 25% EC @ 1ml/L water. Monitor surrounding fields within 5km radius.",
    },
}
