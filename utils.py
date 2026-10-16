import hashlib
import hmac
import os
import sqlite3
import streamlit as st

DB_PATH = os.environ.get("FARMER_DB_PATH", "farmers.db")

TRANSLATIONS = {
    "English": {
        "app_title": "Crop Recommendation System",
        "home_intro": "Get crop suggestions using soil properties, weather conditions, and soil type.",
        "home_note": "This tool provides educational recommendations. For field decisions, consider a soil test and local agricultural advice.",
        "register": "Farmer Registration", "login": "Farmer Login", "dashboard": "Dashboard",
        "register_desc": "Create a farmer account to use the recommendation dashboard.",
        "login_desc": "Sign in to view crop recommendations.",
        "features_title": "What this project includes",
        "features": ["English and Marathi interface", "Farmer registration and login", "Soil-type-based crop guidance",
                     "ML recommendation using N, P, K, temperature, humidity, pH, and rainfall",
                     "Alternative crops and practical suitability notes"],
         "gps_title": "GPS-based location (optional)",
        "gps_help": "Allow location access in your browser to detect your approximate coordinates. GPS may be unavailable on desktop or if permission is denied.",
        "gps_button": "Use my current location",
        "gps_success": "Location detected",
        "gps_find_district": "Identify district from GPS",
        "gps_finding_district": "Looking up the district from your coordinates…",
        "gps_district_found": "Detected district",
        "gps_district_not_found": "Could not identify a district from these coordinates. Please choose/check your district manually.",
        "gps_geocode_error": "District lookup failed. Check your internet connection or choose the district manually.",
        "gps_active_district": "GPS-based district",
        "gps_district_note": "This is an approximate reverse-geocoded result; verify it before using it for farm decisions.",
        "gps_not_detected": "Location has not been detected yet. Click the location control and allow browser permission.",
        "regional_crop_title": "Common crop examples for the detected district",
        "regional_crop_unknown": "No district-specific crop list is available in this demo. Use soil and ML guidance plus local agricultural advice.",
        "regional_crop_note": "These are broad regional examples, not a field-level recommendation. Confirm soil, irrigation, season, variety, and local advice before sowing.",
        "gps_error": "Could not access location. Allow location permission in your browser, or select your district manually.",
        "gps_permission_note": "Coordinates are used to help identify your location. The app does not independently verify your district from GPS.",
        "choose_language": "Language", "name": "Full name", "mobile": "Mobile number", "district_select": "District",
        "username": "Username", "password": "Password", "confirm_password": "Confirm password",
        "create_account": "Create account", "account_created": "Registration successful. Please log in.",
        "account_exists": "That username already exists.", "fill_fields": "Please fill in all fields.",
        "password_mismatch": "Passwords do not match.", "login_button": "Log in",
        "bad_login": "Incorrect username or password.", "welcome": "Welcome",
        "logout": "Log out", "soil_section": "Soil and growing conditions",
        "soil_type": "Soil type", "black": "Black soil", "red": "Red soil",
        "alluvial": "Alluvial soil", "sandy": "Sandy soil", "clay": "Clay soil",
        "water": "Water availability", "low": "Low", "medium": "Medium", "high": "High",
        "season": "Growing season", "kharif": "Kharif / Monsoon", "rabi": "Rabi / Winter", "summer": "Summer",
        "district": "District / region (optional)", "n": "Nitrogen (N)", "p": "Phosphorus (P)",
        "k": "Potassium (K)", "temperature": "Temperature (°C)", "humidity": "Humidity (%)",
        "ph": "Soil pH", "rainfall": "Rainfall (mm)", "recommend": "Recommend crop",
        "soil_crop_title": "Crops commonly considered for this soil type",
        "ml_title": "Machine-learning recommendation", "predicted": "Model's suggested crop",
        "alternatives": "Other crops to consider", "why": "Why these may fit",
        "caveat": "General guidance only: crop suitability also depends on variety, local climate, sowing date, drainage, pests, market access, and soil-test results.",
        "dataset_missing": "The dataset file Crop_recommendation.csv was not found. Put it in the project root folder next to app.py.",
        "dataset_bad": "The dataset must contain columns: N, P, K, temperature, humidity, ph, rainfall, label.",
        "need_login": "Please log in to access the dashboard.",
        "soil_note": "Soil-type suggestions are general examples, not a guarantee. Confirm locally before planting.",
        "inputs_help": "Enter values from a soil test or reliable local measurements. The model needs all seven values.",
        "soil_reason_black": "Black soils often retain moisture and may suit crops such as cotton, soybean, sorghum, and pigeon pea, depending on drainage and rainfall.",
        "soil_reason_red": "Red soils vary widely and often need attention to fertility and moisture; groundnut, millets, and pulses may suit some locations.",
        "soil_reason_alluvial": "Alluvial soils can support several crops, including wheat, maize, rice, or sugarcane where water and climate fit.",
        "soil_reason_sandy": "Sandy soils drain quickly; millets, groundnut, and some pulses may be options where moisture is managed.",
        "soil_reason_clay": "Clay soils can hold water; rice may suit some settings, but drainage and waterlogging risk matter.",
        "lang_saved": "Language preference applies throughout the app."
    },
    "मराठी": {
        "app_title": "पीक शिफारस प्रणाली",
        "home_intro": "मातीचे गुणधर्म, हवामान आणि मातीचा प्रकार यांनुसार पिकांची शिफारस मिळवा.",
        "home_note": "हे साधारण मार्गदर्शन आहे. प्रत्यक्ष पेरणीपूर्वी माती परीक्षण आणि स्थानिक कृषी तज्ज्ञांचा सल्ला घ्या.",
        "register": "शेतकरी नोंदणी", "login": "शेतकरी लॉगिन", "dashboard": "डॅशबोर्ड",
        "register_desc": "पीक शिफारस वापरण्यासाठी शेतकरी खाते तयार करा.",
        "login_desc": "पीक शिफारसी पाहण्यासाठी लॉगिन करा.",
        "features_title": "या प्रोजेक्टमधील सुविधा",
        "features": ["मराठी आणि इंग्रजी भाषा", "शेतकरी नोंदणी आणि लॉगिन", "मातीच्या प्रकारानुसार पिकांचे मार्गदर्शन",
                     "N, P, K, तापमान, आर्द्रता, pH आणि पावसावर आधारित ML शिफारस",
                     "पर्यायी पिके आणि उपयोगी सूचना"],
         "gps_title": "GPS द्वारे स्थान (ऐच्छिक)",
        "gps_help": "अंदाजे स्थान मिळवण्यासाठी ब्राउझरमध्ये location permission द्या. डेस्कटॉपवर GPS उपलब्ध नसेल किंवा परवानगी नाकारली असल्यास हे काम करणार नाही.",
        "gps_button": "माझे सध्याचे स्थान वापरा",
        "gps_success": "स्थान मिळाले",
        "gps_find_district": "GPS वरून जिल्हा ओळखा",
        "gps_finding_district": "GPS coordinates वरून जिल्हा शोधत आहोत…",
        "gps_district_found": "ओळखलेला जिल्हा",
        "gps_district_not_found": "या coordinates वरून जिल्हा ओळखता आला नाही. कृपया जिल्हा स्वतः निवडा/तपासा.",
        "gps_geocode_error": "जिल्हा शोधता आला नाही. इंटरनेट तपासा किंवा जिल्हा स्वतः निवडा.",
        "gps_active_district": "GPS वरून ओळखलेला जिल्हा",
        "gps_district_note": "हा अंदाजे नकाशा-आधारित निकाल आहे; शेतीच्या निर्णयापूर्वी जिल्हा तपासा.",
        "gps_not_detected": "अजून स्थान मिळालेले नाही. Location control वापरा आणि ब्राउझरची परवानगी द्या.",
        "regional_crop_title": "ओळखलेल्या जिल्ह्यातील सामान्य पिकांची उदाहरणे",
        "regional_crop_unknown": "या डेमोमध्ये या जिल्ह्यासाठी स्वतंत्र पिकांची यादी नाही. माती व ML मार्गदर्शनासोबत स्थानिक कृषी सल्ला घ्या.",
        "regional_crop_note": "ही परिसरातील सामान्य पिकांची उदाहरणे आहेत; शेतासाठी खात्रीशीर शिफारस नाही. पेरणीपूर्वी माती, सिंचन, हंगाम, वाण आणि स्थानिक सल्ला तपासा.",
        "gps_error": "स्थान मिळाले नाही. ब्राउझरमध्ये location permission द्या किंवा जिल्हा स्वतः निवडा.",
        "gps_permission_note": "GPS मधील coordinates स्थान समजण्यास मदत करतात; अॅप GPS वरून जिल्ह्याची स्वतंत्र खात्री करत नाही.",
        "choose_language": "भाषा", "name": "पूर्ण नाव", "mobile": "मोबाईल क्रमांक", "district_select": "जिल्हा",
        "username": "वापरकर्ता नाव", "password": "पासवर्ड", "confirm_password": "पासवर्ड पुन्हा टाका",
        "create_account": "खाते तयार करा", "account_created": "नोंदणी यशस्वी. आता लॉगिन करा.",
        "account_exists": "हे वापरकर्ता नाव आधीच वापरले आहे.", "fill_fields": "कृपया सर्व माहिती भरा.",
        "password_mismatch": "दोन्ही पासवर्ड जुळत नाहीत.", "login_button": "लॉगिन",
        "bad_login": "वापरकर्ता नाव किंवा पासवर्ड चुकीचा आहे.", "welcome": "स्वागत",
        "logout": "लॉगआउट", "soil_section": "माती आणि लागवडीची परिस्थिती",
        "soil_type": "मातीचा प्रकार", "black": "काळी माती", "red": "लाल माती",
        "alluvial": "गाळाची माती", "sandy": "वाळूमिश्रित माती", "clay": "चिकणमाती",
        "water": "पाण्याची उपलब्धता", "low": "कमी", "medium": "मध्यम", "high": "भरपूर",
        "season": "हंगाम", "kharif": "खरीप / पावसाळा", "rabi": "रब्बी / हिवाळा", "summer": "उन्हाळी",
        "district": "जिल्हा / परिसर (ऐच्छिक)", "n": "नायट्रोजन (N)", "p": "फॉस्फरस (P)",
        "k": "पोटॅशियम (K)", "temperature": "तापमान (°C)", "humidity": "आर्द्रता (%)",
        "ph": "मातीचा pH", "rainfall": "पाऊस (mm)", "recommend": "पीक सुचवा",
        "soil_crop_title": "या मातीच्या प्रकारात विचारात घेता येणारी पिके",
        "ml_title": "मशीन लर्निंग पीक शिफारस", "predicted": "मॉडेलनुसार सुचवलेले पीक",
        "alternatives": "इतर विचारात घेण्यासारखी पिके", "why": "ही पिके का विचारात घ्यावीत",
        "caveat": "हे सर्वसाधारण मार्गदर्शन आहे. वाण, स्थानिक हवामान, पेरणीची वेळ, निचरा, कीड, बाजारपेठ आणि माती परीक्षण यांचाही विचार करा.",
        "dataset_missing": "Crop_recommendation.csv फाइल सापडली नाही. ती app.py च्या शेजारी मुख्य फोल्डरमध्ये ठेवा.",
        "dataset_bad": "डेटासेटमध्ये N, P, K, temperature, humidity, ph, rainfall, label हे कॉलम असणे आवश्यक आहे.",
        "need_login": "डॅशबोर्ड वापरण्यासाठी कृपया लॉगिन करा.",
        "soil_note": "मातीच्या प्रकारानुसार दिलेली पिके ही सामान्य उदाहरणे आहेत; पेरणीपूर्वी स्थानिक सल्ला घ्या.",
        "inputs_help": "माती परीक्षण किंवा विश्वासार्ह स्थानिक मोजमापांनुसार माहिती भरा. मॉडेलसाठी सातही मूल्ये आवश्यक आहेत.",
        "soil_reason_black": "काळी माती ओलावा धरून ठेवू शकते. निचरा आणि पावसानुसार कापूस, सोयाबीन, ज्वारी आणि तूर योग्य ठरू शकतात.",
        "soil_reason_red": "लाल मातीची सुपीकता व ओलावा वेगवेगळा असतो. काही भागांत भुईमूग, भरडधान्ये आणि कडधान्ये योग्य ठरू शकतात.",
        "soil_reason_alluvial": "गाळाच्या मातीत पाणी व हवामान योग्य असल्यास गहू, मका, भात किंवा ऊस घेता येऊ शकतो.",
        "soil_reason_sandy": "वाळूमिश्रित मातीचा निचरा जलद होतो. ओलावा व्यवस्थापन केल्यास बाजरी, भुईमूग आणि काही कडधान्ये पर्याय असू शकतात.",
        "soil_reason_clay": "चिकणमाती पाणी धरून ठेवू शकते. काही ठिकाणी भात योग्य असतो; निचरा आणि पाणी साचण्याचा धोका तपासावा.",
        "lang_saved": "भाषेची निवड संपूर्ण अॅपमध्ये लागू राहील."
    }
}

def set_language():
    if "language" not in st.session_state:
        st.session_state.language = "मराठी"
    chosen = st.sidebar.selectbox("Language / भाषा", ["मराठी", "English"],
                                  index=["मराठी", "English"].index(st.session_state.language))
    st.session_state.language = chosen
    st.sidebar.caption(TRANSLATIONS[chosen]["lang_saved"])

def t(key):
    lang = st.session_state.get("language", "मराठी")
    return TRANSLATIONS[lang].get(key, key)

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS farmers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        mobile TEXT NOT NULL,
        district TEXT NOT NULL DEFAULT '',
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL
    )""")
    # Migrate databases created by earlier versions.
    columns = [row[1] for row in conn.execute("PRAGMA table_info(farmers)").fetchall()]
    if "district" not in columns:
        conn.execute("ALTER TABLE farmers ADD COLUMN district TEXT NOT NULL DEFAULT ''")
    conn.commit()
    return conn

def _hash_password(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()

MAHARASHTRA_DISTRICTS = ['Ahilyanagar', 'Akola', 'Amravati', 'Beed', 'Bhandara', 'Buldhana', 'Chandrapur', 'Chhatrapati Sambhajinagar', 'Dharashiv', 'Dhule', 'Gadchiroli', 'Gondia', 'Hingoli', 'Jalgaon', 'Jalna', 'Kolhapur', 'Latur', 'Mumbai City', 'Mumbai Suburban', 'Nagpur', 'Nanded', 'Nandurbar', 'Nashik', 'Palghar', 'Parbhani', 'Pune', 'Raigad', 'Ratnagiri', 'Sangli', 'Satara', 'Sindhudurg', 'Solapur', 'Thane', 'Wardha', 'Washim', 'Yavatmal']

def register_farmer(full_name, mobile, district, username, password):
    salt = os.urandom(16).hex()
    digest = _hash_password(password, salt)
    try:
        conn = get_db()
        conn.execute("INSERT INTO farmers(full_name,mobile,district,username,password_hash,salt) VALUES(?,?,?,?,?,?)",
                     (full_name.strip(), mobile.strip(), district.strip(), username.strip(), digest, salt))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate(username, password):
    conn = get_db()
    row = conn.execute("SELECT full_name, username, district, password_hash, salt FROM farmers WHERE username=?",
                       (username.strip(),)).fetchone()
    conn.close()
    if not row:
        return None
    full_name, uname, district, stored, salt = row
    if hmac.compare_digest(_hash_password(password, salt), stored):
        return {"full_name": full_name, "username": uname, "district": district}
    return None

SOIL_CROPS = {
    "black": {
        "crops": ["Cotton", "Soybean", "Sorghum", "Pigeon pea", "Chickpea (season-dependent)"],
        "mr": ["कापूस", "सोयाबीन", "ज्वारी", "तूर", "हरभरा (हंगामानुसार)"],
        "reason": "soil_reason_black"
    },
    "red": {
        "crops": ["Groundnut", "Pearl millet", "Pigeon pea", "Other pulses"],
        "mr": ["भुईमूग", "बाजरी", "तूर", "इतर कडधान्ये"],
        "reason": "soil_reason_red"
    },
    "alluvial": {
        "crops": ["Wheat", "Maize", "Rice", "Sugarcane (where irrigation fits)"],
        "mr": ["गहू", "मका", "भात", "ऊस (सिंचन योग्य असल्यास)"],
        "reason": "soil_reason_alluvial"
    },
    "sandy": {
        "crops": ["Pearl millet", "Groundnut", "Selected pulses"],
        "mr": ["बाजरी", "भुईमूग", "योग्य कडधान्ये"],
        "reason": "soil_reason_sandy"
    },
    "clay": {
        "crops": ["Rice (where water and drainage fit)", "Selected crops suited to local drainage"],
        "mr": ["भात (पाणी व निचरा योग्य असल्यास)", "स्थानिक निचऱ्याला अनुरूप पिके"],
        "reason": "soil_reason_clay"
    }
}
