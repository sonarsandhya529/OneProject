import re
import streamlit as st
from utils import set_language, t, register_farmer, MAHARASHTRA_DISTRICTS

st.set_page_config(page_title="Farmer Registration", page_icon="👨‍🌾")
set_language()
st.title("👨‍🌾 " + t("register"))
with st.form("register_form"):
    full_name = st.text_input(t("name"))
    mobile = st.text_input(t("mobile"), max_chars=15)
    district = st.selectbox(t("district_select"), MAHARASHTRA_DISTRICTS)
    username = st.text_input(t("username"))
    password = st.text_input(t("password"), type="password")
    confirm = st.text_input(t("confirm_password"), type="password")
    submitted = st.form_submit_button(t("create_account"), use_container_width=True)
if submitted:
    if not all([full_name.strip(), mobile.strip(), username.strip(), password, confirm]):
        st.error(t("fill_fields"))
    elif not re.fullmatch(r"[0-9+\-\s]{10,15}", mobile.strip()):
        st.error("Enter a valid mobile number / वैध मोबाईल क्रमांक टाका.")
    elif len(password) < 8:
        st.error("Password must be at least 8 characters / पासवर्ड किमान ८ अक्षरांचा असावा.")
    elif password != confirm:
        st.error(t("password_mismatch"))
    elif register_farmer(full_name, mobile, district, username, password):
        st.success(t("account_created"))
    else:
        st.error(t("account_exists"))
st.page_link("app.py", label="← Home / मुख्यपृष्ठ")
