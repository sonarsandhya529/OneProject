import os
import pandas as pd
from streamlit_geolocation import streamlit_geolocation
from geopy.geocoders import Nominatim
import streamlit as st
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from utils import set_language, t, SOIL_CROPS

st.set_page_config(page_title="Crop Dashboard", page_icon="🌱", layout="wide")
set_language()
if "farmer" not in st.session_state:
    st.warning(t("need_login"))
    if st.button(t("login")):
        st.switch_page("pages/2_Login.py")
    st.stop()

farmer = st.session_state["farmer"]
top1, top2 = st.columns([4,1])
with top1:
    st.title("🌱 " + t("dashboard"))
    st.write(t("welcome") + ", " + farmer["full_name"])
    district_label = "District" if st.session_state.get("language") == "English" else "जिल्हा"
    st.write(f"📍 **{district_label}: {farmer.get('district', '—')}**")
with top2:
    if st.button(t("logout"), use_container_width=True):
        st.session_state.pop("farmer", None)
        st.switch_page("app.py")

st.subheader(t("gps_title"))
st.write(t("gps_help"))
try:
    location = streamlit_geolocation()
except Exception:
    location = None

if location and location.get("latitude") is not None and location.get("longitude") is not None:
    lat = float(location["latitude"])
    lon = float(location["longitude"])
    st.success(f"{t('gps_success')}: {lat:.5f}, {lon:.5f}")
    st.session_state["gps_coordinates"] = (lat, lon)
    if st.button(t("gps_find_district"), key="gps_reverse_geocode"):
        with st.spinner(t("gps_finding_district")):
            try:
                geocoder = Nominatim(user_agent="crop_recommendation_system", timeout=8)
                result = geocoder.reverse((lat, lon), exactly_one=True, language="en", addressdetails=True)
                address = result.raw.get("address", {}) if result else {}
                district = (address.get("state_district") or address.get("county") or
                            address.get("city_district") or address.get("city") or address.get("town"))
                state = address.get("state", "")
                if district:
                    district = district.replace(" District", "").strip()
                    st.session_state["gps_district"] = district
                    st.session_state["gps_state"] = state
                    st.success(f"{t('gps_district_found')}: **{district}**" + (f", {state}" if state else ""))
                else:
                    st.warning(t("gps_district_not_found"))
            except Exception:
                st.warning(t("gps_geocode_error"))
    detected = st.session_state.get("gps_district")
    if detected:
        st.info(f"{t('gps_active_district')}: **{detected}**. {t('gps_district_note')}")
else:
    st.info(t("gps_not_detected"))
st.caption(t("gps_permission_note"))

st.subheader(t("soil_section"))
soil_labels = {
    "black": t("black"), "red": t("red"), "alluvial": t("alluvial"),
    "sandy": t("sandy"), "clay": t("clay")
}
with st.form("crop_form"):
    col1, col2 = st.columns(2)
    with col1:
        soil_key = st.selectbox(t("soil_type"), list(soil_labels.keys()), format_func=lambda x: soil_labels[x])
        water = st.selectbox(t("water"), ["low", "medium", "high"],
                             format_func=lambda x: t(x))
        season = st.selectbox(t("season"), ["kharif", "rabi", "summer"],
                              format_func=lambda x: t(x))
        n = st.number_input(t("n"), min_value=0.0, max_value=2000.0, value=50.0)
        p = st.number_input(t("p"), min_value=0.0, max_value=2000.0, value=40.0)
        k = st.number_input(t("k"), min_value=0.0, max_value=2000.0, value=40.0)
    with col2:
        temperature = st.number_input(t("temperature"), min_value=-10.0, max_value=70.0, value=25.0)
        humidity = st.number_input(t("humidity"), min_value=0.0, max_value=100.0, value=60.0)
        ph = st.number_input(t("ph"), min_value=0.0, max_value=14.0, value=6.5)
        rainfall = st.number_input(t("rainfall"), min_value=0.0, max_value=5000.0, value=100.0)
    st.caption(t("inputs_help"))
    submitted = st.form_submit_button(t("recommend"), use_container_width=True)

st.subheader(t("soil_crop_title"))
soil_info = SOIL_CROPS[soil_key]
crop_list = soil_info["mr"] if st.session_state.get("language") == "मराठी" else soil_info["crops"]
st.write(", ".join(crop_list))
st.info(t(soil_info["reason"]))
st.caption(t("soil_note"))

# Regional examples are shown only when the GPS reverse-geocoding step identifies a district.
regional_crops = {
    "Pune": ["Sugarcane (irrigated areas)", "Jowar", "Bajra", "Soybean", "Pulses"],
    "Nashik": ["Grapes (suitable sites)", "Onion", "Maize", "Soybean", "Pulses"],
    "Solapur": ["Jowar", "Pomegranate (suitable sites)", "Bajra", "Pulses"],
    "Kolhapur": ["Sugarcane", "Rice", "Soybean", "Groundnut"],
    "Nagpur": ["Orange (suitable sites)", "Cotton", "Soybean", "Pigeon pea"],
    "Amravati": ["Cotton", "Soybean", "Pigeon pea", "Turmeric (suitable sites)"],
    "Yavatmal": ["Cotton", "Soybean", "Pigeon pea", "Sorghum"],
    "Jalgaon": ["Banana (irrigated areas)", "Cotton", "Maize", "Pulses"],
    "Satara": ["Sugarcane (irrigated areas)", "Jowar", "Soybean", "Groundnut"],
    "Sangli": ["Sugarcane (irrigated areas)", "Grapes (suitable sites)", "Jowar", "Turmeric"],
    "Ahmednagar": ["Jowar", "Bajra", "Sugarcane (irrigated areas)", "Pulses"],
    "Ahilyanagar": ["Jowar", "Bajra", "Sugarcane (irrigated areas)", "Pulses"],
    "Chhatrapati Sambhajinagar": ["Cotton", "Maize", "Soybean", "Pigeon pea"],
    "Nanded": ["Cotton", "Soybean", "Tur", "Sorghum"],
    "Latur": ["Soybean", "Pigeon pea", "Sorghum", "Chickpea"],
    "Beed": ["Sorghum", "Bajra", "Pigeon pea", "Chickpea"],
    "Akola": ["Cotton", "Soybean", "Pigeon pea", "Green gram"],
    "Buldhana": ["Cotton", "Soybean", "Pigeon pea", "Sorghum"],
    "Wardha": ["Cotton", "Soybean", "Pigeon pea", "Sorghum"],
    "Washim": ["Cotton", "Soybean", "Pigeon pea", "Chickpea"],
    "Dhule": ["Cotton", "Bajra", "Jowar", "Pulses"],
    "Nandurbar": ["Maize", "Cotton", "Pulses", "Millets"],
    "Jalna": ["Cotton", "Soybean", "Maize", "Pigeon pea"],
    "Parbhani": ["Soybean", "Cotton", "Pigeon pea", "Chickpea"],
    "Hingoli": ["Soybean", "Cotton", "Pigeon pea", "Sorghum"],
    "Ratnagiri": ["Rice", "Coconut", "Cashew", "Mango"],
    "Sindhudurg": ["Rice", "Coconut", "Cashew", "Mango"],
    "Raigad": ["Rice", "Coconut", "Cashew", "Vegetables"],
    "Thane": ["Rice", "Vegetables", "Pulses"],
    "Palghar": ["Rice", "Nagli (finger millet)", "Vegetables", "Pulses"],
    "Mumbai City": ["Urban/peri-urban vegetables (where feasible)"],
    "Mumbai Suburban": ["Urban/peri-urban vegetables (where feasible)"],
    "Bhandara": ["Rice", "Pulses", "Vegetables"],
    "Gondia": ["Rice", "Pulses", "Vegetables"],
    "Chandrapur": ["Cotton", "Rice", "Soybean", "Pigeon pea"],
    "Gadchiroli": ["Rice", "Millets", "Pulses"],
    "Nagpur Rural": ["Orange (suitable sites)", "Cotton", "Soybean", "Pigeon pea"],
    "Dharashiv": ["Sorghum", "Soybean", "Pigeon pea", "Chickpea"],
}

detected_district = st.session_state.get("gps_district")
if detected_district:
    district_key = next((key for key in regional_crops if key.casefold() == detected_district.casefold()), detected_district)
    regional_list = regional_crops.get(district_key)
    st.subheader(t("regional_crop_title"))
    if regional_list:
        regional_display = regional_list if st.session_state.get("language") == "English" else {
            "Sugarcane": "ऊस", "Rice": "भात", "Cotton": "कापूस", "Soybean": "सोयाबीन", "Jowar": "ज्वारी",
            "Bajra": "बाजरी", "Pulses": "कडधान्ये", "Pigeon pea": "तूर", "Chickpea": "हरभरा",
            "Maize": "मका", "Groundnut": "भुईमूग", "Orange": "संत्रा", "Onion": "कांदा", "Grapes": "द्राक्षे",
            "Pomegranate": "डाळिंब", "Banana": "केळी", "Turmeric": "हळद", "Green gram": "मूग",
            "Mango": "आंबा", "Cashew": "काजू", "Coconut": "नारळ", "Vegetables": "भाजीपाला",
            "Millets": "भरडधान्ये", "Nagli (finger millet)": "नाचणी", "Urban/peri-urban vegetables (where feasible)": "शक्य असल्यास शहरी/उपनगरी भाजीपाला",
        }
        if isinstance(regional_display, dict):
            regional_display = [next((mr for en, mr in regional_display.items() if crop.startswith(en)), crop) for crop in regional_list]
        st.write(", ".join(regional_display))
    else:
        st.info(t("regional_crop_unknown"))
    st.caption(t("regional_crop_note"))

if submitted:
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Crop_recommendation.csv")
    if not os.path.exists(dataset_path):
        st.error(t("dataset_missing"))
    else:
        try:
            data = pd.read_csv(dataset_path)
            required = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall", "label"]
            if not set(required).issubset(data.columns):
                st.error(t("dataset_bad"))
            else:
                X = data[required[:-1]]
                y = data["label"]
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42, stratify=y
                )
                model = RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")
                model.fit(X_train, y_train)
                acc = accuracy_score(y_test, model.predict(X_test))
                row = pd.DataFrame([[n,p,k,temperature,humidity,ph,rainfall]], columns=required[:-1])
                prediction = model.predict(row)[0]
                probs = model.predict_proba(row)[0]
                top_indices = probs.argsort()[::-1]
                labels = model.classes_
                alternatives = [str(labels[i]) for i in top_indices if str(labels[i]) != str(prediction)][:3]
                st.success("🌾 " + t("predicted") + ": **" + str(prediction.replace("_", " ").title()) + "**")
                st.metric("Validation accuracy / मॉडेलची चाचणी अचूकता", f"{acc:.1%}")
                st.write("**" + t("alternatives") + ":** " + (", ".join(alternatives) if alternatives else "—"))
                st.caption(t("caveat"))
        except Exception as e:
            st.error(f"Could not process dataset: {e}")
